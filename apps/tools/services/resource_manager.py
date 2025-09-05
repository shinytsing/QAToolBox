import asyncio
import hashlib
import io
import logging
import mimetypes
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import aiofiles
from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class FileChunk:
    """文件分片信息"""

    chunk_id: str
    file_id: str
    chunk_number: int
    total_chunks: int
    chunk_size: int
    data: bytes
    checksum: str


@dataclass
class FileInfo:
    """文件信息"""

    file_id: str
    filename: str
    size: int
    mime_type: str
    checksum: str
    chunks: List[FileChunk]
    uploaded_chunks: set
    is_complete: bool = False


class ThumbnailGenerator:
    """缩略图生成器"""

    def __init__(self, sizes: Dict[str, Tuple[int, int]] = None):
        self.sizes = sizes or {"small": (150, 150), "medium": (300, 300), "large": (600, 600)}

    def generate_thumbnails(self, image_path: str, output_dir: str) -> Dict[str, str]:
        """生成多种尺寸的缩略图"""
        try:
            with Image.open(image_path) as img:
                thumbnails = {}

                for size_name, (width, height) in self.sizes.items():
                    # 保持宽高比
                    img_copy = img.copy()
                    img_copy.thumbnail((width, height), Image.Resampling.LANCZOS)

                    # 保存缩略图
                    thumbnail_path = os.path.join(output_dir, f"{size_name}_{os.path.basename(image_path)}")
                    img_copy.save(thumbnail_path, quality=85, optimize=True)
                    thumbnails[size_name] = thumbnail_path

                return thumbnails

        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            return {}

    def generate_thumbnail_from_bytes(self, image_data: bytes, filename: str, size: Tuple[int, int]) -> Optional[bytes]:
        """从字节数据生成缩略图"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)

                # 转换为字节
                output = io.BytesIO()
                img_copy.save(output, format=img.format or "JPEG", quality=85, optimize=True)
                return output.getvalue()

        except Exception as e:
            logger.error(f"从字节生成缩略图失败: {e}")
            return None


class ChunkedFileManager:
    """分片文件管理器"""

    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB分片
        self.chunk_size = chunk_size
        self.temp_dir = Path(settings.MEDIA_ROOT) / "temp" / "chunks"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # 文件信息缓存
        self.file_info_cache: Dict[str, FileInfo] = {}

    def create_file_info(self, filename: str, total_size: int, mime_type: str = None) -> FileInfo:
        """创建文件信息"""
        file_id = self._generate_file_id(filename, total_size)

        if mime_type is None:
            mime_type, _ = mimetypes.guess_type(filename)

        total_chunks = (total_size + self.chunk_size - 1) // self.chunk_size

        file_info = FileInfo(
            file_id=file_id,
            filename=filename,
            size=total_size,
            mime_type=mime_type or "application/octet-stream",
            checksum="",
            chunks=[],
            uploaded_chunks=set(),
        )

        self.file_info_cache[file_id] = file_info
        return file_info

    async def save_chunk(self, chunk: FileChunk) -> bool:
        """保存文件分片"""
        try:
            # 验证分片数据
            if not self._verify_chunk_data(chunk):
                return False

            # 保存分片到临时文件
            chunk_path = self.temp_dir / f"{chunk.file_id}_{chunk.chunk_number}"

            async with aiofiles.open(chunk_path, "wb") as f:
                await f.write(chunk.data)

            # 更新文件信息
            if chunk.file_id in self.file_info_cache:
                file_info = self.file_info_cache[chunk.file_id]
                file_info.uploaded_chunks.add(chunk.chunk_number)

                # 检查是否所有分片都已上传
                if len(file_info.uploaded_chunks) == chunk.total_chunks:
                    await self._assemble_file(chunk.file_id)

            return True

        except Exception as e:
            logger.error(f"保存分片失败: {e}")
            return False

    async def _assemble_file(self, file_id: str) -> bool:
        """组装文件"""
        try:
            file_info = self.file_info_cache[file_id]

            # 创建最终文件路径
            final_path = Path(settings.MEDIA_ROOT) / "uploads" / file_info.filename
            final_path.parent.mkdir(parents=True, exist_ok=True)

            # 按顺序读取并写入分片
            async with aiofiles.open(final_path, "wb") as final_file:
                for chunk_num in range(len(file_info.uploaded_chunks)):
                    chunk_path = self.temp_dir / f"{file_id}_{chunk_num}"

                    if chunk_path.exists():
                        async with aiofiles.open(chunk_path, "rb") as chunk_file:
                            chunk_data = await chunk_file.read()
                            await final_file.write(chunk_data)

                    # 删除分片文件
                    chunk_path.unlink(missing_ok=True)

            # 计算最终文件校验和
            file_info.checksum = await self._calculate_file_checksum(final_path)
            file_info.is_complete = True

            logger.info(f"文件组装完成: {file_info.filename}")
            return True

        except Exception as e:
            logger.error(f"文件组装失败: {e}")
            return False

    def _verify_chunk_data(self, chunk: FileChunk) -> bool:
        """验证分片数据"""
        # 计算分片校验和
        calculated_checksum = hashlib.md5(chunk.data, usedforsecurity=False).hexdigest()
        return calculated_checksum == chunk.checksum

    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        hash_md5 = hashlib.md5(usedforsecurity=False)

        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def _generate_file_id(self, filename: str, size: int) -> str:
        """生成文件ID"""
        content = f"{filename}_{size}_{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_file_info(self, file_id: str) -> Optional[FileInfo]:
        """获取文件信息"""
        return self.file_info_cache.get(file_id)

    def cleanup_temp_files(self, file_id: str = None):
        """清理临时文件"""
        if file_id:
            # 清理特定文件的临时分片
            for chunk_file in self.temp_dir.glob(f"{file_id}_*"):
                chunk_file.unlink(missing_ok=True)
        else:
            # 清理所有临时文件
            for chunk_file in self.temp_dir.glob("*"):
                chunk_file.unlink(missing_ok=True)


class ResourceManager:
    """资源管理器主类"""

    def __init__(self):
        self.thumbnail_generator = ThumbnailGenerator()
        self.chunked_file_manager = ChunkedFileManager()

        # 支持的图片格式
        self.supported_image_formats = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

        # 文件大小限制
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.max_image_size = 10 * 1024 * 1024  # 10MB

    async def upload_file(self, file_data: bytes, filename: str, generate_thumbnails: bool = True) -> Dict:
        """上传文件"""
        try:
            # 检查文件大小
            if len(file_data) > self.max_file_size:
                return {"success": False, "error": f"文件大小超过限制 ({self.max_file_size / 1024 / 1024}MB)"}

            # 检查文件类型
            mime_type, _ = mimetypes.guess_type(filename)

            # 如果是图片文件，生成缩略图
            thumbnails = {}
            if generate_thumbnails and self._is_image_file(filename):
                if len(file_data) > self.max_image_size:
                    return {"success": False, "error": f"图片大小超过限制 ({self.max_image_size / 1024 / 1024}MB)"}

                thumbnails = await self._generate_thumbnails_from_bytes(file_data, filename)

            # 保存文件
            file_path = Path(settings.MEDIA_ROOT) / "uploads" / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data)

            file_url = f"/media/uploads/{filename}"

            return {
                "success": True,
                "filename": filename,
                "size": len(file_data),
                "mime_type": mime_type,
                "url": file_url,
                "thumbnails": thumbnails,
            }

        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return {"success": False, "error": str(e)}

    async def upload_file_chunked(self, file_info: FileInfo, chunk: FileChunk) -> Dict:
        """分片上传文件"""
        try:
            success = await self.chunked_file_manager.save_chunk(chunk)

            if success:
                return {
                    "success": True,
                    "chunk_number": chunk.chunk_number,
                    "total_chunks": chunk.total_chunks,
                    "is_complete": file_info.is_complete,
                }
            else:
                return {"success": False, "error": "分片保存失败"}

        except Exception as e:
            logger.error(f"分片上传失败: {e}")
            return {"success": False, "error": str(e)}

    async def download_file(self, filename: str) -> Optional[bytes]:
        """下载文件"""
        try:
            file_path = Path(settings.MEDIA_ROOT) / "uploads" / filename

            if file_path.exists():
                async with aiofiles.open(file_path, "rb") as f:
                    return await f.read()

            return None

        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return None

    async def delete_file(self, filename: str) -> bool:
        """删除文件"""
        try:
            file_path = Path(settings.MEDIA_ROOT) / "uploads" / filename

            if file_path.exists():
                file_path.unlink()
                return True

            return False

        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False

    async def _generate_thumbnails_from_bytes(self, image_data: bytes, filename: str) -> Dict[str, str]:
        """从字节数据生成缩略图"""
        try:
            thumbnails = {}

            for size_name, size in self.thumbnail_generator.sizes.items():
                thumbnail_data = self.thumbnail_generator.generate_thumbnail_from_bytes(image_data, filename, size)

                if thumbnail_data:
                    # 保存缩略图
                    thumbnail_filename = f"{size_name}_{filename}"
                    thumbnail_path = Path(settings.MEDIA_ROOT) / "thumbnails" / thumbnail_filename
                    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

                    async with aiofiles.open(thumbnail_path, "wb") as f:
                        await f.write(thumbnail_data)

                    thumbnails[size_name] = f"/media/thumbnails/{thumbnail_filename}"

            return thumbnails

        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            return {}

    def _is_image_file(self, filename: str) -> bool:
        """检查是否为图片文件"""
        ext = Path(filename).suffix.lower()
        return ext in self.supported_image_formats

    def get_file_info(self, file_id: str) -> Optional[FileInfo]:
        """获取文件信息"""
        return self.chunked_file_manager.get_file_info(file_id)

    def cleanup_temp_files(self, file_id: str = None):
        """清理临时文件"""
        self.chunked_file_manager.cleanup_temp_files(file_id)


# 全局资源管理器实例
resource_manager = ResourceManager()
