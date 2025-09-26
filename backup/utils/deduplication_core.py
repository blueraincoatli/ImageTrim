# -*- coding: utf-8 -*-
"""
核心去重逻辑模块
统一图片去重的核心业务逻辑，消除代码重复
"""

import os
import time
import hashlib
import threading
from typing import Dict, List, Set, Tuple, Optional, Callable
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    import imagehash
except ImportError:
    print("错误: 必须的库未安装。请运行 'pip install Pillow imagehash'")
    exit()


@dataclass
class DeduplicationConfig:
    """去重配置类"""
    similarity_threshold: float = 95.0  # 相似度阈值 (70-100)
    include_subdirectories: bool = True
    valid_extensions: Tuple[str, ...] = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    enable_logging: bool = True
    log_callback: Optional[Callable] = None


@dataclass
class ScanResult:
    """扫描结果类"""
    total_files: int = 0
    processed_files: int = 0
    duplicate_groups: Dict[str, List[str]] = None
    scan_time: float = 0.0
    hashes_computed: int = 0
    comparisons_made: int = 0

    def __post_init__(self):
        if self.duplicate_groups is None:
            self.duplicate_groups = {}


class ImageHashCalculator:
    """图片哈希计算器"""

    @staticmethod
    def calculate_phash(file_path: str, size: int = 64) -> Optional[int]:
        """
        计算图片的感知哈希值

        Args:
            file_path: 图片文件路径
            size: 哈希计算尺寸 (默认64x64)

        Returns:
            哈希整数值，失败返回None
        """
        try:
            # 验证文件大小
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                return None

            # 使用PIL计算感知哈希
            with Image.open(file_path) as img:
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # 计算感知哈希
                phash = imagehash.phash(img, hash_size=size // 8)
                return int(str(phash), 16)

        except Exception as e:
            # 静默跳过无法处理的文件
            return None

    @staticmethod
    def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> Optional[str]:
        """
        计算文件内容的MD5哈希（用于精确去重）

        Args:
            file_path: 文件路径
            chunk_size: 读取块大小

        Returns:
            MD5哈希字符串，失败返回None
        """
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 分块读取大文件
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()
        except Exception:
            return None


class DuplicateFinder:
    """重复图片查找器"""

    def __init__(self, config: DeduplicationConfig):
        self.config = config
        self._is_running = False

    def stop(self):
        """停止查找过程"""
        self._is_running = False

    def _find_duplicates_naive(self, hashes: Dict[str, int], threshold: int) -> Dict[str, List[str]]:
        """
        原始的O(n²)算法，用于小规模数据集（保证正确性）

        Args:
            hashes: 图片路径到哈希值的映射
            threshold: 相似度阈值

        Returns:
            重复组字典 {主文件: [重复文件列表]}
        """
        duplicates = defaultdict(list)
        files_to_check = list(hashes.keys())

        for i in range(len(files_to_check)):
            if not self._is_running:
                break

            f1 = files_to_check[i]
            if f1 not in hashes:
                continue

            for j in range(i + 1, len(files_to_check)):
                if not self._is_running:
                    break

                f2 = files_to_check[j]
                if f2 not in hashes:
                    continue

                # 计算哈希值差异
                hash_diff = abs(hashes[f1] - hashes[f2])
                if hash_diff <= threshold:
                    if not duplicates[f1]:
                        duplicates[f1].append(f1)  # 添加主文件
                    duplicates[f1].append(f2)
                    # 从后续检查中移除已匹配的文件
                    if f2 in hashes:
                        del hashes[f2]

        return duplicates

    def _find_duplicates_optimized(self, hashes: Dict[str, int], threshold: int) -> Dict[str, List[str]]:
        """
        优化后的重复图片查找算法

        保守策略：
        1. 小数据集（<1000文件）：使用原始O(n²)算法，确保正确性
        2. 大数据集（≥1000文件）：使用滑动窗口优化

        Args:
            hashes: 图片路径到哈希值的映射
            threshold: 相似度阈值

        Returns:
            重复组字典
        """
        if not hashes:
            return {}

        files_to_check = list(hashes.keys())

        # 对于个人桌面程序，文件数量通常不会太大
        # 使用保守阈值，确保正确性优先
        if len(files_to_check) <= 1000:
            # 直接使用原始算法，保证100%正确性
            if self.config.log_callback:
                self.config.log_callback(f"文件数量 {len(files_to_check)} 较少，使用精确算法", "info")
            return self._find_duplicates_naive(hashes, threshold)

        # 对于大数据集，使用安全的滑动窗口优化
        duplicates = defaultdict(list)
        comparison_count = 0

        # 按哈希值排序，这样相似的文件会相邻
        sorted_files = sorted(hashes.items(), key=lambda x: x[1])

        # 使用滑动窗口策略
        for i in range(len(sorted_files)):
            if not self._is_running:
                break

            f1, h1 = sorted_files[i]

            # 只检查后续的文件
            for j in range(i + 1, len(sorted_files)):
                if not self._is_running:
                    break

                f2, h2 = sorted_files[j]
                comparison_count += 1

                # 如果哈希值差距已经超过threshold，可以提前终止
                if h2 - h1 > threshold:
                    break

                if abs(h1 - h2) <= threshold:
                    if not duplicates[f1]:
                        duplicates[f1].append(f1)
                    duplicates[f1].append(f2)

        # 输出性能统计
        original_comparisons = len(files_to_check) * (len(files_to_check) - 1) // 2
        improvement = (1 - comparison_count / original_comparisons) * 100

        if self.config.log_callback:
            self.config.log_callback(
                f"算法优化完成: 原始比较 {original_comparisons:,} 次, "
                f"实际比较 {comparison_count:,} 次, "
                f"减少 {improvement:.1f}%",
                "info"
            )

        return duplicates

    def find_exact_duplicates(self, file_hashes: Dict[str, str]) -> Dict[str, List[str]]:
        """
        查找完全相同的文件（基于MD5）

        Args:
            file_hashes: 文件路径到MD5哈希的映射

        Returns:
            重复组字典
        """
        hash_groups = defaultdict(list)
        for file_path, file_hash in file_hashes.items():
            if file_hash:
                hash_groups[file_hash].append(file_path)

        # 只返回有重复的组
        return {group[0]: group[1:] for group in hash_groups.values() if len(group) > 1}


class DirectoryScanner:
    """目录扫描器"""

    def __init__(self, config: DeduplicationConfig):
        self.config = config
        self._is_running = False

    def stop(self):
        """停止扫描过程"""
        self._is_running = False

    def scan_directories(self, scan_paths: List[str]) -> Tuple[List[str], Dict[str, str]]:
        """
        扫描指定目录，收集所有图片文件

        Args:
            scan_paths: 要扫描的路径列表

        Returns:
            (图片文件列表, 文件哈希字典)
        """
        self._is_running = True
        image_files = []
        file_hashes = {}

        total_paths = len(scan_paths)

        for path_idx, scan_path in enumerate(scan_paths):
            if not self._is_running:
                break

            # 更新进度信息
            if self.config.log_callback:
                self.config.log_callback(
                    f"正在扫描路径 ({path_idx+1}/{total_paths}): {scan_path}",
                    "info"
                )

            # 验证路径存在性
            if not os.path.isdir(scan_path):
                if self.config.log_callback:
                    self.config.log_callback(f"路径不存在: {scan_path}", "warning")
                continue

            # 扫描文件
            if self.config.include_subdirectories:
                # 递归扫描子目录
                for root, _, files in os.walk(scan_path):
                    if not self._is_running:
                        break

                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._is_valid_image_file(file_path):
                            image_files.append(file_path)
            else:
                # 只扫描当前目录
                try:
                    for file in os.listdir(scan_path):
                        file_path = os.path.join(scan_path, file)
                        if os.path.isfile(file_path) and self._is_valid_image_file(file_path):
                            image_files.append(file_path)
                except PermissionError:
                    if self.config.log_callback:
                        self.config.log_callback(f"无权限访问目录: {scan_path}", "warning")
                    continue

        if self.config.log_callback:
            self.config.log_callback(f"扫描完成，找到 {len(image_files)} 个图片文件", "info")

        return image_files, file_hashes

    def _is_valid_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为有效的图片文件

        Args:
            file_path: 文件路径

        Returns:
            是否为有效图片文件
        """
        try:
            # 检查文件扩展名
            if not file_path.lower().endswith(self.config.valid_extensions):
                return False

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size == 0 or file_size > self.config.max_file_size:
                return False

            # 尝试打开文件验证是否为有效图片
            with Image.open(file_path) as img:
                img.verify()  # 验证图片完整性

            return True

        except Exception:
            return False


class DeduplicationEngine:
    """图片去重引擎 - 统一的核心业务逻辑"""

    def __init__(self, config: DeduplicationConfig = None):
        self.config = config or DeduplicationConfig()
        self.hash_calculator = ImageHashCalculator()
        self.duplicate_finder = DuplicateFinder(self.config)
        self.directory_scanner = DirectoryScanner(self.config)
        self._is_running = False

    def stop(self):
        """停止去重过程"""
        self._is_running = False
        self.duplicate_finder.stop()
        self.directory_scanner.stop()

    def set_config(self, config: DeduplicationConfig):
        """更新配置"""
        self.config = config
        self.duplicate_finder.config = config
        self.directory_scanner.config = config

    def set_log_callback(self, callback: Callable[[str, str], None]):
        """设置日志回调函数"""
        self.config.log_callback = callback

    def scan_and_find_duplicates(self, scan_paths: List[str]) -> ScanResult:
        """
        执行完整的扫描和去重流程

        Args:
            scan_paths: 要扫描的路径列表

        Returns:
            扫描结果
        """
        start_time = time.time()
        self._is_running = True

        result = ScanResult()

        try:
            # 1. 扫描目录，收集图片文件
            image_files, file_hashes = self.directory_scanner.scan_directories(scan_paths)
            result.total_files = len(image_files)

            if not self._is_running or not image_files:
                if self.config.log_callback:
                    self.config.log_callback("扫描被中断或未找到图片文件", "warning")
                return result

            # 2. 计算图片感知哈希
            if self.config.log_callback:
                self.config.log_callback("开始计算图片相似度哈希...", "info")

            image_hashes = {}
            for i, file_path in enumerate(image_files):
                if not self._is_running:
                    break

                # 计算感知哈希
                phash = self.hash_calculator.calculate_phash(file_path)
                if phash is not None:
                    image_hashes[file_path] = phash

                # 计算文件MD5（用于精确去重）
                file_hash = self.hash_calculator.calculate_file_hash(file_path)
                if file_hash:
                    file_hashes[file_path] = file_hash

                result.hashes_computed += 1

                # 进度反馈
                if i % 50 == 0 and self.config.log_callback:
                    progress = (i + 1) / len(image_files) * 100
                    self.config.log_callback(
                        f"哈希计算进度: {progress:.1f}% ({i+1}/{len(image_files)})",
                        "info"
                    )

            if not self._is_running:
                if self.config.log_callback:
                    self.config.log_callback("哈希计算被中断", "warning")
                return result

            # 3. 查找相似图片
            if self.config.log_callback:
                self.config.log_callback("开始查找相似图片...", "info")

            # 计算相似度阈值（将百分比转换为哈希差异）
            threshold = int((100 - self.config.similarity_threshold) * 0.64)  # 转换为phash差异

            similar_duplicates = self.duplicate_finder._find_duplicates_optimized(image_hashes, threshold)

            # 4. 查找完全相同的文件
            if self.config.log_callback:
                self.config.log_callback("查找完全相同的文件...", "info")

            exact_duplicates = self.duplicate_finder.find_exact_duplicates(file_hashes)

            # 5. 合并结果
            result.duplicate_groups = self._merge_duplicate_results(similar_duplicates, exact_duplicates)
            result.processed_files = len(image_hashes)

            # 计算比较次数（估算）
            result.comparisons_made = len(image_hashes) * (len(image_hashes) - 1) // 2

            if self.config.log_callback:
                total_groups = len(result.duplicate_groups)
                total_duplicates = sum(len(group) - 1 for group in result.duplicate_groups.values())
                self.config.log_callback(
                    f"去重完成: 发现 {total_groups} 个重复组, "
                    f"共 {total_duplicates} 个重复文件",
                    "info"
                )

        except Exception as e:
            if self.config.log_callback:
                self.config.log_callback(f"去重过程出错: {str(e)}", "error")
        finally:
            result.scan_time = time.time() - start_time
            self._is_running = False

        return result

    def _merge_duplicate_results(self, similar_duplicates: Dict[str, List[str]],
                                exact_duplicates: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        合并相似重复和精确重复的结果

        Args:
            similar_duplicates: 相似图片重复组
            exact_duplicates: 精确重复文件组

        Returns:
            合并后的重复组
        """
        merged = {}

        # 首先添加相似重复组
        merged.update(similar_duplicates)

        # 然后添加精确重复组（避免重复）
        for master_file, duplicate_files in exact_duplicates.items():
            if master_file not in merged:
                merged[master_file] = [master_file] + duplicate_files
            else:
                # 如果主文件已在相似组中，合并重复文件列表
                existing_files = set(merged[master_file])
                new_files = [f for f in duplicate_files if f not in existing_files]
                merged[master_file].extend(new_files)

        return merged

    def get_statistics(self, scan_result: ScanResult) -> Dict[str, any]:
        """
        获取扫描统计信息

        Args:
            scan_result: 扫描结果

        Returns:
            统计信息字典
        """
        if not scan_result.duplicate_groups:
            return {
                "total_files": scan_result.total_files,
                "duplicate_groups": 0,
                "duplicate_files": 0,
                "potential_savings_mb": 0,
                "scan_time": scan_result.scan_time
            }

        total_duplicate_files = sum(len(group) - 1 for group in scan_result.duplicate_groups.values())

        # 计算可节省的空间（估算）
        total_size = 0
        duplicate_size = 0

        for master_file, duplicates in scan_result.duplicate_groups.items():
            try:
                # 主文件大小
                master_size = os.path.getsize(master_file)
                total_size += master_size

                # 重复文件大小
                for dup_file in duplicates[1:]:  # 跳过主文件
                    dup_size = os.path.getsize(dup_file)
                    total_size += dup_size
                    duplicate_size += dup_size
            except OSError:
                continue

        return {
            "total_files": scan_result.total_files,
            "processed_files": scan_result.processed_files,
            "duplicate_groups": len(scan_result.duplicate_groups),
            "duplicate_files": total_duplicate_files,
            "total_size_mb": total_size / (1024 * 1024),
            "duplicate_size_mb": duplicate_size / (1024 * 1024),
            "potential_savings_mb": duplicate_size / (1024 * 1024),
            "scan_time": scan_result.scan_time,
            "hashes_computed": scan_result.hashes_computed,
            "comparisons_made": scan_result.comparisons_made
        }