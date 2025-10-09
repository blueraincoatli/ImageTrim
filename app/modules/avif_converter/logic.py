#!/usr/bin/env python3
"""
AVIF转换模块逻辑实现
"""

import os
import threading
from datetime import datetime
from PIL import Image


class AVIFConverterLogic:
    """
    AVIF转换逻辑类
    """

    def __init__(self, module):
        self.module = module
        self.is_running = False
        
    def convert_images(self, params: dict):
        """
        转换图片

        Args:
            params: 转换参数
        """
        try:
            source_path = params['source_path']
            target_path = params['target_path']
            quality = params.get('quality', 85)
            format_type = params.get('format', 'AVIF')
            scan_subdirs = params.get('include_subdirs', True)
            
            # 初始化统计信息
            total_files = 0
            converted_files = 0
            failed_files = 0
            
            # 收集要转换的文件
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            if scan_subdirs:
                for root, _, files in os.walk(source_path):
                    if not self.is_running: 
                        self.module.log_message.emit("转换已停止", "info")
                        return
                    for file in files:
                        if file.lower().endswith(valid_extensions):
                            image_files.append((os.path.join(root, file), root))
            else:
                for file in os.listdir(source_path):
                    if not self.is_running: 
                        self.module.log_message.emit("转换已停止", "info")
                        return
                    if file.lower().endswith(valid_extensions):
                        image_files.append((os.path.join(source_path, file), source_path))
            
            if not image_files:
                self.module.log_message.emit("未找到要转换的图片文件", "warning")
                self.module.execution_finished.emit({})
                return
                
            total_files = len(image_files)
            self.module.log_message.emit(f"找到 {total_files} 个文件需要转换", "info")
            
            # 更新进度标签和统计信息
            self.module.progress_updated.emit(0, f"正在转换: 0/{total_files}")
            # 发送统计信息更新信号（如果模块支持）
            
            # 转换文件
            last_converted_source = None
            last_converted_target = None
            
            for i, (file_path, original_dir) in enumerate(image_files):
                if not self.is_running: 
                    self.module.log_message.emit("转换已停止", "info")
                    break
                    
                try:
                    # 显示当前转换图片的预览
                    if hasattr(self.module, 'workspace_ui') and self.module.workspace_ui:
                        self.module.workspace_ui.show_preview(file_path)
                    
                    # 计算目标路径
                    relative_path = os.path.relpath(original_dir, source_path)
                    target_dir = os.path.join(target_path, relative_path) if relative_path != '.' else target_path
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 生成目标文件名
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    
                    # 根据选择的格式确定扩展名
                    if format_type.upper() == 'AVIF':
                        target_file_ext = '.avif'
                    elif format_type.upper() == 'WEBP':
                        target_file_ext = '.webp'
                    elif format_type.upper() == 'JPEG':
                        target_file_ext = '.jpg'
                    elif format_type.upper() == 'PNG':
                        target_file_ext = '.png'
                    else:
                        target_file_ext = '.avif'  # 默认为AVIF
                        
                    target_file = os.path.join(target_dir, f"{base_name}{target_file_ext}")
                    
                    # 保存原始目标文件路径以处理重复
                    original_target_file = target_file
                    
                    # 检查是否已存在
                    if os.path.exists(target_file):
                        counter = 1
                        while os.path.exists(
                            os.path.join(target_dir, f"{base_name}_{counter}{target_file_ext}")
                        ):
                            counter += 1
                        target_file = os.path.join(target_dir, f"{base_name}_{counter}{target_file_ext}")
                    
                    # 转换图片
                    with Image.open(file_path) as img:
                        # 处理RGBA模式图片
                        if img.mode == 'RGBA':
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        # 根据格式保存
                        if format_type.upper() == 'AVIF':
                            img.save(target_file, 'AVIF', quality=quality)
                        elif format_type.upper() == 'WEBP':
                            img.save(target_file, 'WEBP', quality=quality)
                        elif format_type.upper() == 'JPEG':
                            img.save(target_file, 'JPEG', quality=quality)
                        elif format_type.upper() == 'PNG':
                            img.save(target_file, 'PNG')
                    
                    converted_files += 1
                    self.module.log_message.emit(
                        f"已转换: {os.path.basename(file_path)} -> {os.path.basename(target_file)}", 
                        "success"
                    )
                    
                    # 保存最后转换的文件路径以显示压缩比率
                    last_converted_source = file_path
                    last_converted_target = target_file
                    
                    # 显示当前转换文件的压缩比率
                    if hasattr(self.module, 'workspace_ui') and self.module.workspace_ui:
                        self.module.workspace_ui.show_compression_ratio(file_path, target_file)
                    
                    # 更新进度和统计信息
                    progress = (i + 1) / total_files * 100
                    self.module.progress_updated.emit(
                        progress, 
                        f"正在转换: {converted_files}/{total_files}"
                    )
                    
                except Exception as e:
                    failed_files += 1
                    self.module.log_message.emit(
                        f"转换失败 {os.path.basename(file_path)}: {str(e)}", 
                        "error"
                    )
            
            # 完成
            self.module.log_message.emit(
                f"转换完成! 成功转换 {converted_files}/{total_files} 个文件", 
                "info"
            )
            
            # 发送完成信号
            self.module.execution_finished.emit({
                'total_files': total_files,
                'converted_files': converted_files,
                'failed_files': failed_files
            })
            
        except Exception as e:
            self.module.log_message.emit(f"转换过程中出错: {str(e)}", "error")
            # 发送完成信号
            self.module.execution_finished.emit({})
        finally:
            self.is_running = False