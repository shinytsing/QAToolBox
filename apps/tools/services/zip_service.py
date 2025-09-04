#!/usr/bin/env python3
"""
ZIP文件处理服务
支持多文件打包和单文件压缩打包
"""
import logging
import mimetypes
import os
import shutil
import tempfile
import urllib.parse
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ZipService:
    """ZIP文件处理服务类"""

    def __init__(self):
        self.supported_formats = {
            "zip": "application/zip",
            "rar": "application/x-rar-compressed",
            "7z": "application/x-7z-compressed",
            "tar": "application/x-tar",
            "gz": "application/gzip",
        }

    def create_zip_from_files(
        self, file_paths: List[str], zip_name: str = None, compression_level: int = 6, include_paths: bool = True
    ) -> Tuple[bool, str, Optional[str]]:
        """
        从多个文件创建ZIP包

        Args:
            file_paths: 文件路径列表
            zip_name: ZIP文件名（可选）
            compression_level: 压缩级别 (0-9)
            include_paths: 是否包含文件路径结构

        Returns:
            (success, message, zip_path)
        """
        try:
            if not file_paths:
                return False, "没有提供文件路径", None

            # 验证文件是否存在
            valid_files = []
            for file_path in file_paths:
                # URL解码文件路径
                decoded_path = urllib.parse.unquote(str(file_path))

                # 检查是否是媒体文件路径
                if (
                    decoded_path.startswith("audio_files/")
                    or decoded_path.startswith("media/")
                    or decoded_path.startswith("temp_audio/")
                ):
                    # 构建完整的媒体文件路径
                    from django.conf import settings

                    media_path = os.path.join(settings.MEDIA_ROOT, decoded_path)
                    if os.path.exists(media_path) and os.path.isfile(media_path):
                        valid_files.append(media_path)
                    else:
                        logger.warning(f"媒体文件不存在: {media_path}")
                        # 尝试查找相似的文件名
                        try:
                            dir_path = os.path.dirname(media_path)
                            if os.path.exists(dir_path):
                                files_in_dir = os.listdir(dir_path)
                                for file_in_dir in files_in_dir:
                                    if urllib.parse.unquote(file_in_dir) == os.path.basename(decoded_path):
                                        found_path = os.path.join(dir_path, file_in_dir)
                                        valid_files.append(found_path)
                                        logger.info(f"找到匹配文件: {found_path}")
                                        break
                        except Exception as e:
                            logger.warning(f"查找相似文件失败: {e}")
                elif os.path.exists(decoded_path) and os.path.isfile(decoded_path):
                    valid_files.append(decoded_path)
                else:
                    logger.warning(f"文件不存在或不是文件: {decoded_path}")

            if not valid_files:
                return False, "没有有效的文件可以打包", None

            # 生成ZIP文件名
            if not zip_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_name = f"files_{timestamp}.zip"
            elif not zip_name.endswith(".zip"):
                zip_name += ".zip"

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, zip_name)

            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                for file_path in valid_files:
                    try:
                        if include_paths:
                            # 包含相对路径
                            arcname = os.path.relpath(file_path, os.path.commonpath([os.path.dirname(f) for f in valid_files]))
                        else:
                            # 只包含文件名
                            arcname = os.path.basename(file_path)

                        # 如果是媒体文件，使用原始文件名
                        from django.conf import settings

                        if str(file_path).startswith(str(settings.MEDIA_ROOT)):
                            # 从媒体路径中提取原始文件名
                            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                            if not include_paths:
                                arcname = os.path.basename(relative_path)
                            else:
                                arcname = relative_path

                        zipf.write(file_path, arcname)
                        logger.info(f"已添加文件到ZIP: {file_path} -> {arcname}")

                    except Exception as e:
                        logger.error(f"添加文件到ZIP失败: {file_path}, 错误: {str(e)}")
                        continue

            # 检查ZIP文件是否创建成功
            if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
                return True, f"成功创建ZIP文件，包含 {len(valid_files)} 个文件", zip_path
            else:
                return False, "ZIP文件创建失败", None

        except Exception as e:
            logger.error(f"创建ZIP文件时发生错误: {str(e)}")
            return False, f"创建ZIP文件失败: {str(e)}", None

    def create_zip_from_directory(
        self, directory_path: str, zip_name: str = None, compression_level: int = 6, exclude_patterns: List[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        从目录创建ZIP包

        Args:
            directory_path: 目录路径
            zip_name: ZIP文件名（可选）
            compression_level: 压缩级别 (0-9)
            exclude_patterns: 排除的文件模式列表

        Returns:
            (success, message, zip_path)
        """
        try:
            if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
                return False, "目录不存在", None

            # 生成ZIP文件名
            if not zip_name:
                dir_name = os.path.basename(directory_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_name = f"{dir_name}_{timestamp}.zip"
            elif not zip_name.endswith(".zip"):
                zip_name += ".zip"

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, zip_name)

            # 默认排除模式
            if exclude_patterns is None:
                exclude_patterns = ["__pycache__", ".git", ".svn", ".DS_Store", "*.pyc", "*.pyo", "*.log", "*.tmp"]

            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                file_count = 0
                for root, dirs, files in os.walk(directory_path):
                    # 排除目录
                    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

                    for file in files:
                        file_path = os.path.join(root, file)

                        # 检查是否应该排除
                        if any(pattern in file for pattern in exclude_patterns):
                            continue

                        try:
                            # 计算相对路径
                            arcname = os.path.relpath(file_path, directory_path)
                            zipf.write(file_path, arcname)
                            file_count += 1
                            logger.debug(f"已添加文件: {arcname}")

                        except Exception as e:
                            logger.error(f"添加文件失败: {file_path}, 错误: {str(e)}")
                            continue

            # 检查ZIP文件是否创建成功
            if os.path.exists(zip_path) and os.path.getsize(zip_path) > 0:
                return True, f"成功创建ZIP文件，包含 {file_count} 个文件", zip_path
            else:
                return False, "ZIP文件创建失败", None

        except Exception as e:
            logger.error(f"从目录创建ZIP文件时发生错误: {str(e)}")
            return False, f"创建ZIP文件失败: {str(e)}", None

    def compress_single_file(self, file_path: str, compression_level: int = 9) -> Tuple[bool, str, Optional[str]]:
        """
        压缩单个文件

        Args:
            file_path: 文件路径
            compression_level: 压缩级别 (0-9)

        Returns:
            (success, message, zip_path)
        """
        try:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return False, "文件不存在", None

            # 获取文件信息
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)

            # 生成ZIP文件名
            name_without_ext = os.path.splitext(file_name)[0]
            zip_name = f"{name_without_ext}_compressed.zip"

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, zip_name)

            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                zipf.write(file_path, file_name)

            # 检查压缩效果
            zip_size = os.path.getsize(zip_path)
            compression_ratio = (1 - zip_size / file_size) * 100 if file_size > 0 else 0

            if os.path.exists(zip_path) and zip_size > 0:
                return True, f"文件压缩成功，压缩率: {compression_ratio:.1f}%", zip_path
            else:
                return False, "文件压缩失败", None

        except Exception as e:
            logger.error(f"压缩文件时发生错误: {str(e)}")
            return False, f"压缩文件失败: {str(e)}", None

    def extract_zip(self, zip_path: str, extract_to: str = None) -> Tuple[bool, str, Optional[str]]:
        """
        解压ZIP文件

        Args:
            zip_path: ZIP文件路径
            extract_to: 解压目标目录（可选）

        Returns:
            (success, message, extract_path)
        """
        try:
            if not os.path.exists(zip_path) or not zip_path.endswith(".zip"):
                return False, "ZIP文件不存在或格式不正确", None

            # 确定解压目录
            if not extract_to:
                extract_to = tempfile.mkdtemp()
            else:
                os.makedirs(extract_to, exist_ok=True)

            # 解压文件
            with zipfile.ZipFile(zip_path, "r") as zipf:
                # 检查文件列表
                file_list = zipf.namelist()
                logger.info(f"ZIP文件包含 {len(file_list)} 个文件")

                # 解压所有文件
                zipf.extractall(extract_to)

            return True, f"成功解压 {len(file_list)} 个文件", extract_to

        except Exception as e:
            logger.error(f"解压ZIP文件时发生错误: {str(e)}")
            return False, f"解压失败: {str(e)}", None

    def get_zip_info(self, zip_path: str) -> Dict:
        """
        获取ZIP文件信息

        Args:
            zip_path: ZIP文件路径

        Returns:
            ZIP文件信息字典
        """
        try:
            if not os.path.exists(zip_path):
                return {"error": "文件不存在"}

            with zipfile.ZipFile(zip_path, "r") as zipf:
                file_list = zipf.namelist()
                total_size = sum(zipf.getinfo(name).file_size for name in file_list)
                compressed_size = sum(zipf.getinfo(name).compress_size for name in file_list)

                return {
                    "file_count": len(file_list),
                    "total_size": total_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": (1 - compressed_size / total_size) * 100 if total_size > 0 else 0,
                    "files": file_list[:10],  # 只返回前10个文件名
                    "zip_size": os.path.getsize(zip_path),
                }

        except Exception as e:
            logger.error(f"获取ZIP信息时发生错误: {str(e)}")
            return {"error": str(e)}

    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        清理临时文件

        Args:
            file_paths: 要清理的文件路径列表
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    logger.info(f"已清理临时文件: {file_path}")
            except Exception as e:
                logger.error(f"清理临时文件失败: {file_path}, 错误: {str(e)}")


# 创建全局实例
zip_service = ZipService()
