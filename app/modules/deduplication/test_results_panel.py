#!/usr/bin/env python3
"""
图片去重结果面板单元测试
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 添加项目路径到sys.path
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(project_root))

# 设置编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 导入PyQt6模块
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
except ImportError as e:
    print(f"无法导入PyQt6: {e}")
    print("请确保在UV虚拟环境中安装了PyQt6")
    sys.exit(1)

# Mock掉外部依赖
sys.modules['utils.image_utils'] = MagicMock()
sys.modules['utils.ui_helpers'] = MagicMock()
sys.modules['utils.image_cache_enhanced'] = MagicMock()

# 直接导入测试目标模块
try:
    from results_panel import DuplicateGroupWidget, DuplicateImageWidget
except ImportError as e:
    print(f"无法导入测试模块: {e}")
    sys.exit(1)


class TestDuplicateGroupWidget(unittest.TestCase):
    """测试重复组控件"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建QApplication实例（PyQt6测试需要）
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_fixed_aspect_ratio(self):
        """测试固定宽高比"""
        # 创建测试控件
        widget = DuplicateGroupWidget(1, ['file1.jpg', 'file2.jpg'], 0.95)
        
        # 设置宽度为300px
        test_width = 300
        widget.update_thumbnails(test_width)
        
        # 验证高度是否为宽度的1/2（2:1比例）
        expected_height = int(test_width / 2)
        self.assertEqual(widget.height(), expected_height)
        self.assertEqual(widget.card_height, expected_height)
        
        print(f"[PASS] 固定宽高比测试通过: 宽度={test_width}, 高度={widget.height()}, 比例=2:1")

    def test_padding_calculation(self):
        """测试内边距计算"""
        widget = DuplicateGroupWidget(1, ['file1.jpg', 'file2.jpg'], 0.95)
        
        # 设置宽度为300px，高度应为200px
        test_width = 300
        widget.update_thumbnails(test_width)
        
        # 计算期望的内边距（高度的1/6）
        expected_padding = int(widget.card_height / 6)
        
        # 获取实际的内边距
        margins = widget.images_layout.contentsMargins()
        actual_padding = margins.left()  # 左右边距应该相同
        
        self.assertEqual(actual_padding, expected_padding)
        print(f"[PASS] 内边距计算测试通过: 高度={widget.card_height}, 内边距={actual_padding}, 应为高度的1/6")

    def test_spacing_calculation(self):
        """测试图片间距计算"""
        widget = DuplicateGroupWidget(1, ['file1.jpg', 'file2.jpg'], 0.95)
        
        # 设置宽度为300px
        test_width = 300
        widget.update_thumbnails(test_width)
        
        # 计算期望的间距（高度的1/12）
        expected_spacing = int(widget.card_height / 12)
        actual_spacing = widget.images_layout.spacing()
        
        self.assertEqual(actual_spacing, expected_spacing)
        print(f"[PASS] 图片间距计算测试通过: 高度={widget.card_height}, 间距={actual_spacing}, 应为高度的1/12")

    def test_image_distribution(self):
        """测试图片分布计算"""
        # 测试多个图片的情况
        files = ['file1.jpg', 'file2.jpg', 'file3.jpg']
        widget = DuplicateGroupWidget(1, files, 0.95)
        
        # 设置宽度为300px
        test_width = 300
        widget.update_thumbnails(test_width)
        
        # 验证是否创建了正确数量的图片控件
        self.assertEqual(len(widget.image_widgets), len(files))
        print(f"[PASS] 图片分布测试通过: 期望图片数={len(files)}, 实际图片数={len(widget.image_widgets)}")

    def test_image_dimensions(self):
        """测试图片尺寸计算"""
        widget = DuplicateGroupWidget(1, ['file1.jpg', 'file2.jpg'], 0.95)
        
        # 设置宽度为300px
        test_width = 300
        widget.update_thumbnails(test_width)
        
        # 验证图片控件的尺寸是否合理
        if widget.image_widgets:
            image_widget = widget.image_widgets[0]
            # 图片宽度应该大于0且小于卡片宽度
            self.assertGreater(image_widget.width, 0)
            self.assertLess(image_widget.width, test_width)
            # 图片高度应该大于0且小于卡片高度
            self.assertGreater(image_widget.height, 0)
            self.assertLess(image_widget.height, widget.card_height)
            
        print(f"[PASS] 图片尺寸计算测试通过: 卡片宽度={test_width}, 卡片高度={widget.card_height}")


class TestDuplicateImageWidget(unittest.TestCase):
    """测试重复图片控件"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建QApplication实例（PyQt6测试需要）
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def test_widget_creation(self):
        """测试控件创建"""
        # 使用mock避免实际文件访问
        with patch('results_panel.ImageUtils.get_thumbnail'):
            widget = DuplicateImageWidget('test.jpg', 100, 100)
            
            # 验证控件属性
            self.assertEqual(widget.file_path, 'test.jpg')
            self.assertEqual(widget.width, 100)
            self.assertFalse(widget.is_selected)
            print("[PASS] 图片控件创建测试通过")


def run_tests():
    """运行所有测试"""
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateGroupWidget))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateImageWidget))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("开始运行图片去重结果面板单元测试...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("[SUCCESS] 所有测试通过!")
    else:
        print("[FAILED] 部分测试失败!")
    
    sys.exit(0 if success else 1)