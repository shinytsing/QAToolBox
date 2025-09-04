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
from django.core.files.storage import default_storage
from django.db import connection
import json
import logging
import os
from datetime import datetime, timedelta

from ..models.diary_models import LifeDiaryEntry, DiaryAchievement, DiaryTemplate, DailyQuestion
from .base import BaseView

logger = logging.getLogger(__name__)


def create_diary_entry_safe(user, date, title, content, mood, entry_type, **kwargs):
    """安全创建日记条目，避免字段问题"""
    try:
        # 检查是否已存在
        existing = LifeDiaryEntry.objects.filter(user=user, date=date).first()
        if existing:
            # 更新现有记录
            if content:
                existing.content = content
            if mood:
                existing.mood = mood
            existing.entry_type = entry_type
            existing.save()
            return existing, False

        # 使用原生SQL插入，避免ORM字段验证问题
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tools_lifediaryentry 
                (date, title, content, mood, entry_type, user_id, created_at, updated_at,
                 mood_note, tags, music_recommendation, question_answers, voice_text,
                 template_name, question_answer, daily_question, hobby_category,
                 word_count, reading_time, is_private, auto_saved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                [
                    date,
                    title,
                    content,
                    mood,
                    entry_type,
                    user.id,
                    timezone.now(),
                    timezone.now(),
                    "",
                    "[]",
                    "",
                    "[]",
                    "",
                    "",
                    "{}",
                    "",
                    "",
                    len(content) if content else 0,
                    1,
                    False,
                    True,
                ],
            )

            # 获取新创建的记录
            entry_id = cursor.lastrowid
            entry = LifeDiaryEntry.objects.get(id=entry_id)
            return entry, True

    except Exception as e:
        logger.error(f"Error creating diary entry: {e}")
        raise e


# @login_required  # 临时注释掉登录要求以便测试
def simple_diary_home(request):
    """简单生活日记主页"""
    # 临时处理匿名用户
    if request.user.is_authenticated:
        user = request.user
    else:
        # 创建匿名用户上下文
        user = None

    # 获取今天的日记
    today = timezone.now().date()
    if user:
        today_entry = LifeDiaryEntry.objects.filter(user=user, date=today).first()
        # 获取最近的成就
        recent_achievements = DiaryAchievement.objects.filter(user=user, is_completed=True).order_by("-completed_at")[:3]
        # 获取连续记录天数
        streak_days = LifeDiaryEntry.get_writing_streak(user)
        # 获取本月记录统计
        this_month = timezone.now().replace(day=1).date()
        month_entries_count = LifeDiaryEntry.objects.filter(user=user, date__gte=this_month).count()
    else:
        today_entry = None
        recent_achievements = []
        streak_days = 0
        month_entries_count = 0

    # 获取今日问题
    daily_question = LifeDiaryEntry.get_random_question()

    context = {
        "today_entry": today_entry,
        "daily_question": daily_question,
        "recent_achievements": recent_achievements,
        "streak_days": streak_days,
        "month_entries_count": month_entries_count,
        "today": today.isoformat(),
    }

    return render(request, "tools/simple_diary_home.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def diary_quick_save(request):
    """快速保存日记（支持实时保存）"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "请先登录"})

    try:
        data = json.loads(request.body)
        content = data.get("content", "").strip()
        mood = data.get("mood", "")
        entry_type = data.get("entry_type", "quick")

        if not content and not mood:
            return JsonResponse({"success": False, "error": "请输入内容或选择心情"})

        user = request.user
        today = timezone.now().date()

        # 使用安全创建函数
        entry, created = create_diary_entry_safe(
            user=user, date=today, title="", content=content, mood=mood, entry_type=entry_type
        )

        if not created:
            # 更新现有条目
            if content:
                entry.content = content
            if mood:
                entry.mood = mood
            entry.entry_type = entry_type
            entry.auto_saved = True
            entry.save()

        # 更新成就进度
        update_user_achievements(user)

        return JsonResponse(
            {
                "success": True,
                "message": "保存成功",
                "entry_id": entry.id,
                "word_count": entry.word_count,
                "created": created,
            }
        )

    except Exception as e:
        logger.error(f"Quick save error: {e}")
        return JsonResponse({"success": False, "error": "保存失败"})


@csrf_exempt
@require_http_methods(["POST"])
def diary_mood_save(request):
    """快速保存心情"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "请先登录"})

    try:
        data = json.loads(request.body)
        mood = data.get("mood", "")

        if not mood:
            return JsonResponse({"success": False, "error": "请选择心情"})

        user = request.user
        today = timezone.now().date()

        # 使用安全创建函数
        entry, created = create_diary_entry_safe(
            user=user, date=today, title=f"今天心情：{mood}", content="", mood=mood, entry_type="quick"
        )

        if not created:
            entry.mood = mood
            if not entry.title:
                entry.title = f"今天心情：{mood}"
            entry.save()

        # 更新成就进度
        update_user_achievements(user)

        return JsonResponse(
            {
                "success": True,
                "message": f"心情记录成功：{mood}",
                "entry_id": entry.id,
            }
        )

    except Exception as e:
        logger.error(f"Mood save error: {e}")
        return JsonResponse({"success": False, "error": "保存失败"})


@csrf_exempt
@require_http_methods(["POST"])
def diary_image_upload(request):
    """上传图片日记"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "请先登录"})

    try:
        if "image" not in request.FILES:
            return JsonResponse({"success": False, "error": "请上传图片"})

        image_file = request.FILES["image"]
        description = request.POST.get("description", "")
        mood = request.POST.get("mood", "😊")

        user = request.user
        today = timezone.now().date()

        # 检查是否已存在今天的记录
        existing = LifeDiaryEntry.objects.filter(user=user, date=today).first()
        if existing:
            # 更新现有记录
            existing.image = image_file
            if description:
                existing.content = description
            if mood:
                existing.mood = mood
            existing.entry_type = "image"
            existing.save()
            entry = existing
            created = False
        else:
            # 使用安全创建函数
            entry, created = create_diary_entry_safe(
                user=user, date=today, title="📸 分享了一张图片", content=description, mood=mood, entry_type="image"
            )
            # 单独设置图片
            entry.image = image_file
            entry.save()

        # 更新成就进度
        update_user_achievements(user)

        return JsonResponse(
            {
                "success": True,
                "message": "图片上传成功",
                "entry_id": entry.id,
                "image_url": entry.image.url if entry.image else "",
            }
        )

    except Exception as e:
        logger.error(f"Image upload error: {e}")
        return JsonResponse({"success": False, "error": "上传失败"})


@csrf_exempt
@require_http_methods(["POST"])
def diary_template_save(request):
    """使用模板保存日记"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "请先登录"})

    try:
        data = json.loads(request.body)
        template_id = data.get("template_id")
        answers = data.get("answers", {})
        mood = data.get("mood", "😊")

        if not template_id:
            return JsonResponse({"success": False, "error": "请选择模板"})

        template = get_object_or_404(DiaryTemplate, id=template_id)

        user = request.user
        today = timezone.now().date()

        # 构建内容
        content_parts = []
        for key, value in answers.items():
            if value.strip():
                content_parts.append(f"{key}: {value}")

        content = "\n".join(content_parts)

        # 创建模板日记条目
        entry, created = LifeDiaryEntry.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                "title": f"📝 {template.name}",
                "content": content,
                "mood": mood,
                "entry_type": "template",
                "template_name": template.name,
                "question_answer": answers,
                "auto_saved": True,
                "voice_text": "",
                "daily_question": "",
                "hobby_category": "",
                "is_private": False,
            },
        )

        if not created:
            entry.content = content
            entry.mood = mood
            entry.template_name = template.name
            entry.question_answer = answers
            entry.save()

        # 增加模板使用次数
        template.increment_usage()

        # 更新成就进度
        update_user_achievements(user)

        return JsonResponse(
            {
                "success": True,
                "message": f"使用 {template.name} 模板记录成功",
                "entry_id": entry.id,
            }
        )

    except Exception as e:
        logger.error(f"Template save error: {e}")
        return JsonResponse({"success": False, "error": "保存失败"})


@login_required
def diary_calendar_view(request):
    """日记日历视图"""
    user = request.user
    year = int(request.GET.get("year", timezone.now().year))
    month = int(request.GET.get("month", timezone.now().month))

    # 获取该月的所有日记
    entries = (
        LifeDiaryEntry.objects.filter(user=user, date__year=year, date__month=month)
        .select_related()
        .values("date", "mood", "entry_type", "word_count", "id")
    )

    # 构建日历数据
    calendar_data = {}
    for entry in entries:
        date_key = entry["date"].strftime("%Y-%m-%d")
        calendar_data[date_key] = {
            "id": entry["id"],
            "mood": entry["mood"],
            "entry_type": entry["entry_type"],
            "word_count": entry["word_count"],
            "has_entry": True,
        }

    return JsonResponse(
        {
            "success": True,
            "year": year,
            "month": month,
            "calendar_data": calendar_data,
        }
    )


@login_required
def diary_achievements(request):
    """获取用户成就"""
    user = request.user

    # 确保用户有默认成就
    DiaryAchievement.create_default_achievements(user)

    achievements = DiaryAchievement.objects.filter(user=user)

    achievements_data = []
    for achievement in achievements:
        achievements_data.append(
            {
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
                "progress": achievement.get_progress_percentage(),
                "current_value": achievement.current_value,
                "target_value": achievement.target_value,
                "is_completed": achievement.is_completed,
                "completed_at": achievement.completed_at.isoformat() if achievement.completed_at else None,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "achievements": achievements_data,
        }
    )


# @login_required  # 临时注释掉登录要求以便测试
def diary_templates(request):
    """获取日记模板"""
    # 临时处理匿名用户
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    templates = DiaryTemplate.objects.filter(is_active=True)

    templates_data = []
    for template in templates:
        templates_data.append(
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "content": template.content,
                "category": template.category,
                "icon": template.icon,
                "usage_count": template.usage_count,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "templates": templates_data,
        }
    )


@login_required
def diary_history_timeline(request):
    """时间轴历史视图"""
    user = request.user
    page = int(request.GET.get("page", 1))
    page_size = 20

    entries = LifeDiaryEntry.objects.filter(user=user).order_by("-date", "-created_at")

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    page_entries = entries[start:end]

    entries_data = []
    for entry in page_entries:
        # 检查是否有"那年今日"
        same_day_last_year = None
        last_year_date = entry.date.replace(year=entry.date.year - 1)
        last_year_entry = LifeDiaryEntry.objects.filter(user=user, date=last_year_date).first()

        if last_year_entry:
            same_day_last_year = {
                "content": last_year_entry.get_entry_summary(),
                "mood": last_year_entry.mood,
                "year": last_year_date.year,
            }

        entries_data.append(
            {
                "id": entry.id,
                "date": entry.date.isoformat(),
                "title": entry.title,
                "summary": entry.get_entry_summary(),
                "mood": entry.mood,
                "entry_type": entry.entry_type,
                "word_count": entry.word_count,
                "image_url": entry.image.url if entry.image else None,
                "same_day_last_year": same_day_last_year,
            }
        )

    return JsonResponse(
        {
            "success": True,
            "entries": entries_data,
            "has_more": end < entries.count(),
            "page": page,
        }
    )


def update_user_achievements(user):
    """更新用户成就进度"""
    try:
        # 确保用户有默认成就
        DiaryAchievement.create_default_achievements(user)

        # 获取用户统计数据
        total_entries = LifeDiaryEntry.objects.filter(user=user).count()
        streak_days = LifeDiaryEntry.get_writing_streak(user)
        unique_moods = LifeDiaryEntry.objects.filter(user=user).values("mood").distinct().count()
        entry_types_used = LifeDiaryEntry.objects.filter(user=user).values("entry_type").distinct().count()

        # 更新各种成就
        achievements = DiaryAchievement.objects.filter(user=user)

        for achievement in achievements:
            if achievement.achievement_type == "count":
                achievement.update_progress(total_entries)
            elif achievement.achievement_type == "streak":
                achievement.update_progress(streak_days)
            elif achievement.achievement_type == "variety" and "情绪" in achievement.name:
                achievement.update_progress(unique_moods)
            elif achievement.achievement_type == "creative":
                achievement.update_progress(entry_types_used)

    except Exception as e:
        logger.error(f"Error updating achievements: {e}")


@login_required
def diary_weekly_report(request):
    """生成周报"""
    user = request.user
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=7)

    entries = LifeDiaryEntry.objects.filter(user=user, date__gte=start_date, date__lte=end_date).order_by("date")

    # 统计数据
    mood_stats = {}
    entry_types = {}
    total_words = 0

    for entry in entries:
        # 心情统计
        mood_stats[entry.mood] = mood_stats.get(entry.mood, 0) + 1
        # 类型统计
        entry_types[entry.entry_type] = entry_types.get(entry.entry_type, 0) + 1
        # 字数统计
        total_words += entry.word_count

    # 最高频心情
    most_common_mood = max(mood_stats.items(), key=lambda x: x[1])[0] if mood_stats else "😊"

    report_data = {
        "period": f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}",
        "total_entries": len(entries),
        "total_words": total_words,
        "most_common_mood": most_common_mood,
        "mood_distribution": mood_stats,
        "entry_types": entry_types,
        "entries": [
            {
                "date": entry.date.strftime("%m/%d"),
                "mood": entry.mood,
                "summary": entry.get_entry_summary()[:100],
            }
            for entry in entries
        ],
    }

    return JsonResponse(
        {
            "success": True,
            "report": report_data,
        }
    )


@login_required
def diary_list(request):
    """获取用户的日记列表"""
    user = request.user
    page = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("page_size", 10))

    # 获取用户的所有日记，按日期倒序
    entries = LifeDiaryEntry.objects.filter(user=user).order_by("-date", "-created_at")

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    page_entries = entries[start:end]

    entries_data = []
    for entry in page_entries:
        entries_data.append(
            {
                "id": entry.id,
                "date": entry.date.isoformat(),
                "title": entry.title or f"{entry.mood} {entry.get_entry_summary()[:20]}",
                "content": entry.content,
                "mood": entry.mood,
                "entry_type": entry.entry_type,
                "word_count": entry.word_count,
                "image_url": entry.image.url if entry.image else None,
                "created_at": entry.created_at.isoformat(),
                "summary": entry.get_entry_summary(),
            }
        )

    return JsonResponse(
        {
            "success": True,
            "entries": entries_data,
            "has_more": end < entries.count(),
            "page": page,
            "total_count": entries.count(),
        }
    )
