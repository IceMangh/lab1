#import <Cocoa/Cocoa.h>
#import <WebKit/WebKit.h>
#include "StructureLab.h"

@interface StructuresApp : NSObject <NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate>
@property(nonatomic, strong) NSWindow* window;
@property(nonatomic, strong) WKWebView* webView;
@property(nonatomic, assign) BOOL busy;
@end

@implementation StructuresApp
- (void)applicationDidFinishLaunching:(NSNotification*)notification {
    NSMenu* menu = [[NSMenu alloc] init];
    NSMenuItem* appItem = [[NSMenuItem alloc] init];
    [menu addItem:appItem];
    NSMenu* appMenu = [[NSMenu alloc] initWithTitle:@"Структуры данных"];
    [appMenu addItemWithTitle:@"Завершить Структуры данных" action:@selector(terminate:) keyEquivalent:@"q"];
    appItem.submenu = appMenu;
    NSMenuItem* editItem = [[NSMenuItem alloc] init];
    [menu addItem:editItem];
    NSMenu* editMenu = [[NSMenu alloc] initWithTitle:@"Правка"];
    [editMenu addItemWithTitle:@"Отменить" action:@selector(undo:) keyEquivalent:@"z"];
    [editMenu addItemWithTitle:@"Вырезать" action:@selector(cut:) keyEquivalent:@"x"];
    [editMenu addItemWithTitle:@"Копировать" action:@selector(copy:) keyEquivalent:@"c"];
    [editMenu addItemWithTitle:@"Вставить" action:@selector(paste:) keyEquivalent:@"v"];
    [editMenu addItemWithTitle:@"Выбрать всё" action:@selector(selectAll:) keyEquivalent:@"a"];
    editItem.submenu = editMenu;
    NSApp.mainMenu = menu;

    NSRect screen = NSScreen.mainScreen.visibleFrame;
    CGFloat width = MIN(1460, screen.size.width - 70);
    CGFloat height = MIN(970, screen.size.height - 60);
    self.window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0, 0, width, height)
        styleMask:NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
                | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable
        backing:NSBackingStoreBuffered defer:NO];
    self.window.title = @"ЛР-1 · Деревья";
    self.window.minSize = NSMakeSize(980, 720);
    self.window.titlebarAppearsTransparent = YES;
    self.window.backgroundColor = [NSColor colorWithRed:0.969 green:0.973 blue:0.965 alpha:1];
    [self.window center];

    WKWebViewConfiguration* configuration = [[WKWebViewConfiguration alloc] init];
    [configuration.userContentController addScriptMessageHandler:self name:@"lab1"];
    self.webView = [[WKWebView alloc] initWithFrame:self.window.contentView.bounds configuration:configuration];
    self.webView.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
    self.webView.navigationDelegate = self;
    [self.webView setValue:@NO forKey:@"drawsBackground"];
    self.window.contentView = self.webView;
    NSURL* folder = [NSBundle.mainBundle.resourceURL URLByAppendingPathComponent:@"web"];
    [self.webView loadFileURL:[folder URLByAppendingPathComponent:@"index.html"] allowingReadAccessToURL:folder];
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication*)sender {
    return YES;
}

- (void)webView:(WKWebView*)webView decidePolicyForNavigationAction:(WKNavigationAction*)action
    decisionHandler:(void (^)(WKNavigationActionPolicy))decisionHandler {
    decisionHandler(action.request.URL.isFileURL ? WKNavigationActionPolicyAllow : WKNavigationActionPolicyCancel);
}

- (void)sendResponse:(NSDictionary*)response {
    NSData* data = [NSJSONSerialization dataWithJSONObject:response options:0 error:nil];
    NSString* json = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    NSString* script = [NSString stringWithFormat:@"window.onNativeMessage(%@)", json];
    [self.webView evaluateJavaScript:script completionHandler:nil];
}

- (void)userContentController:(WKUserContentController*)controller didReceiveScriptMessage:(WKScriptMessage*)message {
    if (!message.frameInfo.isMainFrame || ![message.body isKindOfClass:[NSDictionary class]]) {
        return;
    }
    NSDictionary* request = message.body;
    NSNumber* requestId = request[@"id"];
    if ([request[@"action"] isEqualToString:@"export"]) {
        NSSavePanel* panel = [NSSavePanel savePanel];
        panel.nameFieldStringValue = [request[@"name"] isEqualToString:@"structure-tests.csv"]
            ? @"structure-tests.csv" : @"benchmark-results.csv";
        [panel beginSheetModalForWindow:self.window completionHandler:^(NSModalResponse response) {
            if (response == NSModalResponseOK) {
                NSError* error = nil;
                BOOL saved = [request[@"csv"] writeToURL:panel.URL atomically:YES encoding:NSUTF8StringEncoding error:&error];
                [self sendResponse:@{@"id": requestId, @"saved": @(saved),
                                     @"error": error.localizedDescription ?: @""}];
            } else {
                [self sendResponse:@{@"id": requestId, @"cancelled": @YES}];
            }
        }];
        return;
    }
    if ((![@[@"structure"] containsObject:request[@"action"]]) || self.busy) {
        [self sendResponse:@{@"id": requestId, @"error": @"Дождитесь завершения текущего расчёта"}];
        return;
    }
    self.busy = YES;
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
        @autoreleasepool {
            NSDictionary* response;
            try {
                response = @{@"id": requestId, @"lab": RunStructureLab(request)};
            } catch (const std::exception& error) {
                response = @{@"id": requestId, @"error": [NSString stringWithUTF8String:error.what()]};
            }
            dispatch_async(dispatch_get_main_queue(), ^{
                self.busy = NO;
                [self sendResponse:response];
            });
        }
    });
}
@end

int main(int argc, const char* argv[]) {
    @autoreleasepool {
        NSApplication* app = NSApplication.sharedApplication;
        [app setActivationPolicy:NSApplicationActivationPolicyRegular];
        StructuresApp* delegate = [[StructuresApp alloc] init];
        app.delegate = delegate;
        [app run];
    }
    return 0;
}
