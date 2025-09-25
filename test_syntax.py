#!/usr/bin/env python3
# 测试improved_deduplication_module.py语法

try:
    import improved_deduplication_module
    print("SUCCESS: 模块导入成功")
    
    # 检查类定义
    if hasattr(improved_deduplication_module, 'ImprovedDeduplicationModule'):
        print("SUCCESS: ImprovedDeduplicationModule类存在")
        
        # 尝试实例化
        module = improved_deduplication_module.ImprovedDeduplicationModule()
        print("SUCCESS: 类实例化成功")
    else:
        print("ERROR: ImprovedDeduplicationModule类不存在")
        
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
except Exception as e:
    print(f"ERROR: {e}")

print("测试完成")