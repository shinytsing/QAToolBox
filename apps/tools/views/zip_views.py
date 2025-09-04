#!/usr/bin/env python3
"""
ZIP功能视图
支持多文件打包和单文件压缩打包
"""
import os
import json
import tempfile
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import logging
import shutil

from ..services.zip_service import zip_service
from ..services.enhanced_compression_service import enhanced_compression_service

logger = logging.getLogger(__name__)


@login_required
def zip_tool_view(request):
    """
    ZIP工具主页面
    """
    return render(
        request, "tools/zip_tool.html", {"title": "ZIP文件处理工具", "description": "支持多文件打包和单文件压缩打包"}
    )


@csrf_exempt
@require_http_methods(["POST"])
def create_zip_from_uploaded_files_api(request):
    """
    从上传的文件创建ZIP包 API
    """
    try:
        # 检查是否有上传的文件
        if "files" not in request.FILES:
            return JsonResponse({"success": False, "message": "请上传文件"})

        uploaded_files = request.FILES.getlist("files")
        if not uploaded_files:
            return JsonResponse({"success": False, "message": "请选择要打包的文件"})

        # 获取其他参数
        zip_name = request.POST.get("zip_name", "")
        compression_level = int(request.POST.get("compression_level", 6))
        include_paths = request.POST.get("include_paths", "true").lower() == "true"
        compression_method = request.POST.get("compression_method", "auto")

        # 验证压缩级别
        if not (0 <= compression_level <= 9):
            compression_level = 6

        # 创建临时目录存储上传的文件
        temp_dir = tempfile.mkdtemp()
        temp_file_paths = []

        try:
            # 保存上传的文件到临时目录
            for uploaded_file in uploaded_files:
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb+") as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                temp_file_paths.append(temp_file_path)

            # 使用增强压缩服务
            success, message, compressed_path = enhanced_compression_service.compress_files(
                file_paths=temp_file_paths,
                output_name=zip_name,
                compression_method=compression_method,
                compression_level=compression_level,
                include_paths=include_paths,
            )

            if success and compressed_path:
                # 获取压缩文件信息
                compression_info = enhanced_compression_service.get_compression_info(compressed_path)

                # 将压缩文件保存到媒体目录
                with open(compressed_path, "rb") as f:
                    file_content = f.read()

                # 生成文件名
                if not zip_name:
                    import time

                    if compression_method == "auto":
                        zip_name = f"uploaded_files_{int(time.time())}.zip"
                    else:
                        zip_name = f"uploaded_files_{int(time.time())}.{compression_method}"

                # 保存到媒体目录
                file_path = default_storage.save(f"zip_files/{zip_name}", ContentFile(file_content))

                # 清理临时文件
                enhanced_compression_service.cleanup_temp_files([compressed_path] + temp_file_paths)
                shutil.rmtree(temp_dir, ignore_errors=True)

                return JsonResponse(
                    {
                        "success": True,
                        "message": message,
                        "file_path": file_path,
                        "file_url": default_storage.url(file_path),
                        "compression_info": compression_info,
                    }
                )
            else:
                # 清理临时文件
                enhanced_compression_service.cleanup_temp_files(temp_file_paths)
                shutil.rmtree(temp_dir, ignore_errors=True)

                return JsonResponse({"success": False, "message": message})

        except Exception as e:
            # 清理临时文件
            enhanced_compression_service.cleanup_temp_files(temp_file_paths)
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    except Exception as e:
        logger.error(f"从上传文件创建压缩文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def compress_uploaded_file_api(request):
    """
    压缩上传的单个文件 API
    """
    try:
        # 检查是否有上传的文件
        if "file" not in request.FILES:
            return JsonResponse({"success": False, "message": "请上传文件"})

        uploaded_file = request.FILES["file"]
        compression_level = int(request.POST.get("compression_level", 9))
        compression_method = request.POST.get("compression_method", "auto")

        # 验证压缩级别
        if not (0 <= compression_level <= 9):
            compression_level = 9

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)

        try:
            # 保存上传的文件到临时目录
            with open(temp_file_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # 使用增强压缩服务
            success, message, compressed_path = enhanced_compression_service.compress_files(
                file_paths=[temp_file_path],
                output_name=None,  # 让服务自动生成文件名
                compression_method=compression_method,
                compression_level=compression_level,
                include_paths=False,
            )

            if success and compressed_path:
                # 获取压缩文件信息
                compression_info = enhanced_compression_service.get_compression_info(compressed_path)

                # 将压缩文件保存到媒体目录
                with open(compressed_path, "rb") as f:
                    file_content = f.read()

                # 生成文件名
                file_name = uploaded_file.name
                name_without_ext = os.path.splitext(file_name)[0]
                if compression_method == "auto":
                    zip_name = f"{name_without_ext}_compressed.zip"
                else:
                    zip_name = f"{name_without_ext}_compressed.{compression_method}"

                # 保存到媒体目录
                file_path_saved = default_storage.save(f"zip_files/{zip_name}", ContentFile(file_content))

                # 清理临时文件
                enhanced_compression_service.cleanup_temp_files([compressed_path, temp_file_path])
                shutil.rmtree(temp_dir, ignore_errors=True)

                return JsonResponse(
                    {
                        "success": True,
                        "message": message,
                        "file_path": file_path_saved,
                        "file_url": default_storage.url(file_path_saved),
                        "compression_info": compression_info,
                    }
                )
            else:
                # 清理临时文件
                enhanced_compression_service.cleanup_temp_files([temp_file_path])
                shutil.rmtree(temp_dir, ignore_errors=True)

                return JsonResponse({"success": False, "message": message})

        except Exception as e:
            # 清理临时文件
            enhanced_compression_service.cleanup_temp_files([temp_file_path])
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    except Exception as e:
        logger.error(f"压缩上传文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
# @login_required  # 暂时移除登录要求，因为音频转换器页面不需要登录
def create_zip_from_files_api(request):
    """
    从多个文件创建ZIP包 API (保留原有功能，用于音频转换器等)
    """
    try:
        data = json.loads(request.body)
        file_paths = data.get("file_paths", [])
        zip_name = data.get("zip_name", "")
        compression_level = data.get("compression_level", 6)
        include_paths = data.get("include_paths", True)

        # 验证参数
        if not file_paths:
            return JsonResponse({"success": False, "message": "请提供文件路径列表"})

        # 验证压缩级别
        if not (0 <= compression_level <= 9):
            compression_level = 6

        # 创建ZIP文件
        success, message, zip_path = zip_service.create_zip_from_files(
            file_paths=file_paths, zip_name=zip_name, compression_level=compression_level, include_paths=include_paths
        )

        if success and zip_path:
            # 获取ZIP文件信息
            zip_info = zip_service.get_zip_info(zip_path)

            # 将ZIP文件保存到媒体目录
            with open(zip_path, "rb") as f:
                file_content = f.read()

            # 生成文件名
            if not zip_name:
                import time

                zip_name = f"files_{int(time.time())}.zip"
            elif not zip_name.endswith(".zip"):
                zip_name += ".zip"

            # 保存到媒体目录
            file_path = default_storage.save(f"zip_files/{zip_name}", ContentFile(file_content))

            # 清理临时文件
            zip_service.cleanup_temp_files([zip_path])

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "file_path": file_path,
                    "file_url": default_storage.url(file_path),
                    "zip_info": zip_info,
                }
            )
        else:
            return JsonResponse({"success": False, "message": message})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"创建ZIP文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@require_http_methods(["POST"])
@login_required
def create_zip_from_directory_api(request):
    """
    从目录创建ZIP包 API
    """
    try:
        data = json.loads(request.body)
        directory_path = data.get("directory_path", "")
        zip_name = data.get("zip_name", "")
        compression_level = data.get("compression_level", 6)
        exclude_patterns = data.get("exclude_patterns", [])

        # 验证参数
        if not directory_path:
            return JsonResponse({"success": False, "message": "请提供目录路径"})

        # 验证压缩级别
        if not (0 <= compression_level <= 9):
            compression_level = 6

        # 创建ZIP文件
        success, message, zip_path = zip_service.create_zip_from_directory(
            directory_path=directory_path,
            zip_name=zip_name,
            compression_level=compression_level,
            exclude_patterns=exclude_patterns,
        )

        if success and zip_path:
            # 获取ZIP文件信息
            zip_info = zip_service.get_zip_info(zip_path)

            # 将ZIP文件保存到媒体目录
            with open(zip_path, "rb") as f:
                file_content = f.read()

            # 生成文件名
            if not zip_name:
                dir_name = os.path.basename(directory_path)
                import time

                zip_name = f"{dir_name}_{int(time.time())}.zip"
            elif not zip_name.endswith(".zip"):
                zip_name += ".zip"

            # 保存到媒体目录
            file_path = default_storage.save(f"zip_files/{zip_name}", ContentFile(file_content))

            # 清理临时文件
            zip_service.cleanup_temp_files([zip_path])

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "file_path": file_path,
                    "file_url": default_storage.url(file_path),
                    "zip_info": zip_info,
                }
            )
        else:
            return JsonResponse({"success": False, "message": message})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"从目录创建ZIP文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@require_http_methods(["POST"])
@login_required
def compress_single_file_api(request):
    """
    压缩单个文件 API
    """
    try:
        data = json.loads(request.body)
        file_path = data.get("file_path", "")
        compression_level = data.get("compression_level", 9)

        # 验证参数
        if not file_path:
            return JsonResponse({"success": False, "message": "请提供文件路径"})

        # 验证压缩级别
        if not (0 <= compression_level <= 9):
            compression_level = 9

        # 压缩文件
        success, message, zip_path = zip_service.compress_single_file(file_path=file_path, compression_level=compression_level)

        if success and zip_path:
            # 获取ZIP文件信息
            zip_info = zip_service.get_zip_info(zip_path)

            # 将ZIP文件保存到媒体目录
            with open(zip_path, "rb") as f:
                file_content = f.read()

            # 生成文件名
            file_name = os.path.basename(file_path)
            name_without_ext = os.path.splitext(file_name)[0]
            zip_name = f"{name_without_ext}_compressed.zip"

            # 保存到媒体目录
            file_path_saved = default_storage.save(f"zip_files/{zip_name}", ContentFile(file_content))

            # 清理临时文件
            zip_service.cleanup_temp_files([zip_path])

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "file_path": file_path_saved,
                    "file_url": default_storage.url(file_path_saved),
                    "zip_info": zip_info,
                }
            )
        else:
            return JsonResponse({"success": False, "message": message})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"压缩文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@require_http_methods(["POST"])
@login_required
def extract_zip_api(request):
    """
    解压ZIP文件 API
    """
    try:
        data = json.loads(request.body)
        zip_path = data.get("zip_path", "")
        extract_to = data.get("extract_to", "")

        # 验证参数
        if not zip_path:
            return JsonResponse({"success": False, "message": "请提供ZIP文件路径"})

        # 解压文件
        success, message, extract_path = zip_service.extract_zip(zip_path=zip_path, extract_to=extract_to)

        if success:
            return JsonResponse({"success": True, "message": message, "extract_path": extract_path})
        else:
            return JsonResponse({"success": False, "message": message})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"解压ZIP文件API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@require_http_methods(["POST"])
@login_required
def get_zip_info_api(request):
    """
    获取ZIP文件信息 API
    """
    try:
        data = json.loads(request.body)
        zip_path = data.get("zip_path", "")

        # 验证参数
        if not zip_path:
            return JsonResponse({"success": False, "message": "请提供ZIP文件路径"})

        # 获取ZIP文件信息
        zip_info = zip_service.get_zip_info(zip_path)

        if "error" not in zip_info:
            return JsonResponse({"success": True, "zip_info": zip_info})
        else:
            return JsonResponse({"success": False, "message": zip_info["error"]})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"获取ZIP信息API错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"服务器错误: {str(e)}"})


@login_required
def download_zip_file(request, file_path):
    """
    下载ZIP文件
    """
    try:
        # 构建完整文件路径
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if not os.path.exists(full_path):
            return JsonResponse({"success": False, "message": "文件不存在"})

        # 读取文件内容
        with open(full_path, "rb") as f:
            file_content = f.read()

        # 创建响应
        response = HttpResponse(file_content, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{os.path.basename(file_path)}"'

        return response

    except Exception as e:
        logger.error(f"下载ZIP文件错误: {str(e)}")
        return JsonResponse({"success": False, "message": f"下载失败: {str(e)}"})
