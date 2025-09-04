import os
import mimetypes
import logging
from django.http import FileResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def generic_file_download(request, filename):
    """通用文件下载视图"""
    try:
        # 构建文件路径 - 支持多种文件类型
        possible_paths = [
            os.path.join(settings.MEDIA_ROOT, "test_cases", filename),
            os.path.join(settings.MEDIA_ROOT, "converted", filename),
            os.path.join(settings.MEDIA_ROOT, "uploads", filename),
            os.path.join(settings.MEDIA_ROOT, filename),
        ]

        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break

        if not file_path:
            logger.warning(f"文件不存在: {filename}")
            raise Http404("文件不存在")

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 确定Content-Type
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            # 根据文件扩展名设置默认类型
            if filename.endswith(".mm"):
                content_type = "application/x-freemind"
            elif filename.endswith(".xmind"):
                content_type = "application/vnd.xmind.workbook"
            elif filename.endswith(".txt"):
                content_type = "text/plain"
            elif filename.endswith(".md"):
                content_type = "text/markdown"
            else:
                content_type = "application/octet-stream"

        # 创建文件响应
        response = FileResponse(open(file_path, "rb"), content_type=content_type)

        # 设置下载头
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = file_size

        logger.info(f"文件下载: {filename}, 大小: {file_size} bytes")

        return response

    except Http404:
        raise
    except Exception as e:
        logger.error(f"文件下载失败: {filename}, 错误: {str(e)}")
        return JsonResponse({"success": False, "error": f"文件下载失败: {str(e)}"}, status=500)
