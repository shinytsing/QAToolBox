import json
import logging
import time
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class UserActivityMiddleware(MiddlewareMixin):
    """用户活动监控中间件"""

    def process_request(self, request):
        # 记录请求开始时间
        request.start_time = time.time()

        # 获取用户IP地址
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        request.client_ip = ip

        # 记录页面访问
        if request.user.is_authenticated and not request.path.startswith("/static/"):
            self.log_page_view(request, ip)

    def process_response(self, request, response):
        # 计算响应时间
        if hasattr(request, "start_time"):
            response_time = time.time() - request.start_time
        else:
            response_time = 0

        # 记录API访问
        if (
            request.path.startswith("/api/")
            or request.path.startswith("/content/api/")
            or request.path.startswith("/users/api/")
        ):
            self.log_api_access(request, response, response_time)

        return response

    def log_page_view(self, request, ip):
        """记录页面访问"""
        try:
            from .models import UserActivityLog

            UserActivityLog.objects.create(
                user=request.user,
                activity_type="page_view",
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                endpoint=request.path,
                method=request.method,
                status_code=200,
                details={
                    "referer": request.META.get("HTTP_REFERER", ""),
                    "query_params": dict(request.GET.items()),
                },
            )
        except Exception as e:
            print(f"记录页面访问失败: {e}")

    def log_api_access(self, request, response, response_time):
        """记录API访问"""
        try:
            # 获取请求大小
            request_size = len(request.body) if request.body else 0

            # 获取响应大小
            if hasattr(response, "content"):
                response_size = len(response.content)
            else:
                response_size = 0

            # 获取请求体信息（仅记录非敏感数据）
            request_data = {}
            if request.content_type == "application/json":
                try:
                    body_data = json.loads(request.body.decode("utf-8"))
                    # 过滤敏感信息
                    sensitive_fields = ["password", "token", "key", "secret"]
                    for field in sensitive_fields:
                        if field in body_data:
                            body_data[field] = "***"
                    request_data = body_data
                except Exception:
                    request_data = {}

            from .models import APIUsageStats

            APIUsageStats.objects.create(
                endpoint=request.path,
                method=request.method,
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.client_ip,
                status_code=response.status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
            )

            # 同时记录到活动日志
            if request.user.is_authenticated:
                from .models import UserActivityLog

                UserActivityLog.objects.create(
                    user=request.user,
                    activity_type="api_access",
                    ip_address=request.client_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time=response_time,
                    details={
                        "request_data": request_data,
                        "response_size": response_size,
                    },
                )
        except Exception as e:
            print(f"记录API访问失败: {e}")


class UserSessionMiddleware(MiddlewareMixin):
    """用户会话监控中间件"""

    def process_request(self, request):
        if request.user.is_authenticated:
            # 检查是否有活跃会话
            from .models import UserSessionStats

            active_session = UserSessionStats.objects.filter(user=request.user, is_active=True).first()

            if not active_session:
                # 创建新会话
                UserSessionStats.objects.create(
                    user=request.user,
                    session_start=timezone.now(),
                    ip_address=request.client_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    is_active=True,
                )

    def process_response(self, request, response):
        if request.user.is_authenticated:
            # 更新会话活跃时间
            from .models import UserSessionStats

            active_session = UserSessionStats.objects.filter(user=request.user, is_active=True).first()

            if active_session:
                # 如果超过30分钟没有活动，标记为非活跃
                if timezone.now() - active_session.session_start > timedelta(minutes=30):
                    active_session.is_active = False
                    active_session.session_end = timezone.now()
                    active_session.duration = int((active_session.session_end - active_session.session_start).total_seconds())
                    active_session.save()

        return response


class SessionExtensionMiddleware(MiddlewareMixin):
    """Session延长中间件 - 每次用户活动时延长session过期时间"""

    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request, "session"):
            # 获取当前session
            session = request.session

            # 检查session是否即将过期（比如还有7天过期）
            if session.get_expiry_age() < 60 * 60 * 24 * 7:  # 7天
                # 延长session过期时间到30天
                session.set_expiry(60 * 60 * 24 * 30)  # 30天
                session.save()

                # 同时更新cookie的过期时间
                if hasattr(request, "session"):
                    request.session.modified = True

    def process_response(self, request, response):
        if request.user.is_authenticated and hasattr(request, "session"):
            # 确保session被保存
            if request.session.modified:
                request.session.save()

        return response


class SessionPersistenceMiddleware(MiddlewareMixin):
    """会话持久化中间件 - 确保服务器重启时登录态保存"""

    def process_request(self, request):
        # 如果用户未登录但有会话cookie，尝试恢复会话
        from django.contrib.auth.models import AnonymousUser

        if isinstance(request.user, AnonymousUser) and hasattr(request, "session") and request.session:

            try:
                session_key = request.session.session_key
                if session_key:
                    # 从Redis中恢复会话数据
                    cache_key = f"session:{session_key}"
                    session_data = cache.get(cache_key)

                    if session_data and session_data.get("is_authenticated"):
                        # 恢复用户信息
                        from django.contrib.auth.models import User

                        user_id = session_data.get("user_id")

                        if user_id:
                            try:
                                user = User.objects.get(id=user_id)
                                request.user = user

                                # 更新会话数据
                                request.session.update(session_data)
                                request.session.save()

                                logger.info(f"会话已恢复: {session_key} -> 用户 {user.username}")

                            except User.DoesNotExist:
                                logger.warning(f"会话中的用户不存在: {user_id}")
                                # 清理无效会话
                                cache.delete(cache_key)
                                request.session.flush()

            except Exception as e:
                logger.error(f"会话恢复失败: {e}")

    def process_response(self, request, response):
        # 如果用户已登录，确保会话数据持久化
        from django.contrib.auth.models import AnonymousUser

        if (
            hasattr(request, "user")
            and not isinstance(request.user, AnonymousUser)
            and hasattr(request, "session")
            and request.session
        ):

            try:
                session_key = request.session.session_key
                if session_key:
                    # 在Redis中持久化会话数据
                    session_data = request.session.get_decoded()

                    # 添加用户信息到会话数据
                    session_data.update(
                        {
                            "user_id": request.user.id,
                            "username": request.user.username,
                            "is_authenticated": True,
                            "last_activity": timezone.now().isoformat(),
                        }
                    )

                    # 保存到Redis，设置30天过期
                    cache_key = f"session:{session_key}"
                    cache.set(cache_key, session_data, 60 * 60 * 24 * 30)

                    # 同时保存用户会话映射
                    user_session_key = f"user_session:{request.user.id}"
                    cache.set(user_session_key, session_key, 60 * 60 * 24 * 30)

                    logger.debug(f"会话已持久化: {session_key} -> 用户 {request.user.username}")

            except Exception as e:
                logger.error(f"会话持久化失败: {e}")

        return response
