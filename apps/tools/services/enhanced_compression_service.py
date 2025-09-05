#!/usr/bin/env python3
"""
增强压缩服务
支持多种压缩算法和更好的压缩效果
"""
import bz2
import gzip
import logging
import lzma
import mimetypes
import os
import shutil
import tarfile
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EnhancedCompressionService:
    """增强压缩服务类"""

    def __init__(self):
        self.supported_formats = {
            "zip": "application/zip",
            "gz": "application/gzip",
            "bz2": "application/x-bzip2",
            "xz": "application/x-xz",
            "tar.gz": "application/gzip",
        }

    def _get_optimal_compression_method(self, file_paths: List[str]) -> str:
        """根据文件类型选择最优压缩方法"""
        if not file_paths:
            return "zip"

        # 分析文件类型
        text_files = 0
        binary_files = 0
        total_size = 0

        for file_path in file_paths:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size

                # 检查文件类型
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type and mime_type.startswith("text/"):
                    text_files += 1
                else:
                    binary_files += 1

        # 根据文件类型和大小选择压缩方法
        if total_size > 50 * 1024 * 1024:  # 大于50MB
            return "xz"
        elif text_files > binary_files:
            return "gz"
        elif binary_files > text_files:
            return "bz2"
        else:
            return "zip"

    def compress_with_zip(
        self, file_paths: List[str], output_path: str, compression_level: int = 9, include_paths: bool = True
    ) -> Tuple[bool, str]:
        """使用ZIP压缩"""
        try:
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        arcname = os.path.basename(file_path) if not include_paths else file_path
                        zipf.write(file_path, arcname)

                        # 添加压缩注释以提高压缩率
                        zipf.comment = f"Compressed with ZIP level {compression_level}".encode("utf-8")

            return True, "ZIP压缩成功"
        except Exception as e:
            return False, f"ZIP压缩失败: {str(e)}"

    def compress_with_gzip(self, file_paths: List[str], output_path: str, compression_level: int = 9) -> Tuple[bool, str]:
        """使用GZIP压缩（单文件）"""
        try:
            if len(file_paths) != 1:
                return False, "GZIP只支持单文件压缩"

            file_path = file_paths[0]

            # 读取文件内容
            with open(file_path, "rb") as f_in:
                content = f_in.read()

            # 使用zlib进行预压缩以提高压缩率
            import zlib

            compressed_content = zlib.compress(content, level=compression_level)

            # 写入gzip格式
            with gzip.open(output_path, "wb", compresslevel=compression_level) as f_out:
                f_out.write(compressed_content)

            return True, "GZIP压缩成功"
        except Exception as e:
            return False, f"GZIP压缩失败: {str(e)}"

    def compress_with_bzip2(self, file_paths: List[str], output_path: str, compression_level: int = 9) -> Tuple[bool, str]:
        """使用BZIP2压缩（单文件）"""
        try:
            if len(file_paths) != 1:
                return False, "BZIP2只支持单文件压缩"

            file_path = file_paths[0]

            # 读取文件内容
            with open(file_path, "rb") as f_in:
                content = f_in.read()

            # 使用bz2进行压缩
            compressed_content = bz2.compress(content, compresslevel=compression_level)

            # 写入文件
            with open(output_path, "wb") as f_out:
                f_out.write(compressed_content)

            return True, "BZIP2压缩成功"
        except Exception as e:
            return False, f"BZIP2压缩失败: {str(e)}"

    def compress_with_xz(self, file_paths: List[str], output_path: str, compression_level: int = 6) -> Tuple[bool, str]:
        """使用XZ压缩（单文件）"""
        try:
            if len(file_paths) != 1:
                return False, "XZ只支持单文件压缩"

            file_path = file_paths[0]

            # 读取文件内容
            with open(file_path, "rb") as f_in:
                content = f_in.read()

            # 使用lzma进行压缩
            compressed_content = lzma.compress(content, preset=compression_level, format=lzma.FORMAT_XZ)

            # 写入文件
            with open(output_path, "wb") as f_out:
                f_out.write(compressed_content)

            return True, "XZ压缩成功"
        except Exception as e:
            return False, f"XZ压缩失败: {str(e)}"

    def compress_with_7z(self, file_paths: List[str], output_path: str, compression_level: int = 5) -> Tuple[bool, str]:
        """使用7Z压缩"""
        try:
            # 检查系统是否安装了7zip
            import subprocess

            # 尝试不同的7z命令
            sevenz_commands = ["7z", "7za", "7zr"]
            sevenz_cmd = None

            for cmd in sevenz_commands:
                try:
                    result = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        sevenz_cmd = cmd
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    continue

            if not sevenz_cmd:
                # 如果没有7zip，使用Python的zipfile作为替代
                return self.compress_with_zip(file_paths, output_path, compression_level, True)

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()

            # 准备7z命令
            cmd = [sevenz_cmd, "a", "-t7z", f"-mx{compression_level}", output_path] + file_paths

            # 执行压缩
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir, timeout=300)  # 5分钟超时

            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)

            if result.returncode == 0:
                return True, "7Z压缩成功"
            else:
                # 如果7z失败，回退到zip
                return self.compress_with_zip(file_paths, output_path, compression_level, True)

        except subprocess.TimeoutExpired:
            return self.compress_with_zip(file_paths, output_path, compression_level, True)
        except Exception:
            return self.compress_with_zip(file_paths, output_path, compression_level, True)

    def compress_with_tar_gz(self, file_paths: List[str], output_path: str, compression_level: int = 9) -> Tuple[bool, str]:
        """使用TAR+GZ压缩"""
        try:
            # 创建临时tar文件
            temp_tar = output_path.replace(".tar.gz", ".tar")

            # 创建tar文件
            with tarfile.open(temp_tar, "w") as tar:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        tar.add(file_path, arcname=os.path.basename(file_path))

            # 使用gzip压缩tar文件
            with open(temp_tar, "rb") as f_in:
                with gzip.open(output_path, "wb", compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 删除临时tar文件
            os.remove(temp_tar)

            return True, "TAR+GZ压缩成功"
        except Exception as e:
            return False, f"TAR+GZ压缩失败: {str(e)}"

    def compress_files(
        self,
        file_paths: List[str],
        output_name: str = None,
        compression_method: str = "auto",
        compression_level: int = 9,
        include_paths: bool = True,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        压缩文件

        Args:
            file_paths: 文件路径列表
            output_name: 输出文件名
            compression_method: 压缩方法 ('auto', 'zip', 'gz', 'bz2', 'xz', 'tar.gz')
            compression_level: 压缩级别
            include_paths: 是否包含路径结构（仅ZIP）

        Returns:
            (success, message, output_path)
        """
        try:
            if not file_paths:
                return False, "没有提供文件路径", None

            # 验证文件存在
            valid_files = []
            for file_path in file_paths:
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    valid_files.append(file_path)

            if not valid_files:
                return False, "没有有效的文件", None

            # 自动选择压缩方法
            if compression_method == "auto":
                compression_method = self._get_optimal_compression_method(valid_files)

            # 生成输出文件名
            if not output_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if compression_method == "zip":
                    output_name = f"compressed_{timestamp}.zip"
                elif compression_method == "gz":
                    output_name = f"compressed_{timestamp}.gz"
                elif compression_method == "bz2":
                    output_name = f"compressed_{timestamp}.bz2"
                elif compression_method == "xz":
                    output_name = f"compressed_{timestamp}.xz"
                elif compression_method == "7z":
                    output_name = f"compressed_{timestamp}.7z"
                elif compression_method == "tar.gz":
                    output_name = f"compressed_{timestamp}.tar.gz"

            # 确保文件扩展名正确
            if not output_name.endswith(f".{compression_method}"):
                if compression_method == "tar.gz":
                    if not output_name.endswith(".tar.gz"):
                        output_name += ".tar.gz"
                else:
                    output_name += f".{compression_method}"

            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, output_name)

            # 执行压缩
            if compression_method == "zip":
                success, message = self.compress_with_zip(valid_files, output_path, compression_level, include_paths)
            elif compression_method == "gz":
                success, message = self.compress_with_gzip(valid_files, output_path, compression_level)
            elif compression_method == "bz2":
                success, message = self.compress_with_bzip2(valid_files, output_path, compression_level)
            elif compression_method == "xz":
                success, message = self.compress_with_xz(valid_files, output_path, compression_level)
            elif compression_method == "7z":
                success, message = self.compress_with_7z(valid_files, output_path, compression_level)
            elif compression_method == "tar.gz":
                success, message = self.compress_with_tar_gz(valid_files, output_path, compression_level)
            else:
                return False, f"不支持的压缩方法: {compression_method}", None

            if success and os.path.exists(output_path):
                # 计算压缩效果
                original_size = sum(os.path.getsize(f) for f in valid_files)
                compressed_size = os.path.getsize(output_path)

                # 确保压缩率计算正确
                if original_size > 0:
                    compression_ratio = (1 - compressed_size / original_size) * 100
                    # 限制压缩率在合理范围内
                    compression_ratio = max(0, min(99.9, compression_ratio))
                else:
                    compression_ratio = 0

                # 保存压缩信息到临时文件，供get_compression_info使用
                info_file = output_path + ".info"
                try:
                    import json

                    compression_info = {
                        "original_size": original_size,
                        "compressed_size": compressed_size,
                        "compression_ratio": compression_ratio,
                        "compression_method": compression_method.upper(),
                        "file_count": len(valid_files),
                    }
                    with open(info_file, "w") as f:
                        json.dump(compression_info, f)
                except Exception as e:
                    logger.warning(f"保存压缩信息失败: {e}")

                message += f"，压缩率: {compression_ratio:.1f}%"
                return True, message, output_path
            else:
                return False, message, None

        except Exception as e:
            logger.error(f"压缩文件时发生错误: {str(e)}")
            return False, f"压缩失败: {str(e)}", None

    def get_compression_info(self, file_path: str) -> Dict:
        """获取压缩文件信息"""
        try:
            if not os.path.exists(file_path):
                return {"error": "文件不存在"}

            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower()

            info = {"file_size": file_size, "compression_method": "unknown", "can_extract": False}

            # 根据文件扩展名判断压缩方法
            if file_ext == ".zip":
                info["compression_method"] = "ZIP"
                info["can_extract"] = True
                try:
                    with zipfile.ZipFile(file_path, "r") as zipf:
                        file_list = zipf.namelist()
                        total_size = sum(zipf.getinfo(name).file_size for name in file_list)
                        compressed_size = sum(zipf.getinfo(name).compress_size for name in file_list)
                        # 确保压缩率计算正确
                        if total_size > 0:
                            compression_ratio = (1 - compressed_size / total_size) * 100
                            compression_ratio = max(0, min(99.9, compression_ratio))
                        else:
                            compression_ratio = 0

                        info.update(
                            {
                                "file_count": len(file_list),
                                "original_size": total_size,
                                "compressed_size": compressed_size,
                                "compression_ratio": compression_ratio,
                                "files": file_list[:10],
                            }
                        )
                except Exception as e:
                    info["error"] = str(e)

            elif file_ext == ".gz":
                info["compression_method"] = "GZIP"
                info["can_extract"] = True
                # 尝试读取压缩信息文件
                info_file = file_path + ".info"
                if os.path.exists(info_file):
                    try:
                        import json

                        with open(info_file, "r") as f:
                            compression_info = json.load(f)
                        info.update(compression_info)
                    except Exception as e:
                        logger.warning(f"读取压缩信息失败: {e}")
                        info.update(
                            {
                                "original_size": file_size,
                                "compressed_size": file_size,
                                "compression_ratio": 0.0,
                                "file_count": 1,
                            }
                        )
                else:
                    info.update(
                        {"original_size": file_size, "compressed_size": file_size, "compression_ratio": 0.0, "file_count": 1}
                    )

            elif file_ext == ".bz2":
                info["compression_method"] = "BZIP2"
                info["can_extract"] = True
                # 尝试读取压缩信息文件
                info_file = file_path + ".info"
                if os.path.exists(info_file):
                    try:
                        import json

                        with open(info_file, "r") as f:
                            compression_info = json.load(f)
                        info.update(compression_info)
                    except Exception as e:
                        logger.warning(f"读取压缩信息失败: {e}")
                        info.update(
                            {
                                "original_size": file_size,
                                "compressed_size": file_size,
                                "compression_ratio": 0.0,
                                "file_count": 1,
                            }
                        )
                else:
                    info.update(
                        {"original_size": file_size, "compressed_size": file_size, "compression_ratio": 0.0, "file_count": 1}
                    )

            elif file_ext == ".xz":
                info["compression_method"] = "XZ"
                info["can_extract"] = True
                # 尝试读取压缩信息文件
                info_file = file_path + ".info"
                if os.path.exists(info_file):
                    try:
                        import json

                        with open(info_file, "r") as f:
                            compression_info = json.load(f)
                        info.update(compression_info)
                    except Exception as e:
                        logger.warning(f"读取压缩信息失败: {e}")
                        info.update(
                            {
                                "original_size": file_size,
                                "compressed_size": file_size,
                                "compression_ratio": 0.0,
                                "file_count": 1,
                            }
                        )
                else:
                    info.update(
                        {"original_size": file_size, "compressed_size": file_size, "compression_ratio": 0.0, "file_count": 1}
                    )

            elif file_ext == ".tar.gz":
                info["compression_method"] = "TAR+GZ"
                info["can_extract"] = True
                # 尝试读取压缩信息文件
                info_file = file_path + ".info"
                if os.path.exists(info_file):
                    try:
                        import json

                        with open(info_file, "r") as f:
                            compression_info = json.load(f)
                        info.update(compression_info)
                    except Exception as e:
                        logger.warning(f"读取压缩信息失败: {e}")
                        info.update(
                            {
                                "original_size": file_size,
                                "compressed_size": file_size,
                                "compression_ratio": 0.0,
                                "file_count": 1,
                            }
                        )
                else:
                    info.update(
                        {"original_size": file_size, "compressed_size": file_size, "compression_ratio": 0.0, "file_count": 1}
                    )

            return info

        except Exception as e:
            logger.error(f"获取压缩文件信息时发生错误: {str(e)}")
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
enhanced_compression_service = EnhancedCompressionService()
