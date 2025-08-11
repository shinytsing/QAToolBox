
import re
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import UserEditForm
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json
from .forms import UserRegistrationForm, UserLoginForm, ProfileEditForm
from .models import UserRole, UserStatus, UserMembership, UserActionLog, Profile, UserTheme, UserActivityLog, UserSessionStats
from apps.content.views import admin_required
from django.template.defaulttags import register

from .services.progressive_captcha_service import ProgressiveCaptchaService

# 注册模板过滤器
@register.filter
def activity_color(activity_type):
    """返回活动类型对应的Bootstrap颜色类"""
    colors = {
        'login': 'success',
        'logout': 'secondary',
        'api_access': 'info',
        'page_view': 'primary',
        'tool_usage': 'warning',
        'suggestion_submit': 'info',
        'feedback_submit': 'info',
        'profile_update': 'warning'
    }
    return colors.get(activity_type, 'secondary')

@register.filter
def status_color(status_code):
    """返回状态码对应的Bootstrap颜色类"""
    if not status_code:
        return 'secondary'
    if status_code >= 200 and status_code < 300:
        return 'success'
    elif status_code >= 300 and status_code < 400:
        return 'info'
    elif status_code >= 400 and status_code < 500:
        return 'warning'
    elif status_code >= 500:
        return 'danger'
    return 'secondary'


def has_repeated_characters(password):
    """检查密码中是否有连续重复的字符"""
    for i in range(len(password) - 1):
        if password[i] == password[i + 1]:
            return True
    return False

def has_consecutive_characters(password):
    """检查密码中是否有完全连续的字符"""
    # 检查字符是否是连续的，例如 "12345678" 或 "abcdefg"
    for i in range(len(password) - 1):
        if ord(password[i]) + 1 == ord(password[i + 1]):
            return True
    return False

def has_two_different_character_types(password):
    """检查密码中是否包含至少两种不同的字符类型"""
    types = {
        'lower': re.search(r'[a-z]', password),
        'upper': re.search(r'[A-Z]', password),
        'digit': re.search(r'\d', password),
        'special': re.search(r'[@$!%*?&]', password)  # 可以自定义特殊字符
    }
    return sum(bool(t) for t in types.values()) >= 2

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        email = request.POST.get('email', None)  # 邮箱为可选字段

        if password == password_confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, '用户名已存在，请选择其他用户名。', extra_tags='username')  # 对应标签
            else:
                if len(password) < 8:
                    messages.error(request, '密码必须大于8位。', extra_tags='password')
                elif has_repeated_characters(password):
                    messages.error(request, '密码不能包含连续重复的字符。', extra_tags='password')
                elif has_consecutive_characters(password):
                    messages.error(request, '密码不能是完全连续的字符。', extra_tags='password')
                elif not has_two_different_character_types(password):
                    messages.error(request, '密码必须包含至少两种不同的字符类型（如字母和数字）。', extra_tags='password')
                else:
                    try:
                        user = User.objects.create_user(username=username, password=password, email=email)
                        user.save()
                        messages.success(request, f'{username} 的账户已创建！')
                        return redirect('login')
                    except Exception as e:
                        messages.error(request, f'错误: {str(e)}')
        else:
            messages.error(request, '密码输入不一致，请重新确认。', extra_tags='password_confirm')  # 对应标签

    return render(request, 'users/register.html')



def logout_view(request):
    if request.user.is_authenticated:
        logout(request)  # 退出用户
        messages.info(request, "你已成功登出。")  # 添加登出成功的消息
    else:
        messages.warning(request, "请先登录。")  # 添加没有登录时的提示
    return redirect('home')  # 重定向到首页或其他指定页面





def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建用户角色、状态和会员信息
            UserRole.objects.create(user=user, role='user')
            UserStatus.objects.create(user=user, status='active')
            UserMembership.objects.create(user=user, membership_type='free')
            Profile.objects.create(user=user)
            
            messages.success(request, '注册成功！请登录。')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 检查验证码验证状态（支持新旧两种验证码）
        click_verified = request.session.get('click_captcha_verified', False)
        progressive_verified = request.session.get('progressive_captcha_verified', False)
        
        if not (click_verified or progressive_verified):
            messages.error(request, '请先完成验证码验证')
            return render(request, 'users/login.html')
        
        # 清除验证状态，防止重复使用
        request.session.pop('click_captcha_verified', None)
        request.session.pop('progressive_captcha_verified', None)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # 记录登录活动
            try:
                from .models import UserActivityLog
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
                UserActivityLog.objects.create(
                    user=user,
                    activity_type='login',
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={
                        'login_method': 'password',
                        'success': True
                    }
                )
            except Exception as e:
                print(f"记录登录活动失败: {e}")
            
            messages.success(request, f'欢迎回来，{user.username}！')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'users/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        
        # 记录登出活动
        try:
            from .models import UserActivityLog, UserSessionStats
            from django.core.cache import cache
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'logout_method': 'manual'
                }
            )
            
            # 结束活跃会话
            active_session = UserSessionStats.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            if active_session:
                active_session.is_active = False
                active_session.session_end = timezone.now()
                active_session.duration = int((active_session.session_end - active_session.session_start).total_seconds())
                active_session.save()
                
            # 清除用户相关的缓存token和数据
            cache_keys_to_clear = [
                f'boss_user_token_{user_id}',  # Boss直聘登录token
                f'user_profile_{user_id}',     # 用户配置缓存
                f'user_theme_{user_id}',       # 用户主题缓存
                f'user_session_{user_id}',     # 用户会话缓存
            ]
            
            for cache_key in cache_keys_to_clear:
                try:
                    cache.delete(cache_key)
                except Exception as cache_error:
                    print(f"清除缓存失败 {cache_key}: {cache_error}")
                    
        except Exception as e:
            print(f"记录登出活动失败: {e}")
    
    # 获取当前会话键，以便在前端清除
    session_key = request.session.session_key
    
    # Django内置登出（清除session和认证状态）
    logout(request)
    
    # 添加登出成功消息
    messages.success(request, '您已成功登出，所有认证信息已清除')
    
    # 创建响应并添加自定义头，通知前端清除token
    response = redirect('home')
    response['X-Logout-Success'] = 'true'
    response['X-Clear-Storage'] = 'true'
    
    return response

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    return render(request, 'users/profile.html', {'profile': profile})

@login_required
def profile_edit(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    
    return render(request, 'users/profile_edit.html', {'form': form})

# 管理员用户管理视图
@login_required
@admin_required
def admin_user_management(request):
    # 获取所有用户角色信息，按创建时间倒序排列
    user_roles = UserRole.objects.select_related('user', 'user__profile').prefetch_related('user__status', 'user__membership').order_by('-user__date_joined')
    
    # 统计信息
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # VIP用户统计
    vip_users = UserMembership.objects.filter(
        membership_type='vip',
        is_active=True,
        end_date__gt=timezone.now()
    ).count()
    
    # 今日新增用户
    today = timezone.now().date()
    today_users = User.objects.filter(date_joined__date=today).count()
    
    # 分页
    paginator = Paginator(user_roles, 20)  # 每页显示20个用户
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/admin_user_management.html', {
        'page_obj': page_obj,
        'total_users': total_users,
        'active_users': active_users,
        'vip_users': vip_users,
        'today_users': today_users
    })

@login_required
@admin_required
def admin_user_detail(request, user_id):
    user_detail = get_object_or_404(User, id=user_id)
    user_logs = UserActionLog.objects.filter(target_user=user_detail).select_related('admin_user').order_by('-created_at')[:10]
    
    return render(request, 'users/admin_user_detail.html', {
        'user_detail': user_detail,
        'user_logs': user_logs
    })

# 管理员用户管理API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_user_status_api(request, user_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        reason = data.get('reason', '')
        
        target_user = get_object_or_404(User, id=user_id)
        user_status, created = UserStatus.objects.get_or_create(user=target_user)
        
        old_status = user_status.status
        user_status.status = status
        user_status.reason = reason
        
        if status == 'suspended':
            user_status.suspended_until = timezone.now() + timedelta(days=7)  # 默认暂停7天
        else:
            user_status.suspended_until = None
        
        user_status.save()
        
        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action='status_change',
            details=f'状态从 {old_status} 变更为 {status}，原因：{reason}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'用户状态已更新为 {status}'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_membership_api(request, user_id):
    try:
        data = json.loads(request.body)
        membership_type = data.get('membership_type')
        days = data.get('days', 30)
        note = data.get('note', '')
        
        target_user = get_object_or_404(User, id=user_id)
        membership, created = UserMembership.objects.get_or_create(user=target_user)
        
        old_type = membership.membership_type
        membership.membership_type = membership_type
        membership.is_active = True
        
        if days > 0:
            membership.end_date = timezone.now() + timedelta(days=days)
        else:
            membership.end_date = None
        
        membership.save()
        
        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action='membership_change',
            details=f'会员类型从 {old_type} 变更为 {membership_type}，有效期：{days}天，备注：{note}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'用户会员已更新为 {membership_type}'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_change_role_api(request, user_id):
    try:
        data = json.loads(request.body)
        role = data.get('role')
        note = data.get('note', '')
        
        target_user = get_object_or_404(User, id=user_id)
        user_role, created = UserRole.objects.get_or_create(user=target_user)
        
        old_role = user_role.role
        user_role.role = role
        user_role.save()
        
        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action='role_change',
            details=f'角色从 {old_role} 变更为 {role}，备注：{note}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'用户角色已更新为 {role}'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_delete_user_api(request, user_id):
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '')
        
        target_user = get_object_or_404(User, id=user_id)
        
        # 软删除：将状态设置为deleted
        user_status, created = UserStatus.objects.get_or_create(user=target_user)
        user_status.status = 'deleted'
        user_status.reason = reason
        user_status.save()
        
        # 记录操作日志
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=target_user,
            action='account_delete',
            details=f'删除账号，原因：{reason}'
        )
        
        return JsonResponse({
            'success': True,
            'message': '用户账号已删除'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 获取用户操作日志API
@login_required
@admin_required
def admin_user_logs(request):
    logs = UserActionLog.objects.select_related('admin_user', 'target_user').order_by('-created_at')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/admin_user_logs.html', {
        'page_obj': page_obj
    })

# 批量操作API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_operation_api(request):
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        operation = data.get('operation')
        note = data.get('note', '')
        
        if not user_ids:
            return JsonResponse({'success': False, 'message': '请选择要操作的用户'}, status=400, content_type='application/json')
        
        success_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            try:
                target_user = User.objects.get(id=user_id)
                
                if operation == 'suspend':
                    # 批量暂停
                    user_status, created = UserStatus.objects.get_or_create(user=target_user)
                    user_status.status = 'suspended'
                    user_status.suspended_until = timezone.now() + timedelta(days=7)
                    user_status.save()
                    
                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action='batch_suspended',
                        details=f'批量暂停，备注：{note}'
                    )
                    
                elif operation == 'activate':
                    # 批量激活
                    user_status, created = UserStatus.objects.get_or_create(user=target_user)
                    user_status.status = 'active'
                    user_status.suspended_until = None
                    user_status.save()
                    
                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action='batch_activated',
                        details=f'批量激活，备注：{note}'
                    )
                    
                elif operation == 'upgrade_membership':
                    # 批量升级会员
                    membership, created = UserMembership.objects.get_or_create(user=target_user)
                    membership.membership_type = 'premium'
                    membership.is_active = True
                    membership.end_date = timezone.now() + timedelta(days=30)
                    membership.save()
                    
                    UserActionLog.objects.create(
                        admin_user=request.user,
                        target_user=target_user,
                        action='batch_upgraded',
                        details=f'批量升级会员，备注：{note}'
                    )
                
                success_count += 1
                
            except User.DoesNotExist:
                failed_count += 1
                continue
        
        return JsonResponse({
            'success': True,
            'message': f'批量操作完成，成功：{success_count}，失败：{failed_count}'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# 用户监控管理页面
@login_required
@admin_required
def admin_user_monitoring(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg
    from .models import UserActivityLog, APIUsageStats, UserSessionStats
    
    # 获取今日数据
    today = timezone.now().date()
    
    # 今日活跃用户
    today_active_users = UserActivityLog.objects.filter(
        created_at__date=today
    ).values('user').distinct().count()
    
    # 今日登录次数
    today_logins = UserActivityLog.objects.filter(
        activity_type='login',
        created_at__date=today
    ).count()
    
    # 今日API调用次数
    today_api_calls = APIUsageStats.objects.filter(
        created_at__date=today
    ).count()
    
    # 当前在线用户
    online_users = UserSessionStats.objects.filter(
        is_active=True,
        session_start__gte=timezone.now() - timedelta(minutes=30)
    ).count()
    
    # 最近活动
    recent_activities = UserActivityLog.objects.select_related('user').order_by('-created_at')[:20]
    
    # API使用统计
    api_stats = APIUsageStats.objects.filter(
        created_at__date=today
    ).values('endpoint', 'method').annotate(
        count=Count('id'),
        avg_response_time=Avg('response_time')
    ).order_by('-count')[:10]
    
    # 活跃会话
    active_sessions = UserSessionStats.objects.select_related('user').filter(
        is_active=True
    ).order_by('-session_start')
    
    return render(request, 'users/admin_user_monitoring.html', {
        'today_active_users': today_active_users,
        'today_logins': today_logins,
        'today_api_calls': today_api_calls,
        'online_users': online_users,
        'recent_activities': recent_activities,
        'api_stats': api_stats,
        'active_sessions': active_sessions,
    })

# 用户监控统计API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def admin_monitoring_stats_api(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Avg
    from .models import UserActivityLog, APIUsageStats, UserSessionStats
    
    try:
        # 获取今日数据
        today = timezone.now().date()
        
        # 今日活跃用户
        today_active_users = UserActivityLog.objects.filter(
            created_at__date=today
        ).values('user').distinct().count()
        
        # 今日登录次数
        today_logins = UserActivityLog.objects.filter(
            activity_type='login',
            created_at__date=today
        ).count()
        
        # 今日API调用次数
        today_api_calls = APIUsageStats.objects.filter(
            created_at__date=today
        ).count()
        
        # 当前在线用户
        online_users = UserSessionStats.objects.filter(
            is_active=True,
            session_start__gte=timezone.now() - timedelta(minutes=30)
        ).count()
        
        # 最近活动
        recent_activities = UserActivityLog.objects.select_related('user').order_by('-created_at')[:20]
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'user_name': activity.user.username if activity.user else '匿名用户',
                'activity_type': activity.activity_type,
                'activity_type_display': activity.get_activity_type_display(),
                'ip_address': activity.ip_address,
                'endpoint': activity.endpoint,
                'created_at': activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status_code': activity.status_code,
            })
        
        # API使用统计
        api_stats = APIUsageStats.objects.filter(
            created_at__date=today
        ).values('endpoint', 'method').annotate(
            count=Count('id'),
            avg_response_time=Avg('response_time')
        ).order_by('-count')[:10]
        
        api_stats_data = []
        for stat in api_stats:
            api_stats_data.append({
                'endpoint': stat['endpoint'],
                'method': stat['method'],
                'count': stat['count'],
                'avg_response_time': float(stat['avg_response_time'] or 0),
            })
        
        # 活跃会话
        active_sessions = UserSessionStats.objects.select_related('user').filter(
            is_active=True
        ).order_by('-session_start')
        
        sessions_data = []
        for session in active_sessions:
            sessions_data.append({
                'user_id': session.user.id,
                'user_name': session.user.username,
                'session_start': session.session_start.strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'is_active': session.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'stats': {
                'today_active_users': today_active_users,
                'today_logins': today_logins,
                'today_api_calls': today_api_calls,
                'online_users': online_users,
            },
            'recent_activities': activities_data,
            'api_stats': api_stats_data,
            'active_sessions': sessions_data,
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 强制登出用户API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_force_logout_api(request, user_id):
    import json
    from django.contrib.auth import logout
    from django.contrib.sessions.models import Session
    
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '管理员强制登出')
        
        # 获取用户
        user = get_object_or_404(User, id=user_id)
        
        # 结束用户的所有活跃会话
        active_sessions = UserSessionStats.objects.filter(
            user=user,
            is_active=True
        )
        
        for session in active_sessions:
            session.is_active = False
            session.session_end = timezone.now()
            session.duration = int((session.session_end - session.session_start).total_seconds())
            session.save()
        
        # 记录强制登出活动
        UserActivityLog.objects.create(
            user=user,
            activity_type='logout',
            ip_address=request.client_ip if hasattr(request, 'client_ip') else None,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={
                'logout_method': 'force',
                'reason': reason,
                'admin_user': request.user.username
            }
        )
        
        # 记录管理员操作
        UserActionLog.objects.create(
            admin_user=request.user,
            target_user=user,
            action='force_logout',
            details=f'强制登出用户 {user.username}，原因：{reason}'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'用户 {user.username} 已被强制登出'
        }, content_type='application/json')
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400, content_type='application/json')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# 主题API
@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required
def theme_api(request):
    """用户主题设置API"""
    try:
        if request.method == 'GET':
            # 获取用户当前主题
            user_theme, created = UserTheme.objects.get_or_create(
                user=request.user,
                defaults={'mode': 'work', 'theme_style': 'default'}
            )
            
            return JsonResponse({
                'success': True,
                'data': {
                    'mode': user_theme.mode,
                    'theme_style': user_theme.theme_style,
                    'subtitle': user_theme.subtitle,
                    'switch_count': user_theme.switch_count,
                    'last_switch_time': user_theme.last_switch_time.isoformat() if user_theme.last_switch_time else None
                }
            })
            
        elif request.method == 'POST':
            # 更新用户主题
            data = json.loads(request.body)
            mode = data.get('mode', 'work')
            
            # 验证模式是否有效
            valid_modes = ['work', 'life', 'training', 'emo', 'cyberpunk']
            if mode not in valid_modes:
                return JsonResponse({
                    'success': False,
                    'error': '无效的主题模式'
                }, status=400, content_type='application/json')
            
            # 更新或创建用户主题
            user_theme, created = UserTheme.objects.get_or_create(
                user=request.user,
                defaults={'mode': mode, 'theme_style': 'default'}
            )
            
            if not created:
                # 记录切换统计
                if user_theme.mode != mode:
                    user_theme.switch_count += 1
                    user_theme.last_switch_time = timezone.now()
                user_theme.mode = mode
                user_theme.save()
            
            return JsonResponse({
                'success': True,
                'data': {
                    'mode': user_theme.mode,
                    'theme_style': user_theme.theme_style,
                    'subtitle': user_theme.subtitle,
                    'switch_count': user_theme.switch_count,
                    'last_switch_time': user_theme.last_switch_time.isoformat() if user_theme.last_switch_time else None
                }
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400, content_type='application/json')
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# 头像上传API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def upload_avatar(request):
    """用户头像上传API"""
    try:
        # 检查是否有文件上传
        if 'avatar' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': '请选择要上传的头像文件'
            }, status=400, content_type='application/json')
        
        avatar_file = request.FILES['avatar']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': '只支持 JPG、PNG、GIF、WebP 格式的图片'
            }, status=400, content_type='application/json')
        
        # 验证文件大小（限制为5MB）
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'message': '头像文件大小不能超过5MB'
            }, status=400, content_type='application/json')
        
        # 获取或创建用户资料
        try:
            profile, created = Profile.objects.get_or_create(
                user=request.user,
                defaults={'user': request.user}
            )
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取用户资料失败: {str(e)}'
            }, status=500)
        
        # 图片处理：压缩和调整大小
        try:
            from PIL import Image
            import io
            import os
            from django.conf import settings
            from django.core.files.base import ContentFile
            
            # 打开图片
            img = Image.open(avatar_file)
            
            # 转换为RGB模式（如果是RGBA，去除透明通道）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 计算新的尺寸（强制正方形）
            target_size = (40, 40)  # 目标尺寸40x40像素
            
            # 计算缩放比例，取宽高的最大值
            width, height = img.size
            scale = max(target_size[0] / width, target_size[1] / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # 先缩放到能包含目标尺寸的大小
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 然后裁剪成正方形
            left = (new_width - target_size[0]) // 2
            top = (new_height - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]
            
            # 裁剪成正方形
            img = img.crop((left, top, right, bottom))
            
            # 保存压缩后的图片到内存
            output = io.BytesIO()
            
            # 根据原始文件类型选择保存格式
            file_extension = os.path.splitext(avatar_file.name)[1].lower()
            if file_extension in ['.jpg', '.jpeg']:
                img.save(output, format='JPEG', quality=85, optimize=True)
                content_type = 'image/jpeg'
                file_extension = '.jpg'
            elif file_extension == '.png':
                img.save(output, format='PNG', optimize=True)
                content_type = 'image/png'
            elif file_extension == '.webp':
                img.save(output, format='WEBP', quality=85, optimize=True)
                content_type = 'image/webp'
            else:
                # 默认保存为JPEG
                img.save(output, format='JPEG', quality=85, optimize=True)
                content_type = 'image/jpeg'
                file_extension = '.jpg'
            
            output.seek(0)
            
            # 生成文件名
            filename = f'avatar_{request.user.id}_{int(timezone.now().timestamp())}{file_extension}'
            
            # 创建ContentFile对象
            content_file = ContentFile(output.getvalue(), filename)
            
            # 保存到用户资料
            profile.avatar.save(filename, content_file, save=True)
            
            # 关闭图片对象
            img.close()
            output.close()
            
        except ImportError:
            # 如果没有Pillow库，使用原始文件
            import os
            from django.conf import settings
            
            file_extension = os.path.splitext(avatar_file.name)[1]
            if not file_extension:
                file_extension = '.jpg'
            
            filename = f'avatar_{request.user.id}_{int(timezone.now().timestamp())}{file_extension}'
            profile.avatar.save(filename, avatar_file, save=True)
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'图片处理失败: {str(e)}'
            }, status=500)
        
        # 记录用户操作
        try:
            UserActionLog.objects.create(
                user=request.user,
                action='avatar_upload',
                details=f'上传新头像: {filename}'
            )
        except Exception as e:
            print(f"Failed to log avatar upload: {e}")
        
        return JsonResponse({
            'success': True,
            'message': '头像上传成功',
            'avatar_url': profile.avatar.url if profile.avatar else None
        }, content_type='application/json')
        
    except Exception as e:
        import traceback
        print(f"Avatar upload error: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'message': f'头像上传失败: {str(e)}'
        }, status=500)

# 头像上传测试页面
@login_required
def avatar_test_view(request):
    """头像上传测试页面"""
    return render(request, 'avatar_test.html')


# 点击验证码相关视图



# 渐进式验证码相关视图
def generate_progressive_captcha(request):
    """生成渐进式验证码"""
    try:
        captcha_service = ProgressiveCaptchaService()
        session_key = request.session.session_key
        
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        result = captcha_service.generate_captcha(session_key)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'生成验证码失败: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def verify_progressive_captcha(request):
    """验证渐进式验证码"""
    try:
        data = json.loads(request.body)
        captcha_id = data.get('captcha_id')
        captcha_type = data.get('captcha_type')
        user_input = data.get('user_input')
        
        if not all([captcha_id, captcha_type, user_input is not None]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要的验证参数'
            })
        
        captcha_service = ProgressiveCaptchaService()
        session_key = request.session.session_key
        
        if not session_key:
            return JsonResponse({
                'success': False,
                'message': '会话无效，请刷新页面'
            })
        
        result = captcha_service.verify_captcha(session_key, captcha_id, captcha_type, user_input)
        
        # 如果验证成功，在session中标记
        if result.get('success'):
            request.session['progressive_captcha_verified'] = True
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }, status=500)

# 用户登出API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def user_logout_api(request):
    """用户登出API - 清除所有认证信息和token"""
    try:
        user_id = request.user.id
        
        # 记录登出活动
        try:
            from .models import UserActivityLog, UserSessionStats
            from django.core.cache import cache
            
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            UserActivityLog.objects.create(
                user=request.user,
                activity_type='logout',
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={
                    'logout_method': 'api'
                }
            )
            
            # 结束活跃会话
            active_sessions = UserSessionStats.objects.filter(
                user=request.user,
                is_active=True
            )
            
            for session in active_sessions:
                session.is_active = False
                session.session_end = timezone.now()
                session.duration = int((session.session_end - session.session_start).total_seconds())
                session.save()
                
            # 清除用户相关的缓存token和数据
            cache_keys_to_clear = [
                f'boss_user_token_{user_id}',       # Boss直聘登录token
                f'user_profile_{user_id}',          # 用户配置缓存
                f'user_theme_{user_id}',            # 用户主题缓存
                f'user_session_{user_id}',          # 用户会话缓存
                f'boss_login_status_{user_id}',     # Boss登录状态缓存
                f'user_preferences_{user_id}',      # 用户偏好设置缓存
            ]
            
            for cache_key in cache_keys_to_clear:
                try:
                    cache.delete(cache_key)
                except Exception as cache_error:
                    print(f"清除缓存失败 {cache_key}: {cache_error}")
                    
        except Exception as e:
            print(f"API登出记录失败: {e}")
        
        # Django内置登出
        logout(request)
        
        return JsonResponse({
            'success': True,
            'message': '登出成功，所有认证信息已清除',
            'clear_storage': True,  # 通知前端清除本地存储
            'redirect_url': '/'
        }, content_type='application/json')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'登出失败: {str(e)}'
        }, status=500, content_type='application/json')


# 登出功能测试页面
@login_required
def test_logout_view(request):
    """登出功能测试页面"""
    return render(request, 'test_logout.html')