import os
import uuid
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
import magic

# 允许的文件类型
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
ALLOWED_DOCUMENT_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv'
]
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv']
ALLOWED_AUDIO_TYPES = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a']

ALLOWED_TYPES = ALLOWED_IMAGE_TYPES + ALLOWED_DOCUMENT_TYPES + ALLOWED_VIDEO_TYPES + ALLOWED_AUDIO_TYPES

# 文件大小限制 (字节)
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file_type(file):
    """验证文件类型"""
    try:
        # 使用python-magic检测真实文件类型
        file_content = file.read(1024)  # 读取前1KB
        file.seek(0)  # 重置文件指针
        mime_type = magic.from_buffer(file_content, mime=True)
        
        return mime_type in ALLOWED_TYPES
    except Exception:
        # 如果检测失败，使用Django的MIME类型检测
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file.name)
        return mime_type in ALLOWED_TYPES

def validate_file_size(file):
    """验证文件大小"""
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    
    if mime_type in ALLOWED_IMAGE_TYPES:
        return file.size <= MAX_IMAGE_SIZE
    elif mime_type in ALLOWED_DOCUMENT_TYPES:
        return file.size <= MAX_DOCUMENT_SIZE
    else:
        return file.size <= MAX_FILE_SIZE

def scan_file_for_viruses(file):
    """扫描文件病毒 (简单实现)"""
    try:
        # 这里应该集成真实的病毒扫描服务
        # 目前只是简单的文件头检查
        file_content = file.read(1024)
        file.seek(0)
        
        # 检查是否包含可疑的脚本标签
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'<iframe',
            b'<object',
            b'<embed'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in file_content.lower():
                return False
        
        return True
    except Exception:
        return False

def generate_thumbnail(file_path, filename):
    """生成图片缩略图"""
    try:
        # 打开图片
        with Image.open(file_path) as img:
            # 转换为RGB模式
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # 计算缩略图尺寸
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 生成缩略图文件名
            name, ext = os.path.splitext(filename)
            thumbnail_filename = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join('thumbnails', thumbnail_filename)
            
            # 保存缩略图
            thumbnail_full_path = os.path.join(settings.MEDIA_ROOT, thumbnail_path)
            os.makedirs(os.path.dirname(thumbnail_full_path), exist_ok=True)
            
            img.save(thumbnail_full_path, 'JPEG', quality=85)
            
            return thumbnail_path
            
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return None

def generate_share_code():
    """生成分享码"""
    return str(uuid.uuid4()).replace('-', '')[:16]

def get_file_extension(filename):
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def is_image_file(mime_type):
    """判断是否为图片文件"""
    return mime_type in ALLOWED_IMAGE_TYPES

def is_document_file(mime_type):
    """判断是否为文档文件"""
    return mime_type in ALLOWED_DOCUMENT_TYPES

def is_video_file(mime_type):
    """判断是否为视频文件"""
    return mime_type in ALLOWED_VIDEO_TYPES

def is_audio_file(mime_type):
    """判断是否为音频文件"""
    return mime_type in ALLOWED_AUDIO_TYPES

def get_file_category(mime_type):
    """获取文件分类"""
    if is_image_file(mime_type):
        return 'image'
    elif is_document_file(mime_type):
        return 'document'
    elif is_video_file(mime_type):
        return 'video'
    elif is_audio_file(mime_type):
        return 'audio'
    else:
        return 'other'

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
