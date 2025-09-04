"""
文件管理器 - 处理文件分片上传和图片缩略图生成
"""

import os
import hashlib
import mimetypes
from typing import List, Dict, Optional, Tuple
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import io
import uuid


class FileManager:
    """文件管理器"""

    def __init__(self):
        self.chunk_size = 1024 * 1024  # 1MB分片
        self.max_file_size = 100 * 1024 * 1024  # 100MB最大文件
        self.allowed_types = {
            "image": ["jpg", "jpeg", "png", "gif", "webp"],
            "video": ["mp4", "avi", "mov", "wmv"],
            "audio": ["mp3", "wav", "flac", "m4a"],
            "document": ["pdf", "doc", "docx", "txt"],
        }

    def get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        ext = filename.lower().split(".")[-1]

        for file_type, extensions in self.allowed_types.items():
            if ext in extensions:
                return file_type

        return "other"

    def validate_file(self, file_obj, filename: str) -> Tuple[bool, str]:
        """验证文件"""
        # 检查文件大小
        if file_obj.size > self.max_file_size:
            return False, f"文件大小超过限制 ({self.max_file_size / 1024 / 1024}MB)"

        # 检查文件类型
        file_type = self.get_file_type(filename)
        if file_type == "other":
            return False, "不支持的文件类型"

        return True, "文件验证通过"

    def generate_thumbnail(self, image_file, size: Tuple[int, int] = (200, 200)) -> Optional[bytes]:
        """生成图片缩略图"""
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式（处理RGBA图片）
                if img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # 保持宽高比缩放
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # 保存为JPEG格式
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=85, optimize=True)
                output.seek(0)

                return output.getvalue()

        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return None

    def save_file_with_thumbnail(self, file_obj, filename: str, user_id: int) -> Dict:
        """保存文件并生成缩略图"""
        try:
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            ext = filename.split(".")[-1]
            new_filename = f"{file_id}.{ext}"

            # 保存原文件
            file_path = f"chat_files/{user_id}/{new_filename}"
            saved_path = default_storage.save(file_path, file_obj)

            result = {
                "file_id": file_id,
                "original_name": filename,
                "saved_path": saved_path,
                "file_size": file_obj.size,
                "file_type": self.get_file_type(filename),
                "thumbnail_path": None,
            }

            # 如果是图片，生成缩略图
            if result["file_type"] == "image":
                thumbnail_data = self.generate_thumbnail(file_obj)
                if thumbnail_data:
                    thumbnail_filename = f"{file_id}_thumb.jpg"
                    thumbnail_path = f"chat_files/{user_id}/thumbnails/{thumbnail_filename}"

                    thumbnail_file = ContentFile(thumbnail_data)
                    saved_thumbnail_path = default_storage.save(thumbnail_path, thumbnail_file)
                    result["thumbnail_path"] = saved_thumbnail_path

            return result

        except Exception as e:
            print(f"保存文件失败: {e}")
            return None

    def split_file_into_chunks(self, file_obj) -> List[bytes]:
        """将文件分片"""
        chunks = []
        while True:
            chunk = file_obj.read(self.chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
        return chunks

    def merge_chunks(self, chunks: List[bytes]) -> bytes:
        """合并文件分片"""
        return b"".join(chunks)

    def get_file_url(self, file_path: str) -> str:
        """获取文件URL"""
        if hasattr(settings, "MEDIA_URL"):
            return f"{settings.MEDIA_URL}{file_path}"
        return f"/media/{file_path}"

    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False


# 全局文件管理器实例
file_manager = FileManager()
