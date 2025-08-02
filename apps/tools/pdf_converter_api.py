#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转换引擎API
支持PDF与Word、图片等格式的相互转换
"""

import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("警告: PyMuPDF (fitz) 未安装，PDF转换功能将受限")
from PIL import Image
import io
import base64
from datetime import datetime
import uuid

# 配置日志
logger = logging.getLogger(__name__)

class PDFConverter:
    """PDF转换引擎核心类"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': ['.pdf'],
            'word': ['.doc', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        }
    
    def validate_file(self, file, expected_type):
        """验证文件格式"""
        if not file:
            return False, "文件不能为空"
        
        file_ext = os.path.splitext(file.name)[1].lower()
        if expected_type in self.supported_formats:
            if file_ext not in self.supported_formats[expected_type]:
                return False, f"不支持的文件格式: {file_ext}"
        
        # 检查文件大小 (限制为50MB)
        if file.size > 50 * 1024 * 1024:
            return False, "文件大小不能超过50MB"
        
        return True, "文件验证通过"
    
    def pdf_to_word(self, pdf_file):
        """PDF转Word (模拟实现)"""
        try:
            if not FITZ_AVAILABLE:
                return False, "PyMuPDF未安装，无法进行PDF转换", None
            
            # 这里应该使用实际的PDF转Word库，如pdf2docx
            # 目前返回模拟结果
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()
            
            doc.close()
            
            # 生成Word文档内容 (简化实现)
            word_content = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>转换结果</title>
            </head>
            <body>
                <h1>PDF转换结果</h1>
                <p>原始文件: {pdf_file.name}</p>
                <p>转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <div>{text_content}</div>
            </body>
            </html>
            """
            
            return True, word_content, "pdf_to_word"
            
        except Exception as e:
            logger.error(f"PDF转Word失败: {str(e)}")
            return False, f"转换失败: {str(e)}", None
    
    def word_to_pdf(self, word_file):
        """Word转PDF (模拟实现)"""
        try:
            # 这里应该使用实际的Word转PDF库
            # 目前返回模拟结果
            pdf_content = f"""
            %PDF-1.4
            1 0 obj
            <<
            /Type /Catalog
            /Pages 2 0 R
            >>
            endobj
            
            2 0 obj
            <<
            /Type /Pages
            /Kids [3 0 R]
            /Count 1
            >>
            endobj
            
            3 0 obj
            <<
            /Type /Page
            /Parent 2 0 R
            /MediaBox [0 0 612 792]
            /Contents 4 0 R
            >>
            endobj
            
            4 0 obj
            <<
            /Length 44
            >>
            stream
            BT
            /F1 12 Tf
            72 720 Td
            (Word转PDF结果) Tj
            ET
            endstream
            endobj
            
            xref
            0 5
            0000000000 65535 f 
            0000000009 00000 n 
            0000000058 00000 n 
            0000000115 00000 n 
            0000000204 00000 n 
            trailer
            <<
            /Size 5
            /Root 1 0 R
            >>
            startxref
            297
            %%EOF
            """
            
            return True, pdf_content, "word_to_pdf"
            
        except Exception as e:
            logger.error(f"Word转PDF失败: {str(e)}")
            return False, f"转换失败: {str(e)}", None
    
    def pdf_to_images(self, pdf_file, dpi=150):
        """PDF转图片"""
        try:
            if not FITZ_AVAILABLE:
                return False, "PyMuPDF未安装，无法进行PDF转换", None
            
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(dpi/72, dpi/72)  # 设置DPI
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                
                # 转换为base64
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                images.append({
                    'page': page_num + 1,
                    'data': img_base64,
                    'width': img.width,
                    'height': img.height
                })
            
            doc.close()
            return True, images, "pdf_to_images"
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {str(e)}")
            return False, f"转换失败: {str(e)}", None
    
    def images_to_pdf(self, image_files):
        """图片转PDF"""
        try:
            images = []
            
            for img_file in image_files:
                img = Image.open(img_file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            if not images:
                return False, "没有有效的图片文件", None
            
            # 创建PDF
            pdf_buffer = io.BytesIO()
            if len(images) == 1:
                images[0].save(pdf_buffer, format='PDF')
            else:
                images[0].save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])
            
            pdf_content = pdf_buffer.getvalue()
            return True, pdf_content, "images_to_pdf"
            
        except Exception as e:
            logger.error(f"图片转PDF失败: {str(e)}")
            return False, f"转换失败: {str(e)}", None

# 全局转换器实例
converter = PDFConverter()

@csrf_exempt
@require_http_methods(["POST"])
def pdf_converter_api(request):
    """PDF转换API主入口"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有上传文件'
            }, status=400)
        
        file = request.FILES['file']
        conversion_type = request.POST.get('type', '')
        
        # 验证转换类型
        valid_types = ['pdf-to-word', 'word-to-pdf', 'pdf-to-image', 'image-to-pdf']
        if conversion_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': f'不支持的转换类型: {conversion_type}'
            }, status=400)
        
        # 根据转换类型验证文件格式
        if conversion_type == 'pdf-to-word':
            is_valid, message = converter.validate_file(file, 'pdf')
        elif conversion_type == 'word-to-pdf':
            is_valid, message = converter.validate_file(file, 'word')
        elif conversion_type == 'pdf-to-image':
            is_valid, message = converter.validate_file(file, 'pdf')
        elif conversion_type == 'image-to-pdf':
            is_valid, message = converter.validate_file(file, 'image')
        else:
            is_valid, message = True, "文件验证通过"
        
        if not is_valid:
            return JsonResponse({
                'success': False,
                'error': message
            }, status=400)
        
        # 执行转换
        if conversion_type == 'pdf-to-word':
            success, result, file_type = converter.pdf_to_word(file)
        elif conversion_type == 'word-to-pdf':
            success, result, file_type = converter.word_to_pdf(file)
        elif conversion_type == 'pdf-to-image':
            success, result, file_type = converter.pdf_to_images(file)
        elif conversion_type == 'image-to-pdf':
            success, result, file_type = converter.images_to_pdf([file])
        else:
            return JsonResponse({
                'success': False,
                'error': '未知的转换类型'
            }, status=400)
        
        if not success:
            return JsonResponse({
                'success': False,
                'error': result
            }, status=500)
        
        # 保存转换结果
        output_filename = f"{uuid.uuid4()}_{conversion_type.replace('-', '_')}"
        
        if file_type == 'pdf_to_word':
            output_filename += '.html'
            file_path = default_storage.save(f'converted/{output_filename}', ContentFile(result.encode('utf-8')))
        elif file_type == 'word_to_pdf':
            output_filename += '.pdf'
            file_path = default_storage.save(f'converted/{output_filename}', ContentFile(result.encode('utf-8')))
        elif file_type == 'pdf_to_images':
            # 返回图片数据
            return JsonResponse({
                'success': True,
                'type': 'images',
                'data': result,
                'filename': f"{os.path.splitext(file.name)[0]}_converted"
            })
        elif file_type == 'images_to_pdf':
            output_filename += '.pdf'
            file_path = default_storage.save(f'converted/{output_filename}', ContentFile(result))
        else:
            return JsonResponse({
                'success': False,
                'error': '未知的文件类型'
            }, status=500)
        
        # 返回下载链接
        download_url = default_storage.url(file_path)
        
        return JsonResponse({
            'success': True,
            'type': 'file',
            'download_url': download_url,
            'filename': output_filename,
            'original_filename': file.name
        })
        
    except Exception as e:
        logger.error(f"PDF转换API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def pdf_converter_status(request):
    """获取转换状态"""
    return JsonResponse({
        'success': True,
        'status': 'ready',
        'supported_formats': converter.supported_formats
    }) 