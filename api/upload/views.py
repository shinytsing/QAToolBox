import os
import uuid
import mimetypes
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from PIL import Image
import magic

from .models import FileUpload
from .serializers import FileUploadSerializer
from .utils import (
    validate_file_type, 
    validate_file_size, 
    generate_thumbnail,
    scan_file_for_viruses
)

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({
                    'success': False,
                    'message': '没有上传文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证文件类型
            if not validate_file_type(file):
                return Response({
                    'success': False,
                    'message': '不支持的文件类型'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证文件大小
            if not validate_file_size(file):
                return Response({
                    'success': False,
                    'message': '文件大小超出限制'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 扫描文件病毒
            if not scan_file_for_viruses(file):
                return Response({
                    'success': False,
                    'message': '文件可能包含恶意内容'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 生成唯一文件名
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # 保存文件
            file_path = default_storage.save(unique_filename, file)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # 获取文件信息
            file_size = file.size
            mime_type = magic.from_file(full_path, mime=True)
            
            # 创建文件记录
            file_upload = FileUpload.objects.create(
                user=request.user,
                original_name=file.name,
                file_name=unique_filename,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                upload_type=request.data.get('upload_type', 'general')
            )
            
            # 如果是图片，生成缩略图
            if mime_type.startswith('image/'):
                try:
                    thumbnail_path = generate_thumbnail(full_path, unique_filename)
                    file_upload.thumbnail_path = thumbnail_path
                    file_upload.save()
                except Exception as e:
                    print(f"生成缩略图失败: {e}")
            
            serializer = FileUploadSerializer(file_upload)
            
            return Response({
                'success': True,
                'message': '文件上传成功',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'文件上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MultipleFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            files = request.FILES.getlist('files')
            if not files:
                return Response({
                    'success': False,
                    'message': '没有上传文件'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_files = []
            failed_files = []
            
            for file in files:
                try:
                    # 验证文件
                    if not validate_file_type(file) or not validate_file_size(file):
                        failed_files.append({
                            'name': file.name,
                            'error': '文件类型或大小不符合要求'
                        })
                        continue
                    
                    # 扫描病毒
                    if not scan_file_for_viruses(file):
                        failed_files.append({
                            'name': file.name,
                            'error': '文件可能包含恶意内容'
                        })
                        continue
                    
                    # 保存文件
                    file_extension = os.path.splitext(file.name)[1]
                    unique_filename = f"{uuid.uuid4()}{file_extension}"
                    file_path = default_storage.save(unique_filename, file)
                    
                    # 创建记录
                    file_upload = FileUpload.objects.create(
                        user=request.user,
                        original_name=file.name,
                        file_name=unique_filename,
                        file_path=file_path,
                        file_size=file.size,
                        mime_type=magic.from_file(
                            os.path.join(settings.MEDIA_ROOT, file_path), 
                            mime=True
                        ),
                        upload_type=request.data.get('upload_type', 'general')
                    )
                    
                    uploaded_files.append(FileUploadSerializer(file_upload).data)
                    
                except Exception as e:
                    failed_files.append({
                        'name': file.name,
                        'error': str(e)
                    })
            
            return Response({
                'success': True,
                'message': f'上传完成，成功: {len(uploaded_files)}, 失败: {len(failed_files)}',
                'data': {
                    'uploaded_files': uploaded_files,
                    'failed_files': failed_files
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'批量上传失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_files(request):
    """获取用户文件列表"""
    try:
        files = FileUpload.objects.filter(user=request.user).order_by('-created_at')
        serializer = FileUploadSerializer(files, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取文件列表失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    """删除文件"""
    try:
        file_upload = FileUpload.objects.get(id=file_id, user=request.user)
        
        # 删除物理文件
        if default_storage.exists(file_upload.file_path):
            default_storage.delete(file_upload.file_path)
        
        # 删除缩略图
        if file_upload.thumbnail_path and default_storage.exists(file_upload.thumbnail_path):
            default_storage.delete(file_upload.thumbnail_path)
        
        # 删除数据库记录
        file_upload.delete()
        
        return Response({
            'success': True,
            'message': '文件删除成功'
        })
    except FileUpload.DoesNotExist:
        return Response({
            'success': False,
            'message': '文件不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'删除文件失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_info(request, file_id):
    """获取文件信息"""
    try:
        file_upload = FileUpload.objects.get(id=file_id, user=request.user)
        serializer = FileUploadSerializer(file_upload)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    except FileUpload.DoesNotExist:
        return Response({
            'success': False,
            'message': '文件不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取文件信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
