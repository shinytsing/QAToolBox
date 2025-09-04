from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from ..models import LifeDiaryEntry, LifeStatistics
from .base import (
    BaseView,
    CachedViewMixin,
    PaginationMixin,
    SearchMixin,
    FilterMixin,
    OrderMixin,
    success_response,
    error_response,
    cache_response,
    validate_request_data,
    rate_limit,
)

logger = logging.getLogger(__name__)


@login_required
@cache_response(timeout=300)
def diary_dashboard(request):
    """日记仪表盘"""
    user = request.user

    # 获取用户日记统计
    stats = LifeDiaryEntry.get_user_diary_stats(user, days=30)

    # 获取最近的日记
    recent_entries = LifeDiaryEntry.objects.filter(user=user).order_by("-date")[:5]

    # 获取心情分布
    mood_distribution = (
        LifeDiaryEntry.objects.filter(user=user, date__gte=timezone.now().date() - timezone.timedelta(days=30))
        .values("mood")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    context = {
        "stats": stats,
        "recent_entries": recent_entries,
        "mood_distribution": mood_distribution,
    }

    return render(request, "tools/diary_dashboard.html", context)


@login_required
@cache_response(timeout=60)
def diary_list(request):
    """日记列表"""
    user = request.user
    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 20)
    search = request.GET.get("search", "")
    mood_filter = request.GET.get("mood", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    queryset = LifeDiaryEntry.objects.filter(user=user)

    # 搜索过滤
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(content__icontains=search))

    # 心情过滤
    if mood_filter:
        queryset = queryset.filter(mood=mood_filter)

    # 日期过滤
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    # 分页
    total_count = queryset.count()
    start = (int(page) - 1) * int(page_size)
    end = start + int(page_size)

    entries = list(queryset.order_by("-date")[start:end])

    return success_response(
        {
            "entries": entries,
            "pagination": {
                "page": int(page),
                "page_size": int(page_size),
                "total_count": total_count,
                "total_pages": (total_count + int(page_size) - 1) // int(page_size),
            },
        }
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["title", "content", "mood"])
@rate_limit(max_requests=10, window=3600)  # 每小时最多10篇日记
def create_diary_entry(request):
    """创建日记条目"""
    try:
        data = request.validated_data
        user = request.user

        # 检查是否已有当天的日记
        today = timezone.now().date()
        existing_entry = LifeDiaryEntry.objects.filter(user=user, date=today).first()

        if existing_entry:
            return error_response("今天已经写过日记了", status=400)

        # 创建日记条目
        entry = LifeDiaryEntry.objects.create(
            user=user,
            title=data["title"],
            content=data["content"],
            mood=data["mood"],
            mood_note=data.get("mood_note", ""),
            tags=data.get("tags", []),
            question_answers=data.get("question_answers", []),
            music_recommendation=data.get("music_recommendation", ""),
        )

        # 清除相关缓存
        cache.delete(f"diary_stats_{user.id}_30")
        cache.delete(f"diary_list_{user.id}")

        return success_response(
            {
                "entry": {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content,
                    "mood": entry.mood,
                    "date": entry.date.isoformat(),
                    "word_count": entry.get_word_count(),
                }
            },
            message="日记创建成功",
        )

    except Exception as e:
        logger.error(f"Error creating diary entry: {e}")
        return error_response("创建日记失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
@validate_request_data(required_fields=["title", "content", "mood"])
def update_diary_entry(request, entry_id):
    """更新日记条目"""
    try:
        data = request.validated_data
        user = request.user

        entry = get_object_or_404(LifeDiaryEntry, id=entry_id, user=user)

        # 更新字段
        entry.title = data["title"]
        entry.content = data["content"]
        entry.mood = data["mood"]
        entry.mood_note = data.get("mood_note", entry.mood_note)
        entry.tags = data.get("tags", entry.tags)
        entry.question_answers = data.get("question_answers", entry.question_answers)
        entry.music_recommendation = data.get("music_recommendation", entry.music_recommendation)
        entry.save()

        # 清除相关缓存
        cache.delete(f"diary_stats_{user.id}_30")
        cache.delete(f"diary_list_{user.id}")

        return success_response(
            {
                "entry": {
                    "id": entry.id,
                    "title": entry.title,
                    "content": entry.content,
                    "mood": entry.mood,
                    "date": entry.date.isoformat(),
                    "word_count": entry.get_word_count(),
                }
            },
            message="日记更新成功",
        )

    except Exception as e:
        logger.error(f"Error updating diary entry: {e}")
        return error_response("更新日记失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_diary_entry(request, entry_id):
    """删除日记条目"""
    try:
        user = request.user
        entry = get_object_or_404(LifeDiaryEntry, id=entry_id, user=user)

        entry.delete()

        # 清除相关缓存
        cache.delete(f"diary_stats_{user.id}_30")
        cache.delete(f"diary_list_{user.id}")

        return success_response(message="日记删除成功")

    except Exception as e:
        logger.error(f"Error deleting diary entry: {e}")
        return error_response("删除日记失败", status=500)


@login_required
@cache_response(timeout=300)
def diary_detail(request, entry_id):
    """日记详情"""
    user = request.user
    entry = get_object_or_404(LifeDiaryEntry, id=entry_id, user=user)

    return success_response(
        {
            "entry": {
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "mood": entry.mood,
                "mood_emoji": entry.get_mood_emoji(),
                "mood_note": entry.mood_note,
                "tags": entry.tags,
                "tags_display": entry.get_tags_display(),
                "question_answers": entry.question_answers,
                "music_recommendation": entry.music_recommendation,
                "date": entry.date.isoformat(),
                "word_count": entry.get_word_count(),
                "created_at": entry.created_at.isoformat(),
                "updated_at": entry.updated_at.isoformat(),
            }
        }
    )


@login_required
@cache_response(timeout=600)
def diary_statistics(request):
    """日记统计"""
    user = request.user
    days = int(request.GET.get("days", 30))

    stats = LifeDiaryEntry.get_user_diary_stats(user, days=days)

    return success_response(stats)


@login_required
@cache_response(timeout=300)
def diary_calendar(request):
    """日记日历视图"""
    user = request.user
    year = int(request.GET.get("year", timezone.now().year))
    month = int(request.GET.get("month", timezone.now().month))

    # 获取指定月份的日记
    entries = LifeDiaryEntry.objects.filter(user=user, date__year=year, date__month=month).values("date", "mood", "id")

    # 构建日历数据
    calendar_data = {}
    for entry in entries:
        date_str = entry["date"].isoformat()
        calendar_data[date_str] = {
            "id": entry["id"],
            "mood": entry["mood"],
            "has_entry": True,
        }

    return success_response(
        {
            "year": year,
            "month": month,
            "calendar_data": calendar_data,
        }
    )


@login_required
@cache_response(timeout=300)
def mood_analysis(request):
    """心情分析"""
    user = request.user
    days = int(request.GET.get("days", 30))

    # 获取心情分布
    mood_stats = (
        LifeDiaryEntry.objects.filter(user=user, date__gte=timezone.now().date() - timezone.timedelta(days=days))
        .values("mood")
        .annotate(count=Count("id"), avg_words=Avg("content__length"))
        .order_by("-count")
    )

    # 获取心情趋势
    mood_trend = (
        LifeDiaryEntry.objects.filter(user=user, date__gte=timezone.now().date() - timezone.timedelta(days=days))
        .values("date", "mood")
        .order_by("date")
    )

    return success_response(
        {
            "mood_stats": list(mood_stats),
            "mood_trend": list(mood_trend),
            "total_entries": sum(item["count"] for item in mood_stats),
        }
    )


class DiaryAPIView(BaseView, CachedViewMixin, PaginationMixin, SearchMixin, FilterMixin, OrderMixin):
    """日记API视图类"""

    @method_decorator(login_required)
    def get(self, request):
        """获取日记列表"""
        user = request.user

        # 获取查询参数
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        search = request.GET.get("search", "")
        mood_filter = request.GET.get("mood", "")
        date_from = request.GET.get("date_from", "")
        date_to = request.GET.get("date_to", "")
        order_by = request.GET.get("order_by", "-date")

        # 构建查询集
        queryset = LifeDiaryEntry.objects.filter(user=user)

        # 应用过滤
        filters = {}
        if mood_filter:
            filters["mood"] = mood_filter
        if date_from:
            filters["date__gte"] = date_from
        if date_to:
            filters["date__lte"] = date_to

        queryset = self.filter_queryset(queryset, filters)

        # 应用搜索
        if search:
            queryset = self.search_queryset(queryset, ["title", "content"], search)

        # 应用排序
        allowed_order_fields = ["date", "-date", "mood", "-mood", "created_at", "-created_at"]
        queryset = self.order_queryset(queryset, order_by, allowed_order_fields)

        # 应用分页
        result = self.get_paginated_data(queryset, page, page_size)

        return self.success_response(result)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """创建日记条目"""
        try:
            data = json.loads(request.body) if request.body else {}

            # 验证必需字段
            required_fields = ["title", "content", "mood"]
            for field in required_fields:
                if field not in data:
                    return self.error_response(f"缺少必需字段: {field}")

            user = request.user

            # 检查是否已有当天的日记
            today = timezone.now().date()
            existing_entry = LifeDiaryEntry.objects.filter(user=user, date=today).first()

            if existing_entry:
                return self.error_response("今天已经写过日记了")

            # 创建日记条目
            entry = LifeDiaryEntry.objects.create(
                user=user,
                title=data["title"],
                content=data["content"],
                mood=data["mood"],
                mood_note=data.get("mood_note", ""),
                tags=data.get("tags", []),
                question_answers=data.get("question_answers", []),
                music_recommendation=data.get("music_recommendation", ""),
            )

            # 清除相关缓存
            self.clear_user_cache(user.id, "diary")

            return self.success_response(
                {
                    "entry": {
                        "id": entry.id,
                        "title": entry.title,
                        "content": entry.content,
                        "mood": entry.mood,
                        "date": entry.date.isoformat(),
                        "word_count": entry.get_word_count(),
                    }
                }
            )

        except json.JSONDecodeError:
            return self.error_response("无效的JSON数据")
        except Exception as e:
            logger.error(f"Error creating diary entry: {e}")
            return self.error_response("创建日记失败")


# 批量操作视图
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def batch_delete_diary_entries(request):
    """批量删除日记条目"""
    try:
        data = json.loads(request.body) if request.body else {}
        entry_ids = data.get("entry_ids", [])

        if not entry_ids:
            return error_response("请选择要删除的日记")

        user = request.user
        deleted_count = LifeDiaryEntry.objects.filter(user=user, id__in=entry_ids).delete()[0]

        # 清除相关缓存
        cache.delete(f"diary_stats_{user.id}_30")
        cache.delete(f"diary_list_{user.id}")

        return success_response({"deleted_count": deleted_count}, message=f"成功删除 {deleted_count} 篇日记")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error batch deleting diary entries: {e}")
        return error_response("批量删除失败")


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def export_diary_entries(request):
    """导出日记条目"""
    try:
        data = json.loads(request.body) if request.body else {}
        date_from = data.get("date_from")
        date_to = data.get("date_to")
        format_type = data.get("format", "json")

        user = request.user
        queryset = LifeDiaryEntry.objects.filter(user=user)

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        entries = list(queryset.order_by("-date").values("title", "content", "mood", "date", "tags", "mood_note"))

        if format_type == "json":
            return JsonResponse(
                {
                    "entries": entries,
                    "export_info": {
                        "user": user.username,
                        "export_date": timezone.now().isoformat(),
                        "total_entries": len(entries),
                    },
                }
            )
        else:
            return error_response("不支持的导出格式")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error exporting diary entries: {e}")
        return error_response("导出失败")


# Emo情感日记相关视图
@login_required
def emo_diary(request):
    """Emo情感日记页面"""
    return render(request, "tools/emo_diary.html")


@csrf_exempt
@require_http_methods(["POST"])
def emo_diary_api(request):
    """情感日记API"""
    try:
        data = json.loads(request.body)
        action = data.get("action", "")

        if action == "save_diary":
            # 保存情感日记
            title = data.get("title", "")
            content = data.get("content", "")
            emotion = data.get("emotion", "")
            intensity = data.get("intensity", 5)
            triggers = data.get("triggers", "")
            emotion_note = data.get("emotion_note", "")

            if not title or not content:
                return JsonResponse({"success": False, "error": "请填写标题和内容"}, content_type="application/json")

            # 这里可以保存到数据库，暂时返回成功
            return JsonResponse(
                {
                    "success": True,
                    "message": "情感日记保存成功",
                    "data": {
                        "title": title,
                        "content": content,
                        "emotion": emotion,
                        "intensity": intensity,
                        "triggers": triggers,
                        "emotion_note": emotion_note,
                        "created_at": timezone.now().isoformat(),
                    },
                }
            )

        elif action == "get_statistics":
            # 获取情感统计
            return JsonResponse(
                {
                    "success": True,
                    "data": {"total_entries": 0, "happy_days": 0, "sad_days": 0, "calm_days": 0, "average_intensity": 5.0},
                },
                content_type="application/json",
            )

        elif action == "get_history":
            # 获取历史记录
            return JsonResponse({"success": True, "data": []}, content_type="application/json")

        else:
            return JsonResponse({"success": False, "error": "未知操作"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# 创意写作相关视图
@login_required
def creative_writer(request):
    """创意文案生成器页面"""
    return render(request, "tools/creative_writer.html")


@csrf_exempt
@require_http_methods(["POST"])
def creative_writer_api(request):
    """创意写作API"""
    try:
        data = json.loads(request.body)
        action = data.get("action", "")

        if action == "generate_content":
            # 生成创意内容
            prompt = data.get("prompt", "")
            style = data.get("style", "creative")
            length = data.get("length", "medium")

            if not prompt:
                return JsonResponse({"success": False, "error": "请提供写作提示"}, content_type="application/json")

            # 这里可以调用AI生成内容，暂时返回示例
            generated_content = f"基于您的提示'{prompt}'，我为您生成了{style}风格的{length}长度内容..."

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "content": generated_content,
                        "style": style,
                        "length": length,
                        "generated_at": timezone.now().isoformat(),
                    },
                }
            )

        elif action == "save_draft":
            # 保存草稿
            title = data.get("title", "")
            content = data.get("content", "")

            if not title or not content:
                return JsonResponse({"success": False, "error": "请填写标题和内容"}, content_type="application/json")

            return JsonResponse(
                {
                    "success": True,
                    "message": "草稿保存成功",
                    "data": {"title": title, "content": content, "saved_at": timezone.now().isoformat()},
                }
            )

        else:
            return JsonResponse({"success": False, "error": "未知操作"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
