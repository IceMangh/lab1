cmake_minimum_required(VERSION 3.20)
project(lab1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(lab1 main.cpp)
add_executable(lab1_web_backend gui/WebBackend.cpp)
add_executable(data_structure_tests tests/data_structure_tests.cpp)
add_executable(structure_benchmarks benchmarks/structure_benchmarks.cpp)
foreach(target lab1 lab1_web_backend data_structure_tests structure_benchmarks)
    target_include_directories(${target} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /utf-8)
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endif()
endforeach()

option(LAB1_SANITIZERS "Run C++ tests with AddressSanitizer and UndefinedBehaviorSanitizer" ON)
foreach(target data_structure_tests)
    if(MSVC)
        target_compile_options(${target} PRIVATE /UNDEBUG)
    else()
        target_compile_options(${target} PRIVATE -UNDEBUG)
        if(LAB1_SANITIZERS)
            target_compile_options(${target} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all)
            target_link_options(${target} PRIVATE -fsanitize=address,undefined)
        endif()
    endif()
endforeach()

if(APPLE)
    enable_language(OBJCXX)
    set(CMAKE_OBJCXX_STANDARD 20)
    set(CMAKE_OBJCXX_STANDARD_REQUIRED ON)
    add_executable(lab1_gui MACOSX_BUNDLE gui/StructuresApp.mm)
    target_include_directories(lab1_gui PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(lab1_gui PRIVATE -fobjc-arc)
    target_link_libraries(lab1_gui PRIVATE "-framework Cocoa" "-framework WebKit")
    set_target_properties(lab1_gui PROPERTIES
        MACOSX_BUNDLE_BUNDLE_NAME "Структуры данных"
        MACOSX_BUNDLE_GUI_IDENTIFIER "ru.lab1.structures"
        MACOSX_BUNDLE_SHORT_VERSION_STRING "1.0"
        MACOSX_BUNDLE_BUNDLE_VERSION "1")
    add_custom_command(TARGET lab1_gui POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_SOURCE_DIR}/web
            $<TARGET_BUNDLE_CONTENT_DIR:lab1_gui>/Resources/web)
    file(GLOB WEB_RESOURCES CONFIGURE_DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/web/*)
    set_property(TARGET lab1_gui APPEND PROPERTY LINK_DEPENDS ${WEB_RESOURCES})
endif()

find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_FOUND)
    add_custom_target(lab1_web
        COMMAND ${Python3_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/server.py
            --backend $<TARGET_FILE:lab1_web_backend>
        DEPENDS lab1_web_backend WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} USES_TERMINAL)
endif()

enable_testing()
add_test(NAME data_structures COMMAND data_structure_tests)
if(Python3_FOUND)
    add_test(NAME web_backend COMMAND ${Python3_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/tests/web_tests.py $<TARGET_FILE:lab1_web_backend>)
    add_test(NAME console_interface COMMAND ${Python3_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/tests/console_tests.py $<TARGET_FILE:lab1>)
endif()
set_tests_properties(data_structures PROPERTIES TIMEOUT 90)
add_custom_target(check COMMAND ${CMAKE_CTEST_COMMAND} --output-on-failure
    DEPENDS data_structure_tests lab1_web_backend lab1 USES_TERMINAL)

if(APPLE)
    add_executable(native_tests tests/native_tests.mm)
    target_include_directories(native_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
    target_compile_options(native_tests PRIVATE -fobjc-arc -UNDEBUG)
    target_link_libraries(native_tests PRIVATE "-framework Foundation")
    add_test(NAME native_interface_backend COMMAND native_tests)
    add_dependencies(check native_tests)
endif()
