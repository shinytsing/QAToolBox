from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.template.defaulttags import register
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import uuid
from datetime import datetime
from .models import Article, Comment, Suggestion, Feedback, Announcement, AILink, FeatureAccess, UserFeatureAccess
from .forms import ArticleForm, CommentForm
from .utils import extract_favicon_url, download_and_save_icon, get_domain_from_url
from apps.users.models import UserRole


# 注册模板过滤器
@register.filter
def status_color(status):
    """返回状态对应的Bootstrap颜色类"""
    colors = {"pending": "warning", "reviewing": "info", "implemented": "success", "rejected": "danger"}
    return colors.get(status, "secondary")


@register.filter
def status_display(status):
    """返回状态的中文显示名称"""
    displays = {"pending": "待处理", "reviewing": "审核中", "implemented": "已实现", "rejected": "已拒绝"}
    return displays.get(status, status)


def article_list(request):
    articles = Article.objects.all().order_by("-created_at")
    paginator = Paginator(articles, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "content/article_list.html", {"page_obj": page_obj})


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comment_set.all().order_by("-created_at")

    if request.method == "POST" and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            messages.success(request, "评论已添加！")
            return redirect("article_detail", pk=pk)
    else:
        form = CommentForm()

    return render(request, "content/article_detail.html", {"article": article, "comments": comments, "form": form})


@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "文章已创建！")
            return redirect("article_detail", pk=article.pk)
    else:
        form = ArticleForm()

    return render(request, "content/article_form.html", {"form": form})


@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, "您没有权限编辑此文章！")
        return redirect("article_detail", pk=pk)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "文章已更新！")
            return redirect("article_detail", pk=pk)
    else:
        form = ArticleForm(instance=article)

    return render(request, "content/article_form.html", {"form": form})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, "您没有权限删除此文章！")
        return redirect("article_detail", pk=pk)

    if request.method == "POST":
        article.delete()
        messages.success(request, "文章已删除！")
        return redirect("article_list")

    return render(request, "content/article_confirm_delete.html", {"article": article})


# 管理员权限检查装饰器
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "请先登录")
            return redirect("users:login")

        try:
            user_role = request.user.role
            if not user_role.is_admin:
                messages.error(request, "您没有管理员权限")
                return redirect("home")
        except UserRole.DoesNotExist:
            messages.error(request, "您没有管理员权限")
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


# 管理员建议管理页面
@login_required
@admin_required
def admin_suggestions(request):
    suggestions = Suggestion.objects.all().order_by("-created_at")
    return render(request, "content/admin_suggestions.html", {"suggestions": suggestions})


# 管理员仪表板
@login_required
@admin_required
def admin_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from apps.users.models import User, UserActionLog

    # 获取统计数据
    total_users = User.objects.count()
    pending_suggestions = Suggestion.objects.filter(status="pending").count()
    pending_feedbacks = Feedback.objects.filter(status="pending").count()

    # 今日活跃用户（有操作记录的用户）
    today = timezone.now().date()
    active_users = UserActionLog.objects.filter(created_at__date=today).values("admin_user").distinct().count()

    # 最近操作日志
    recent_logs = UserActionLog.objects.select_related("admin_user").order_by("-created_at")[:10]

    return render(
        request,
        "content/admin_dashboard.html",
        {
            "total_users": total_users,
            "pending_suggestions": pending_suggestions,
            "pending_feedbacks": pending_feedbacks,
            "active_users": active_users,
            "recent_logs": recent_logs,
        },
    )


# 管理员反馈管理页面
@login_required
@admin_required
def admin_feedback(request):
    feedbacks = Feedback.objects.all().order_by("-created_at")
    return render(request, "content/admin_feedback.html", {"feedbacks": feedbacks})


@login_required
@admin_required
def admin_announcements(request):
    """管理员公告管理页面"""
    return render(request, "content/admin_announcements.html")


# 建议和反馈API
@csrf_exempt
@require_http_methods(["POST"])
def upload_media_api(request):
    """处理图片和视频文件上传"""
    if request.method == "POST":
        try:
            uploaded_files = []

            # 处理多个文件上传
            for field_name in request.FILES:
                files = request.FILES.getlist(field_name)
                for file in files:
                    # 验证文件类型
                    file_ext = os.path.splitext(file.name)[1].lower()
                    allowed_image_exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                    allowed_video_exts = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]

                    if file_ext in allowed_image_exts:
                        file_type = "image"
                        upload_path = f'suggestions/images/{datetime.now().strftime("%Y/%m/%d")}/{uuid.uuid4()}{file_ext}'
                    elif file_ext in allowed_video_exts:
                        file_type = "video"
                        upload_path = f'suggestions/videos/{datetime.now().strftime("%Y/%m/%d")}/{uuid.uuid4()}{file_ext}'
                    else:
                        continue  # 跳过不支持的文件类型

                    # 保存文件
                    saved_path = default_storage.save(upload_path, ContentFile(file.read()))
                    file_url = default_storage.url(saved_path)

                    uploaded_files.append({"type": file_type, "name": file.name, "url": file_url, "size": file.size})

            return JsonResponse(
                {
                    "success": True,
                    "files": uploaded_files,
                    "message": f"成功上传 {len(uploaded_files)} 个文件",
                    "upload_info": {
                        "total_files": len(uploaded_files),
                        "upload_time": datetime.now().strftime("%H:%M:%S"),
                        "file_details": [
                            {"name": file["name"], "type": file["type"], "size": f'{file["size"] / 1024:.1f}KB'}
                            for file in uploaded_files
                        ],
                    },
                }
            )

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def suggestions_api(request):
    if request.method == "GET":
        # 根据用户角色获取建议
        if request.user.is_authenticated:
            try:
                # 检查用户是否为管理员
                if request.user.role.is_admin:
                    # 管理员可以看到所有建议
                    suggestions = Suggestion.objects.all().order_by("-created_at")
                else:
                    # 普通用户只能看到自己的建议
                    suggestions = Suggestion.objects.filter(user=request.user).order_by("-created_at")
            except:
                # 如果没有角色信息，普通用户只能看到自己的建议
                suggestions = Suggestion.objects.filter(user=request.user).order_by("-created_at")
        else:
            # 未登录用户看不到任何建议
            suggestions = Suggestion.objects.none()

        suggestions_data = []
        for suggestion in suggestions:
            suggestions_data.append(
                {
                    "id": suggestion.id,
                    "title": suggestion.title,
                    "content": suggestion.content,
                    "suggestion_type": suggestion.get_suggestion_type_display(),
                    "suggestion_type_code": suggestion.suggestion_type,
                    "status": suggestion.get_status_display(),
                    "status_code": suggestion.status,
                    "user_name": suggestion.user_name or (suggestion.user.username if suggestion.user else "匿名用户"),
                    "user": suggestion.user.id if suggestion.user else None,
                    "created_at": suggestion.created_at.strftime("%Y-%m-%d %H:%M"),
                    "updated_at": suggestion.updated_at.strftime("%Y-%m-%d %H:%M"),
                    "admin_response": suggestion.admin_response,
                    "has_response": bool(suggestion.admin_response),
                    "images": suggestion.images or [],
                    "videos": suggestion.videos or [],
                }
            )
        return JsonResponse({"success": True, "suggestions": suggestions_data}, content_type="application/json")

    elif request.method == "POST":
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({"error": "请先登录后再提交建议"}, status=401, content_type="application/json")

        # 提交新建议
        try:
            data = json.loads(request.body)
            title = data.get("title", "")
            content = data.get("content", "")
            suggestion_type = data.get("suggestion_type", "feature")
            images = data.get("images", [])
            videos = data.get("videos", [])

            if not title or not content:
                return JsonResponse({"error": "标题和内容不能为空"}, status=400, content_type="application/json")

            # 创建建议（用户已登录）
            suggestion = Suggestion.objects.create(
                title=title,
                content=content,
                suggestion_type=suggestion_type,
                user=request.user,
                user_name=request.user.username,
                user_email=request.user.email or "",
                images=images,
                videos=videos,
            )

            return JsonResponse(
                {"success": True, "message": "建议提交成功！", "suggestion_id": suggestion.id}, content_type="application/json"
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def feedback_api(request):
    if request.method == "GET":
        # 根据用户角色获取反馈
        if request.user.is_authenticated:
            try:
                # 检查用户是否为管理员
                if request.user.role.is_admin:
                    # 管理员可以看到所有反馈
                    feedbacks = Feedback.objects.all().order_by("-created_at")
                else:
                    # 普通用户只能看到自己的反馈
                    feedbacks = Feedback.objects.filter(user=request.user).order_by("-created_at")
            except:
                # 如果没有角色信息，普通用户只能看到自己的反馈
                feedbacks = Feedback.objects.filter(user=request.user).order_by("-created_at")
        else:
            # 未登录用户看不到任何反馈
            feedbacks = Feedback.objects.none()

        feedbacks_data = []
        for feedback in feedbacks:
            feedbacks_data.append(
                {
                    "id": feedback.id,
                    "feedback_type": feedback.get_feedback_type_display(),
                    "content": feedback.content,
                    "status": feedback.get_status_display(),
                    "user_name": feedback.user_name or (feedback.user.username if feedback.user else "匿名用户"),
                    "created_at": feedback.created_at.strftime("%Y-%m-%d %H:%M"),
                    "admin_response": feedback.admin_response,
                }
            )
        return JsonResponse({"feedbacks": feedbacks_data}, content_type="application/json")

    elif request.method == "POST":
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({"error": "请先登录后再提交反馈"}, status=401, content_type="application/json")

        # 提交新反馈
        try:
            data = json.loads(request.body)
            feedback_type = data.get("feedback_type", "bug")
            content = data.get("content", "")

            if not content:
                return JsonResponse({"error": "反馈内容不能为空"}, status=400, content_type="application/json")

            # 创建反馈（用户已登录）
            feedback = Feedback.objects.create(
                feedback_type=feedback_type,
                content=content,
                user=request.user,
                user_name=request.user.username,
                user_email=request.user.email or "",
            )

            return JsonResponse(
                {"success": True, "message": "反馈提交成功！", "feedback_id": feedback.id}, content_type="application/json"
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# 管理员回复建议API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_reply_suggestion(request):
    try:
        data = json.loads(request.body)
        suggestion_id = data.get("suggestion_id")
        response = data.get("response", "")
        status = data.get("status", "reviewing")
        action_note = data.get("action_note", "")

        suggestion = get_object_or_404(Suggestion, id=suggestion_id)

        # 记录原始状态
        old_status = suggestion.status
        old_response = suggestion.admin_response

        # 更新建议
        suggestion.admin_response = response
        suggestion.status = status
        suggestion.save()

        # 记录操作日志
        from apps.users.models import UserActionLog

        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=suggestion.user if suggestion.user else None,
            action="suggestion_processed",
            details=f'建议ID: {suggestion_id}, 状态从 {old_status} 变更为 {status}, 回复: {response[:100]}{"..." if len(response) > 100 else ""}, 备注: {action_note}',
        )

        return JsonResponse(
            {
                "success": True,
                "message": "建议处理完成",
                "suggestion": {
                    "id": suggestion.id,
                    "status": suggestion.status,
                    "admin_response": suggestion.admin_response,
                    "updated_at": suggestion.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 管理员回复反馈API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_reply_feedback(request):
    try:
        data = json.loads(request.body)
        feedback_id = data.get("feedback_id")
        response = data.get("response", "")
        status = data.get("status", "processing")

        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.admin_response = response
        feedback.status = status
        feedback.save()

        return JsonResponse({"success": True, "message": "回复已保存"}, content_type="application/json")

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 管理员仪表板统计API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def admin_dashboard_stats_api(request):
    from django.utils import timezone
    from apps.users.models import User, UserActionLog

    try:
        # 获取统计数据
        total_users = User.objects.count()
        pending_suggestions = Suggestion.objects.filter(status="pending").count()
        pending_feedbacks = Feedback.objects.filter(status="pending").count()

        # 今日活跃用户
        today = timezone.now().date()
        active_users = UserActionLog.objects.filter(created_at__date=today).values("admin_user").distinct().count()

        # 最近操作日志
        recent_logs = UserActionLog.objects.select_related("admin_user").order_by("-created_at")[:5]
        logs_data = []
        for log in recent_logs:
            logs_data.append(
                {
                    "admin_user": log.admin_user.username,
                    "action": log.action,
                    "created_at": log.created_at.strftime("%m-%d %H:%M"),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "stats": {
                    "total_users": total_users,
                    "pending_suggestions": pending_suggestions,
                    "pending_feedbacks": pending_feedbacks,
                    "active_users": active_users,
                    "recent_logs": logs_data,
                },
            },
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 批量更改建议状态API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_change_status_api(request):
    try:
        data = json.loads(request.body)
        suggestion_ids = data.get("suggestion_ids", [])
        new_status = data.get("new_status", "reviewing")

        if not suggestion_ids:
            return JsonResponse({"error": "请选择要操作的建议"}, status=400, content_type="application/json")

        # 批量更新建议状态
        updated_count = 0
        for suggestion_id in suggestion_ids:
            try:
                suggestion = Suggestion.objects.get(id=suggestion_id)
                old_status = suggestion.status
                suggestion.status = new_status
                suggestion.save()

                # 记录操作日志
                from apps.users.models import UserActionLog

                UserActionLog.objects.create(
                    admin_user=request.user,
                    target_user=suggestion.user if suggestion.user else None,
                    action="batch_status_change",
                    details=f"建议ID: {suggestion_id}, 状态从 {old_status} 批量变更为 {new_status}",
                )

                updated_count += 1
            except Suggestion.DoesNotExist:
                continue

        return JsonResponse(
            {"success": True, "message": f"成功更新 {updated_count} 条建议状态", "updated_count": updated_count},
            content_type="application/json",
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 批量处理建议API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_process_suggestions(request):
    try:
        data = json.loads(request.body)
        suggestion_ids = data.get("suggestion_ids", [])
        action = data.get("action", "")  # 'approve', 'reject', 'implement'
        response = data.get("response", "")

        if not suggestion_ids:
            return JsonResponse({"error": "请选择要处理的建议"}, status=400, content_type="application/json")

        processed_count = 0
        for suggestion_id in suggestion_ids:
            try:
                suggestion = Suggestion.objects.get(id=suggestion_id)

                if action == "approve":
                    suggestion.status = "reviewing"
                elif action == "reject":
                    suggestion.status = "rejected"
                elif action == "implement":
                    suggestion.status = "implemented"

                if response:
                    suggestion.admin_response = response

                suggestion.save()
                processed_count += 1

                # 记录操作日志
                from apps.users.models import UserActionLog

                UserActionLog.objects.create(
                    admin_user=request.user,
                    target_user=suggestion.user if suggestion.user else None,
                    action=f"batch_{action}_suggestion",
                    details=f"批量处理建议ID: {suggestion_id}, 操作: {action}",
                )

            except Suggestion.DoesNotExist:
                continue

        return JsonResponse(
            {"success": True, "message": f"成功处理 {processed_count} 条建议", "processed_count": processed_count},
            content_type="application/json",
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 公告相关API
@csrf_exempt
@require_http_methods(["GET"])
def announcement_list_api(request):
    """获取有效的公告列表"""
    try:
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({"success": True, "announcements": []}, content_type="application/json")

        # 检查用户是否已经看过公告（使用session跟踪）
        session_key = f"announcements_seen_{request.user.id}"
        announcements_seen = request.session.get(session_key, [])

        # 获取已发布且在有效期内的公告
        announcements = Announcement.objects.filter(status="published").order_by("-priority", "-created_at")

        # 过滤出有效的公告，并且用户还没有看过的
        active_announcements = []
        new_announcements = []

        for announcement in announcements:
            if announcement.is_active():
                announcement_data = {
                    "id": announcement.id,
                    "title": announcement.title,
                    "content": announcement.content,
                    "priority": announcement.priority,
                    "priority_display": announcement.get_priority_display(),
                    "is_popup": announcement.is_popup,
                    "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M"),
                }

                # 如果用户还没有看过这个公告，且需要弹窗显示
                if announcement.id not in announcements_seen and announcement.is_popup:
                    new_announcements.append(announcement_data)
                    # 记录用户已经看过这个公告
                    announcements_seen.append(announcement.id)

                active_announcements.append(announcement_data)

        # 更新session
        request.session[session_key] = announcements_seen
        request.session.modified = True

        return JsonResponse(
            {"success": True, "announcements": new_announcements}, content_type="application/json"  # 只返回用户没看过的新公告
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def announcement_admin_api(request):
    """管理员公告管理API"""
    # 检查管理员权限
    if not request.user.is_authenticated:
        return JsonResponse({"error": "需要登录"}, status=401, content_type="application/json")

    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role not in ["admin", "super_admin"]:
            return JsonResponse({"error": "权限不足"}, status=403, content_type="application/json")
    except UserRole.DoesNotExist:
        return JsonResponse({"error": "权限不足"}, status=403, content_type="application/json")

    if request.method == "GET":
        # 获取所有公告（管理员视图）
        try:
            announcements = Announcement.objects.all().order_by("-created_at")
            announcements_data = []

            for announcement in announcements:
                announcements_data.append(
                    {
                        "id": announcement.id,
                        "title": announcement.title,
                        "content": announcement.content,
                        "priority": announcement.priority,
                        "priority_display": announcement.get_priority_display(),
                        "status": announcement.status,
                        "status_display": announcement.get_status_display(),
                        "is_popup": announcement.is_popup,
                        "is_active": announcement.is_active(),
                        "start_time": announcement.start_time.strftime("%Y-%m-%d %H:%M"),
                        "end_time": announcement.end_time.strftime("%Y-%m-%d %H:%M") if announcement.end_time else None,
                        "created_by": announcement.created_by.username,
                        "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M"),
                    }
                )

            return JsonResponse({"success": True, "announcements": announcements_data}, content_type="application/json")

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == "POST":
        # 创建或更新公告
        try:
            data = json.loads(request.body)

            # 获取公告ID（如果是更新）
            announcement_id = data.get("id")

            if announcement_id:
                # 更新公告
                announcement = get_object_or_404(Announcement, id=announcement_id)
            else:
                # 创建新公告
                announcement = Announcement(created_by=request.user)

            # 更新字段
            announcement.title = data.get("title", "")
            announcement.content = data.get("content", "")
            announcement.priority = data.get("priority", "medium")
            announcement.status = data.get("status", "draft")
            announcement.is_popup = data.get("is_popup", True)

            # 处理时间字段
            if data.get("start_time"):
                from django.utils.dateparse import parse_datetime

                announcement.start_time = parse_datetime(data["start_time"])

            if data.get("end_time"):
                from django.utils.dateparse import parse_datetime

                announcement.end_time = parse_datetime(data["end_time"])

            announcement.save()

            return JsonResponse(
                {"success": True, "message": "公告保存成功", "announcement_id": announcement.id},
                content_type="application/json",
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的JSON数据"}, status=400, content_type="application/json")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def announcement_delete_api(request, announcement_id):
    """删除公告"""
    # 检查管理员权限
    if not request.user.is_authenticated:
        return JsonResponse({"error": "需要登录"}, status=401, content_type="application/json")

    try:
        user_role = UserRole.objects.get(user=request.user)
        if user_role.role not in ["admin", "super_admin"]:
            return JsonResponse({"error": "权限不足"}, status=403, content_type="application/json")
    except UserRole.DoesNotExist:
        return JsonResponse({"error": "权限不足"}, status=403, content_type="application/json")

    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.delete()

        return JsonResponse({"success": True, "message": "公告删除成功"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def ai_links_view(request):
    """AI友情链接页面"""
    links = AILink.objects.filter(is_active=True).order_by("sort_order", "name")

    # 按分类分组
    links_by_category = {}
    for link in links:
        category = link.get_category_display()
        if category not in links_by_category:
            links_by_category[category] = []
        links_by_category[category].append(link)

    return render(request, "content/ai_links.html", {"links_by_category": links_by_category})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def fetch_ai_link_icon(request):
    """获取AI链接的图标"""
    try:
        data = json.loads(request.body)
        link_id = data.get("link_id")

        if not link_id:
            return JsonResponse({"success": False, "message": "缺少链接ID"}, content_type="application/json")

        link = get_object_or_404(AILink, id=link_id)

        # 提取favicon URL
        favicon_url = extract_favicon_url(link.url)

        if not favicon_url:
            return JsonResponse({"success": False, "message": "无法获取网站图标"}, content_type="application/json")

        # 下载并保存图标
        domain = get_domain_from_url(link.url)
        filename = f"{domain}_icon"
        saved_path = download_and_save_icon(favicon_url, filename)

        if saved_path:
            # 更新链接的图标字段
            link.icon = saved_path
            link.icon_url = favicon_url
            link.save()

            return JsonResponse(
                {"success": True, "message": "图标获取成功", "icon_url": link.icon.url}, content_type="application/json"
            )
        else:
            return JsonResponse({"success": False, "message": "图标下载失败"}, content_type="application/json")

    except Exception as e:
        return JsonResponse({"success": False, "message": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def create_ai_links_from_list(request):
    """从预定义列表创建AI链接"""
    try:
        # 预定义的AI链接列表
        ai_links_data = [
            {
                "name": "Midjourney",
                "url": "https://www.midjourney.com/account",
                "category": "visual",
                "description": "AI图像生成工具，创建高质量的艺术作品",
            },
            {"name": "Suno", "url": "https://suno.com/", "category": "music", "description": "AI音乐创作平台，生成原创音乐"},
            {
                "name": "Cursor",
                "url": "https://cursor.com/cn/agents",
                "category": "programming",
                "description": "AI编程助手，智能代码生成和编辑",
            },
            {
                "name": "Pollo AI",
                "url": "https://pollo.ai/image-to-video",
                "category": "image",
                "description": "AI图片转视频工具，将静态图片转换为动态视频",
            },
            {
                "name": "Viggle AI",
                "url": "https://viggle.ai/home",
                "category": "image",
                "description": "AI视频生成工具，创建动态视频内容",
            },
            {
                "name": "MiniMax",
                "url": "https://www.minimaxi.com/",
                "category": "other",
                "description": "全栈自研的新一代AI模型矩阵，包含文本、视频、音频等多种AI能力",
            },
        ]

        created_count = 0
        for link_data in ai_links_data:
            # 检查是否已存在
            if not AILink.objects.filter(url=link_data["url"]).exists():
                link = AILink.objects.create(**link_data)

                # 尝试获取图标
                favicon_url = extract_favicon_url(link.url)
                if favicon_url:
                    domain = get_domain_from_url(link.url)
                    filename = f"{domain}_icon"
                    saved_path = download_and_save_icon(favicon_url, filename)
                    if saved_path:
                        link.icon = saved_path
                        link.icon_url = favicon_url
                        link.save()

                created_count += 1

        return JsonResponse(
            {"success": True, "message": f"成功创建 {created_count} 个AI友情链接"}, content_type="application/json"
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": f"创建失败: {str(e)}"})
