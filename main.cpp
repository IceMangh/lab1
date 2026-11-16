#include "BinarySearchTree.h"
#include <charconv>
#include <cmath>
#include <type_traits>
#include "BinaryHeap.h"
#include "PriorityQueue.h"
#include <iostream>
#include <random>
#include <sstream>
#include <string>

template<typename T>
T Value(const std::string& text) {
    if constexpr (std::is_same_v<T, std::string>) return text;
    else if constexpr (std::is_same_v<T, int>) {
        int value;
        auto result = std::from_chars(text.data(), text.data() + text.size(), value);
        if (result.ec != std::errc() || result.ptr != text.data() + text.size())
            throw std::invalid_argument("Ожидается целое число в диапазоне int");
        return value;
    } else {
        std::size_t end = 0;
        double value;
        try { value = std::stod(text, &end); }
        catch (const std::exception&) { throw std::invalid_argument("Ожидается число double, например 2.5"); }
        if (end != text.size() || !std::isfinite(value)) throw std::invalid_argument("Ожидается конечное число double");
        return value;
    }
}

// Console UI required by the assignment; the graphical UI uses the same classes.
template<typename T>
void RunConsole(const std::string& structure) {
    BinarySearchTree<T> tree;
    BinaryHeap<T> heap(structure == "minheap");
    PriorityQueue<T> queue;
    std::cout << "\n" << structure << "\n";
    if (structure == "tree")
        std::cout << "insert VALUE, contains VALUE, remove VALUE, top, pop, show, height, threads, reverse\n";
    else if (structure == "queue")
        std::cout << "push PRIORITY VALUE, top, pop, empty, show (первый элемент)\n";
    else std::cout << "push VALUE, top, pop, empty, show\n";
    std::cout << "random COUNT SEED, clear, back, quit. Строки вводятся без кавычек.\n";
    std::string line;
    while (std::cout << "> " && std::getline(std::cin, line)) {
        std::istringstream input(line);
        std::string op, value;
        input >> op;
        if (op.empty()) continue;
        std::getline(input, value);
        if (!value.empty() && value.front() == ' ') value.erase(0, 1);
        if (op == "back") return;
        if (op == "quit") { std::cin.setstate(std::ios::eofbit); return; }
        try {
            if (op == "clear") { tree = BinarySearchTree<T>{}; heap = BinaryHeap<T>(structure == "minheap"); queue = PriorityQueue<T>{}; std::cout << "Очищено\n"; }
            else if (op == "random") {
                std::istringstream args(value);
                int count; unsigned seed; std::string trailing;
                if (!(args >> count >> seed) || count < 0 || count > 1000000 || args >> trailing)
                    throw std::invalid_argument("random: количество от 0 до 1000000 и seed");
                std::mt19937 random(seed);
                for (int i = 0; i < count; ++i) {
                    T generated;
                    if constexpr (std::is_same_v<T, std::string>) generated = "value-" + std::to_string(random() % 1000000);
                    else generated = static_cast<T>(random() % 1000000);
                    if (structure == "tree") tree.Insert(generated);
                    else if (structure == "queue") queue.Push(generated, static_cast<int>(random() % 1000));
                    else heap.Push(generated);
                }
                std::cout << "Сгенерировано: " << count << ". Повторные значения дерева объединяются.\n";
            } else if (structure == "tree") {
                if (op == "insert") std::cout << (tree.Insert(Value<T>(value)) ? "true" : "false") << '\n';
                else if (op == "contains") std::cout << (tree.Contains(Value<T>(value)) ? "true" : "false") << '\n';
                else if (op == "remove") std::cout << (tree.Remove(Value<T>(value)) ? "true" : "false") << '\n';
                else if (op == "top") std::cout << tree.GetMax() << '\n';
                else if (op == "pop") std::cout << tree.ExtractMax() << '\n';
                else if (op == "show") { tree.LKP(); std::cout << "\nВысота: " << tree.GetHeight() << '\n'; }
                else if (op == "height") std::cout << tree.GetHeight() << '\n';
                else if (op == "threads") { tree.LKPThreads(); std::cout << '\n'; }
                else if (op == "reverse") { tree.PKLThreads(); std::cout << '\n'; }
                else throw std::invalid_argument("Неизвестная операция дерева");
            } else if (structure == "queue") {
                if (op == "push") {
                    std::istringstream args(value); long long priority; std::string element;
                    if (!(args >> priority)) throw std::invalid_argument("push: целый приоритет и значение");
                    std::getline(args, element); if (!element.empty() && element.front() == ' ') element.erase(0, 1);
                    queue.Push(Value<T>(element), priority); std::cout << "Добавлено\n";
                } else if (op == "top") std::cout << queue.Top() << '\n';
                else if (op == "pop") std::cout << queue.Pop() << '\n';
                else if (op == "show") { if (queue.IsEmpty()) std::cout << "Очередь пуста\n"; else std::cout << "Первый: " << queue.Top() << '\n'; }
                else if (op == "empty") std::cout << (queue.IsEmpty() ? "true" : "false") << '\n';
                else throw std::invalid_argument("Операции очереди: push, top, pop, show, clear, random");
            } else {
                if (op == "push" || op == "insert") { heap.Push(Value<T>(value)); std::cout << "Добавлено\n"; }
                else if (op == "top") std::cout << heap.Top() << '\n';
                else if (op == "pop") std::cout << heap.Pop() << '\n';
                else if (op == "empty") std::cout << (heap.IsEmpty() ? "true" : "false") << '\n';
                else if (op == "show") { auto copy = heap; while (!copy.IsEmpty()) std::cout << copy.Pop() << ' '; std::cout << '\n'; }
                else throw std::invalid_argument("Операции кучи: push, top, pop, show, clear, random");
            }
        } catch (const std::exception& error) { std::cout << "Ошибка: " << error.what() << '\n'; }
    }
}

int main() {
    std::cout << "ЛР-1 · Деревья и структуры данных\n"
        "Выберите структуру и тип: tree|minheap|maxheap|queue int|double|string\n"
        "Например: tree int. Для завершения: quit.\n";
    std::string line;
    while (std::cout << "lab1> " && std::getline(std::cin, line)) {
        if (line == "quit") break;
        std::istringstream input(line); std::string structure, type, trailing;
        input >> structure >> type;
        if ((structure != "tree" && structure != "minheap" && structure != "maxheap" && structure != "queue") || input >> trailing) {
            std::cout << "Структура: tree, minheap, maxheap или queue. Затем тип данных.\n"; continue;
        }
        if (type == "int") RunConsole<int>(structure);
        else if (type == "double") RunConsole<double>(structure);
        else if (type == "string") RunConsole<std::string>(structure);
        else std::cout << "Тип данных: int, double или string.\n";
    }
}
