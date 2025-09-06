import os
import uuid
from PIL import Image, ImageOps
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
import logging

logger = logging.getLogger(__name__)

class ImageOptimizer:
    """图片优化器"""
    
    def __init__(self):
        self.quality = 85
        self.max_width = 1920
        self.max_height = 1080
        self.thumbnail_sizes = [
            (150, 150),   # 小缩略图
            (300, 300),   # 中缩略图
            (600, 600),   # 大缩略图
        ]
    
    def optimize_image(self, image_file, output_format='JPEG', quality=None):
        """优化图片"""
        try:
            # 打开图片
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 调整大小
                img = self._resize_image(img)
                
                # 优化图片
                img = self._optimize_image(img)
                
                # 保存优化后的图片
                output = io.BytesIO()
                img.save(output, format=output_format, quality=quality or self.quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"图片优化失败: {e}")
            return None
    
    def _resize_image(self, img):
        """调整图片大小"""
        # 计算新尺寸
        width, height = img.size
        
        if width <= self.max_width and height <= self.max_height:
            return img
        
        # 按比例缩放
        ratio = min(self.max_width / width, self.max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def _optimize_image(self, img):
        """优化图片质量"""
        # 自动调整对比度和亮度
        img = ImageOps.autocontrast(img)
        
        # 锐化
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return img
    
    def generate_thumbnails(self, image_file, base_name):
        """生成多种尺寸的缩略图"""
        thumbnails = {}
        
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                for size in self.thumbnail_sizes:
                    # 生成缩略图
                    thumbnail = self._create_thumbnail(img, size)
                    
                    # 保存缩略图
                    thumbnail_name = f"{base_name}_{size[0]}x{size[1]}.jpg"
                    thumbnail_path = self._save_thumbnail(thumbnail, thumbnail_name)
                    
                    if thumbnail_path:
                        thumbnails[f"{size[0]}x{size[1]}"] = thumbnail_path
                
                return thumbnails
                
        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            return {}
    
    def _create_thumbnail(self, img, size):
        """创建缩略图"""
        # 使用thumbnail方法保持宽高比
        thumbnail = img.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        
        # 创建正方形缩略图
        if thumbnail.size != size:
            # 创建白色背景
            background = Image.new('RGB', size, (255, 255, 255))
            
            # 计算居中位置
            x = (size[0] - thumbnail.size[0]) // 2
            y = (size[1] - thumbnail.size[1]) // 2
            
            # 粘贴缩略图到背景上
            background.paste(thumbnail, (x, y))
            thumbnail = background
        
        return thumbnail
    
    def _save_thumbnail(self, thumbnail, name):
        """保存缩略图"""
        try:
            output = io.BytesIO()
            thumbnail.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # 保存到存储
            path = f"thumbnails/{name}"
            saved_path = default_storage.save(path, ContentFile(output.getvalue()))
            
            return saved_path
            
        except Exception as e:
            logger.error(f"保存缩略图失败: {e}")
            return None
    
    def compress_image(self, image_file, target_size_kb=100):
        """压缩图片到指定大小"""
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 调整大小
                img = self._resize_image(img)
                
                # 逐步降低质量直到达到目标大小
                quality = 95
                while quality > 10:
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    
                    if len(output.getvalue()) <= target_size_kb * 1024:
                        break
                    
                    quality -= 5
                
                output.seek(0)
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"压缩图片失败: {e}")
            return None
    
    def convert_format(self, image_file, target_format='JPEG'):
        """转换图片格式"""
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                output = io.BytesIO()
                img.save(output, format=target_format, quality=self.quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"转换图片格式失败: {e}")
            return None
    
    def add_watermark(self, image_file, watermark_text, position='bottom-right'):
        """添加水印"""
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 创建水印
                watermark = self._create_watermark(img.size, watermark_text)
                
                # 合并水印
                img.paste(watermark, self._get_watermark_position(img.size, position), watermark)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=self.quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"添加水印失败: {e}")
            return None
    
    def _create_watermark(self, image_size, text):
        """创建水印"""
        from PIL import ImageDraw, ImageFont
        
        # 创建透明水印
        watermark = Image.new('RGBA', image_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 设置字体
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # 绘制水印文本
        draw.text((10, 10), text, fill=(255, 255, 255, 128), font=font)
        
        return watermark
    
    def _get_watermark_position(self, image_size, position):
        """获取水印位置"""
        width, height = image_size
        
        positions = {
            'top-left': (10, 10),
            'top-right': (width - 200, 10),
            'bottom-left': (10, height - 50),
            'bottom-right': (width - 200, height - 50),
            'center': (width // 2 - 100, height // 2 - 25)
        }
        
        return positions.get(position, positions['bottom-right'])

class WebPConverter:
    """WebP转换器"""
    
    def __init__(self):
        self.quality = 80
    
    def convert_to_webp(self, image_file, quality=None):
        """转换为WebP格式"""
        try:
            with Image.open(image_file) as img:
                # 转换为RGB模式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                output = io.BytesIO()
                img.save(output, format='WebP', quality=quality or self.quality, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"转换为WebP失败: {e}")
            return None
    
    def convert_from_webp(self, image_file, target_format='JPEG'):
        """从WebP转换"""
        try:
            with Image.open(image_file) as img:
                output = io.BytesIO()
                img.save(output, format=target_format, quality=85, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            logger.error(f"从WebP转换失败: {e}")
            return None

class ImageProcessor:
    """图片处理器"""
    
    def __init__(self):
        self.optimizer = ImageOptimizer()
        self.webp_converter = WebPConverter()
    
    def process_uploaded_image(self, image_file, user_id, image_type='general'):
        """处理上传的图片"""
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(image_file.name)[1]
            unique_name = f"{uuid.uuid4()}{file_extension}"
            
            # 优化图片
            optimized_image = self.optimizer.optimize_image(image_file)
            if not optimized_image:
                return None
            
            # 保存原图
            original_path = f"images/{user_id}/{image_type}/{unique_name}"
            saved_path = default_storage.save(original_path, optimized_image)
            
            # 生成缩略图
            base_name = os.path.splitext(unique_name)[0]
            thumbnails = self.optimizer.generate_thumbnails(optimized_image, base_name)
            
            # 生成WebP版本
            webp_image = self.webp_converter.convert_to_webp(optimized_image)
            if webp_image:
                webp_path = f"images/{user_id}/{image_type}/{base_name}.webp"
                default_storage.save(webp_path, webp_image)
            
            return {
                'original_path': saved_path,
                'thumbnails': thumbnails,
                'webp_path': webp_path if webp_image else None
            }
            
        except Exception as e:
            logger.error(f"处理上传图片失败: {e}")
            return None
    
    def get_optimized_image_url(self, image_path, size=None, format='JPEG'):
        """获取优化后的图片URL"""
        try:
            if not default_storage.exists(image_path):
                return None
            
            # 如果指定了尺寸，返回缩略图
            if size:
                thumbnail_path = f"thumbnails/{os.path.splitext(os.path.basename(image_path))[0]}_{size[0]}x{size[1]}.jpg"
                if default_storage.exists(thumbnail_path):
                    return default_storage.url(thumbnail_path)
            
            # 返回原图
            return default_storage.url(image_path)
            
        except Exception as e:
            logger.error(f"获取优化图片URL失败: {e}")
            return None

# 全局图片处理器实例
image_processor = ImageProcessor()
