
import matplotlib
matplotlib.use('Agg')  # 设置后端为Agg
import random
import string
import re
import matplotlib.pyplot as plt
from django.http import HttpResponse
import numpy as np
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
from .models import UserRole, UserStatus, UserMembership, UserActionLog, Profile
from apps.content.views import admin_required
from django.template.defaulttags import register

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

def login_view(request):
    form = LoginForm(request.POST or None)  # 如果是GET请求，表单将为None

    if request.method == 'POST':
        captcha_response = request.POST.get('captcha')  # 获取用户输入的验证码

        # 验证验证码
        if captcha_response != request.session.get('captcha'):
            messages.error(request, '验证码不正确，请重新输入。', extra_tags='captcha')
        elif form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')  # 登录成功后重定向到主页
            else:
                messages.error(request, "用户名或密码不正确。")
        else:
            messages.error(request, "请检查输入的内容。")

    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)  # 退出用户
        messages.info(request, "你已成功登出。")  # 添加登出成功的消息
    else:
        messages.warning(request, "请先登录。")  # 添加没有登录时的提示
    return redirect('home')  # 重定向到首页或其他指定页面

# 在这里定义生成验证码的视图
def generate_captcha(request):
    # 生成随机验证码
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # 创建验证码图像
    fig = plt.figure(figsize=(3, 1), dpi=100)
    plt.text(0.5, 0.5, captcha_text, fontsize=40, ha='center', va='center', color='black', fontweight='bold')

    # 添加干扰线
    for _ in range(5):  # 添加5条干扰线
        x_values = np.random.rand(2)
        y_values = np.random.rand(2)
        plt.plot(x_values, y_values, color='red', linewidth=1, alpha=0.5)

    # 设置背景颜色为淡色
    fig.patch.set_facecolor('#f0f0f0')

    # 隐藏坐标轴
    plt.axis('off')

    # 将验证码文本存储在会话中
    request.session['captcha'] = captcha_text

    # 保存验证码图像到内存
    response = HttpResponse(content_type='image/png')
    plt.savefig(response, format='png')  # 保存图像到响应
    plt.close(fig)  # 关闭图像以释放内存
    return response

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})



@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # 保存修改的信息到数据库
            messages.success(request, "资料已成功更新！")
            return redirect('profile_view')  # 重定向到用户资料视图
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})

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
        captcha = request.POST.get('captcha')
        stored_captcha = request.session.get('captcha', '')
        
        if captcha.lower() != stored_captcha.lower():
            messages.error(request, '验证码错误')
            return render(request, 'users/login.html')
        
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
        # 记录登出活动
        try:
            from .models import UserActivityLog, UserSessionStats
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
        except Exception as e:
            print(f"记录登出活动失败: {e}")
    
    logout(request)
    messages.success(request, '您已成功登出')
    return redirect('home')

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
            return redirect('profile_view')
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
        })
        
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
        })
        
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
        })
        
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
        })
        
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
            return JsonResponse({'success': False, 'message': '请选择要操作的用户'}, status=400)
        
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
        })
        
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
        })
        
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
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)