#include "gui/StructureLab.h"
#include <cassert>

int main() {
    @autoreleasepool {
        int total = 0;
        for (NSString* kind in @[@"array",@"tree",@"hash",@"queue",@"minheap",@"maxheap"]) {
            NSArray* types = [kind hasSuffix:@"heap"] ? @[@"double"] : @[@"int",@"double",@"string"];
            for (NSString* type in types) {
                NSDictionary* request = @{@"structure":kind,@"valueType":type,@"mode":@"tests"};
                NSDictionary* result = RunStructureLab(request);
                if ([result[@"failed"] intValue]) NSLog(@"FAILED %@ %@: %@",kind,type,result[@"steps"]);
                assert([result[@"failed"] intValue] == 0);
                assert([result[@"passed"] intValue] == [result[@"total"] intValue]);
                total += [result[@"total"] intValue];
                NSMutableDictionary* prefix = [request mutableCopy]; prefix[@"count"]=@0;
                assert([RunStructureLab(prefix)[@"steps"] count] == 0);
            }
        }
        assert(total == 244);
        NSDictionary* fractions = RunStructureLab(@{@"structure":@"minheap",@"valueType":@"double",@"mode":@"manual",
            @"operations":@[@{@"op":@"push",@"value":@"1.25"},@{@"op":@"top"}]});
        assert([fractions[@"snapshot"][@"values"] isEqual:@[@"1.25"]]);
        NSDictionary* tree = RunStructureLab(@{@"structure":@"tree",@"valueType":@"int",@"mode":@"manual",
            @"operations":@[@{@"op":@"insert",@"value":@"2"},@{@"op":@"insert",@"value":@"1"},
                @{@"op":@"inorder"}]});
        assert([tree[@"steps"][2][@"actual"] isEqual:@"1 2"]);
        assert(([tree[@"snapshot"][@"values"] isEqual:@[@"1",@"2"]]));
        std::cout << "[OK] Native backend: " << total << " checks, replay, double heap and tree operations\n";
    }
}
