# QAToolbox/apps/tools/views/food_image_views.py
"""
食物图片相关的视图函数
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_photos(request):
    """获取照片列表API - 动态扫描静态文件夹"""
    try:
        import os
        from django.conf import settings

        # 获取查询参数
        category = request.GET.get("category", "all")
        limit = int(request.GET.get("limit", 200))
        offset = int(request.GET.get("offset", 0))

        # 扫描静态文件夹中的图片文件
        # 使用STATICFILES_DIRS中的第一个目录（开发环境）
        static_base_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
        static_food_dir = os.path.join(static_base_dir, "img", "food")

        if not os.path.exists(static_food_dir):
            logger.warning(f"静态文件夹不存在: {static_food_dir}")
            return JsonResponse([], safe=False)

        # 获取所有图片文件
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        photo_files = []

        for filename in os.listdir(static_food_dir):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                # 跳过带随机后缀的文件（如 .ebe15523056a.jpg）
                # 检查文件名是否包含随机后缀（12位十六进制字符）
                if "." in filename:
                    parts = filename.split(".")
                    if len(parts) >= 3:  # 有多个点号
                        # 检查倒数第二个部分是否是随机后缀（12位十六进制字符）
                        second_last = parts[-2]
                        if len(second_last) == 12 and all(c in "0123456789abcdef" for c in second_last.lower()):
                            continue
                photo_files.append(filename)

        # 按文件名排序
        photo_files.sort()

        # 生成照片数据
        photos_data = []
        for i, photo_file in enumerate(photo_files):
            # 根据文件名推断菜系
            photo_category = "chinese"  # 默认中餐
            if "japanese" in photo_file or "ramen" in photo_file:
                photo_category = "japanese"
            elif "korean" in photo_file or "bibimbap" in photo_file or "gimbap" in photo_file:
                photo_category = "korean"
            elif "pasta" in photo_file or "pizza" in photo_file or "salad" in photo_file or "steak" in photo_file:
                photo_category = "western"
            elif "chinese" in photo_file:
                photo_category = "chinese"
            elif photo_file.startswith("uuid"):  # 用户上传的文件
                photo_category = "uploaded"

            # 生成显示名称
            if photo_file.startswith("uuid"):
                # 用户上传的文件，使用原始文件名或简化显示
                display_name = f"上传图片 {i+1}"
            else:
                display_name = photo_file.replace("_1280.jpg", "").replace("-", " ").title()

            photos_data.append(
                {
                    "id": i + 1,
                    "name": photo_file,
                    "display_name": display_name,
                    "url": f"/static/img/food/{photo_file}",
                    "category": photo_category,
                    "tags": [photo_category, "美食", "图片"],
                    "uploaded_at": (datetime.now() - timedelta(days=i + 1)).isoformat(),
                }
            )

        # 根据类别过滤
        if category != "all":
            photos_data = [photo for photo in photos_data if photo["category"] == category]

        # 分页
        total_count = len(photos_data)
        photos_page = photos_data[offset : offset + limit]

        logger.info(f"获取照片列表: 用户 {request.user.id}, 类别 {category}, 返回 {len(photos_page)} 条记录")

        return JsonResponse(photos_page, safe=False)

    except Exception as e:
        logger.error(f"获取照片列表失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取照片失败: {str(e)}"}, status=500)
