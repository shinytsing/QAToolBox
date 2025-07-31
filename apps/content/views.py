from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.template.defaulttags import register
import json
from .models import Article, Comment, Suggestion, Feedback
from .forms import ArticleForm, CommentForm
from apps.users.models import UserRole

# 注册模板过滤器
@register.filter
def status_color(status):
    """返回状态对应的Bootstrap颜色类"""
    colors = {
        'pending': 'warning',
        'reviewing': 'info',
        'implemented': 'success',
        'rejected': 'danger'
    }
    return colors.get(status, 'secondary')

@register.filter
def status_display(status):
    """返回状态的中文显示名称"""
    displays = {
        'pending': '待处理',
        'reviewing': '审核中',
        'implemented': '已实现',
        'rejected': '已拒绝'
    }
    return displays.get(status, status)

def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'content/article_list.html', {'page_obj': page_obj})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comment_set.all().order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            messages.success(request, '评论已添加！')
            return redirect('article_detail', pk=pk)
    else:
        form = CommentForm()
    
    return render(request, 'content/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form
    })

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, '文章已创建！')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    
    return render(request, 'content/article_form.html', {'form': form})

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, '您没有权限编辑此文章！')
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, '文章已更新！')
            return redirect('article_detail', pk=pk)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'content/article_form.html', {'form': form})

@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, '您没有权限删除此文章！')
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, '文章已删除！')
        return redirect('article_list')
    
    return render(request, 'content/article_confirm_delete.html', {'article': article})

# 管理员权限检查装饰器
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '请先登录')
            return redirect('login')
        
        try:
            user_role = request.user.role
            if not user_role.is_admin:
                messages.error(request, '您没有管理员权限')
                return redirect('home')
        except UserRole.DoesNotExist:
            messages.error(request, '您没有管理员权限')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper

# 管理员建议管理页面
@login_required
@admin_required
def admin_suggestions(request):
    suggestions = Suggestion.objects.all().order_by('-created_at')
    return render(request, 'content/admin_suggestions.html', {
        'suggestions': suggestions
    })

# 管理员仪表板
@login_required
@admin_required
def admin_dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from apps.users.models import User, UserActionLog
    
    # 获取统计数据
    total_users = User.objects.count()
    pending_suggestions = Suggestion.objects.filter(status='pending').count()
    pending_feedbacks = Feedback.objects.filter(status='pending').count()
    
    # 今日活跃用户（有操作记录的用户）
    today = timezone.now().date()
    active_users = UserActionLog.objects.filter(
        created_at__date=today
    ).values('admin_user').distinct().count()
    
    # 最近操作日志
    recent_logs = UserActionLog.objects.select_related('admin_user').order_by('-created_at')[:10]
    
    return render(request, 'content/admin_dashboard.html', {
        'total_users': total_users,
        'pending_suggestions': pending_suggestions,
        'pending_feedbacks': pending_feedbacks,
        'active_users': active_users,
        'recent_logs': recent_logs
    })

# 管理员反馈管理页面
@login_required
@admin_required
def admin_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'content/admin_feedback.html', {
        'feedbacks': feedbacks
    })

# 建议和反馈API
@csrf_exempt
@require_http_methods(["GET", "POST"])
def suggestions_api(request):
    if request.method == 'GET':
        # 根据用户角色获取建议
        if request.user.is_authenticated:
            try:
                # 检查用户是否为管理员
                if request.user.role.is_admin:
                    # 管理员可以看到所有建议
                    suggestions = Suggestion.objects.all().order_by('-created_at')
                else:
                    # 普通用户只能看到自己的建议
                    suggestions = Suggestion.objects.filter(user=request.user).order_by('-created_at')
            except:
                # 如果没有角色信息，普通用户只能看到自己的建议
                suggestions = Suggestion.objects.filter(user=request.user).order_by('-created_at')
        else:
            # 未登录用户看不到任何建议
            suggestions = Suggestion.objects.none()
        
        suggestions_data = []
        for suggestion in suggestions:
            suggestions_data.append({
                'id': suggestion.id,
                'title': suggestion.title,
                'content': suggestion.content,
                'suggestion_type': suggestion.get_suggestion_type_display(),
                'suggestion_type_code': suggestion.suggestion_type,
                'status': suggestion.get_status_display(),
                'status_code': suggestion.status,
                'user_name': suggestion.user_name or (suggestion.user.username if suggestion.user else '匿名用户'),
                'user': suggestion.user.id if suggestion.user else None,
                'created_at': suggestion.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': suggestion.updated_at.strftime('%Y-%m-%d %H:%M'),
                'admin_response': suggestion.admin_response,
                'has_response': bool(suggestion.admin_response)
            })
        return JsonResponse({'success': True, 'suggestions': suggestions_data})
    
    elif request.method == 'POST':
        # 提交新建议
        try:
            data = json.loads(request.body)
            title = data.get('title', '')
            content = data.get('content', '')
            suggestion_type = data.get('suggestion_type', 'feature')
            user_name = data.get('user_name', '')
            user_email = data.get('user_email', '')
            
            if not title or not content:
                return JsonResponse({'error': '标题和内容不能为空'}, status=400)
            
            # 如果用户已登录，使用登录用户信息
            if request.user.is_authenticated:
                suggestion = Suggestion.objects.create(
                    title=title,
                    content=content,
                    suggestion_type=suggestion_type,
                    user=request.user,
                    user_name=request.user.username,
                    user_email=request.user.email or user_email
                )
            else:
                # 匿名用户提交建议
                suggestion = Suggestion.objects.create(
                    title=title,
                    content=content,
                    suggestion_type=suggestion_type,
                    user=None,
                    user_name=user_name,
                    user_email=user_email
                )
            
            return JsonResponse({
                'success': True,
                'message': '建议提交成功！',
                'suggestion_id': suggestion.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def feedback_api(request):
    if request.method == 'GET':
        # 根据用户角色获取反馈
        if request.user.is_authenticated:
            try:
                # 检查用户是否为管理员
                if request.user.role.is_admin:
                    # 管理员可以看到所有反馈
                    feedbacks = Feedback.objects.all().order_by('-created_at')
                else:
                    # 普通用户只能看到自己的反馈
                    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
            except:
                # 如果没有角色信息，普通用户只能看到自己的反馈
                feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
        else:
            # 未登录用户看不到任何反馈
            feedbacks = Feedback.objects.none()
        
        feedbacks_data = []
        for feedback in feedbacks:
            feedbacks_data.append({
                'id': feedback.id,
                'feedback_type': feedback.get_feedback_type_display(),
                'content': feedback.content,
                'status': feedback.get_status_display(),
                'user_name': feedback.user_name or (feedback.user.username if feedback.user else '匿名用户'),
                'created_at': feedback.created_at.strftime('%Y-%m-%d %H:%M'),
                'admin_response': feedback.admin_response
            })
        return JsonResponse({'feedbacks': feedbacks_data})
    
    elif request.method == 'POST':
        # 提交新反馈
        try:
            data = json.loads(request.body)
            feedback_type = data.get('feedback_type', 'bug')
            content = data.get('content', '')
            user_name = data.get('user_name', '')
            user_email = data.get('user_email', '')
            
            if not content:
                return JsonResponse({'error': '反馈内容不能为空'}, status=400)
            
            # 如果用户已登录，使用登录用户信息
            if request.user.is_authenticated:
                feedback = Feedback.objects.create(
                    feedback_type=feedback_type,
                    content=content,
                    user=request.user,
                    user_name=request.user.username,
                    user_email=request.user.email or user_email
                )
            else:
                # 匿名用户提交反馈
                feedback = Feedback.objects.create(
                    feedback_type=feedback_type,
                    content=content,
                    user=None,
                    user_name=user_name,
                    user_email=user_email
                )
            
            return JsonResponse({
                'success': True,
                'message': '反馈提交成功！',
                'feedback_id': feedback.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# 管理员回复建议API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_reply_suggestion(request):
    try:
        data = json.loads(request.body)
        suggestion_id = data.get('suggestion_id')
        response = data.get('response', '')
        status = data.get('status', 'reviewing')
        action_note = data.get('action_note', '')
        
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
            action='suggestion_processed',
            details=f'建议ID: {suggestion_id}, 状态从 {old_status} 变更为 {status}, 回复: {response[:100]}{"..." if len(response) > 100 else ""}, 备注: {action_note}'
        )
        
        return JsonResponse({
            'success': True,
            'message': '建议处理完成',
            'suggestion': {
                'id': suggestion.id,
                'status': suggestion.status,
                'admin_response': suggestion.admin_response,
                'updated_at': suggestion.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 管理员回复反馈API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_reply_feedback(request):
    try:
        data = json.loads(request.body)
        feedback_id = data.get('feedback_id')
        response = data.get('response', '')
        status = data.get('status', 'processing')
        
        feedback = get_object_or_404(Feedback, id=feedback_id)
        feedback.admin_response = response
        feedback.status = status
        feedback.save()
        
        return JsonResponse({
            'success': True,
            'message': '回复已保存'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        pending_suggestions = Suggestion.objects.filter(status='pending').count()
        pending_feedbacks = Feedback.objects.filter(status='pending').count()
        
        # 今日活跃用户
        today = timezone.now().date()
        active_users = UserActionLog.objects.filter(
            created_at__date=today
        ).values('admin_user').distinct().count()
        
        # 最近操作日志
        recent_logs = UserActionLog.objects.select_related('admin_user').order_by('-created_at')[:5]
        logs_data = []
        for log in recent_logs:
            logs_data.append({
                'admin_user': log.admin_user.username,
                'action': log.action,
                'created_at': log.created_at.strftime('%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_users': total_users,
                'pending_suggestions': pending_suggestions,
                'pending_feedbacks': pending_feedbacks,
                'active_users': active_users,
                'recent_logs': logs_data
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 批量更改建议状态API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_change_status_api(request):
    try:
        data = json.loads(request.body)
        suggestion_ids = data.get('suggestion_ids', [])
        new_status = data.get('new_status', 'reviewing')
        
        if not suggestion_ids:
            return JsonResponse({'error': '请选择要操作的建议'}, status=400)
        
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
                    action='batch_status_change',
                    details=f'建议ID: {suggestion_id}, 状态从 {old_status} 批量变更为 {new_status}'
                )
                
                updated_count += 1
            except Suggestion.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功更新 {updated_count} 条建议状态',
            'updated_count': updated_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 批量处理建议API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_process_suggestions(request):
    try:
        data = json.loads(request.body)
        suggestion_ids = data.get('suggestion_ids', [])
        action = data.get('action', '')  # 'approve', 'reject', 'implement'
        response = data.get('response', '')
        
        if not suggestion_ids:
            return JsonResponse({'error': '请选择要处理的建议'}, status=400)
        
        processed_count = 0
        for suggestion_id in suggestion_ids:
            try:
                suggestion = Suggestion.objects.get(id=suggestion_id)
                
                if action == 'approve':
                    suggestion.status = 'reviewing'
                elif action == 'reject':
                    suggestion.status = 'rejected'
                elif action == 'implement':
                    suggestion.status = 'implemented'
                
                if response:
                    suggestion.admin_response = response
                
                suggestion.save()
                processed_count += 1
                
                # 记录操作日志
                from apps.users.models import UserActionLog
                UserActionLog.objects.create(
                    admin_user=request.user,
                    target_user=suggestion.user if suggestion.user else None,
                    action=f'batch_{action}_suggestion',
                    details=f'批量处理建议ID: {suggestion_id}, 操作: {action}'
                )
                
            except Suggestion.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'成功处理 {processed_count} 条建议',
            'processed_count': processed_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
