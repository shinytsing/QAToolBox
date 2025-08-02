import re
import html
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """安全中间件，提供多种安全防护"""
    
    def process_request(self, request):
        """处理请求前的安全检查"""
        # 检查请求来源
        if not self._is_valid_origin(request):
            logger.warning(f"可疑请求来源: {request.META.get('HTTP_REFERER', 'Unknown')}")
            return HttpResponseForbidden("Invalid request origin")
        
        # 检查请求频率
        if not self._check_rate_limit(request):
            logger.warning(f"请求频率过高: {request.META.get('REMOTE_ADDR', 'Unknown')}")
            return HttpResponseForbidden("Request rate limit exceeded")
        
        # 检查可疑请求头
        if self._has_suspicious_headers(request):
            logger.warning(f"可疑请求头: {request.META.get('REMOTE_ADDR', 'Unknown')}")
            return HttpResponseForbidden("Suspicious request headers")
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """处理视图前的安全检查"""
        # 检查用户权限
        if not self._check_user_permissions(request, view_func):
            logger.warning(f"权限不足: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
            return HttpResponseForbidden("Insufficient permissions")
        
        return None
    
    def _is_valid_origin(self, request):
        """检查请求来源是否有效"""
        referer = request.META.get('HTTP_REFERER', '')
        if not referer:
            return True  # 允许直接访问
        
        # 检查是否来自允许的域名
        allowed_domains = getattr(settings, 'ALLOWED_REFERER_DOMAINS', [])
        if allowed_domains:
            from urllib.parse import urlparse
            parsed = urlparse(referer)
            return parsed.netloc in allowed_domains
        
        return True
    
    def _check_rate_limit(self, request):
        """检查请求频率限制"""
        # 这里可以实现更复杂的频率限制逻辑
        # 目前只是简单的检查
        return True
    
    def _has_suspicious_headers(self, request):
        """检查是否有可疑的请求头"""
        suspicious_headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CLIENT_IP',
        ]
        
        for header in suspicious_headers:
            if header in request.META:
                value = request.META[header]
                if self._is_suspicious_ip(value):
                    return True
        
        return False
    
    def _is_suspicious_ip(self, ip):
        """检查是否为可疑IP"""
        # 这里可以实现IP黑名单检查
        blacklisted_ips = getattr(settings, 'BLACKLISTED_IPS', [])
        return ip in blacklisted_ips
    
    def _check_user_permissions(self, request, view_func):
        """检查用户权限"""
        # 这里可以实现更复杂的权限检查逻辑
        return True


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_username(username):
        """验证用户名"""
        if not username:
            raise ValidationError("用户名不能为空")
        
        if len(username) < 3 or len(username) > 30:
            raise ValidationError("用户名长度必须在3-30个字符之间")
        
        # 只允许字母、数字和下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("用户名只能包含字母、数字和下划线")
        
        # 检查是否包含敏感词
        sensitive_words = ['admin', 'root', 'system', 'test']
        if username.lower() in sensitive_words:
            raise ValidationError("用户名包含敏感词")
        
        return username
    
    @staticmethod
    def validate_email(email):
        """验证邮箱"""
        if not email:
            raise ValidationError("邮箱不能为空")
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("邮箱格式不正确")
        
        # 检查邮箱域名
        domain = email.split('@')[1] if '@' in email else ''
        blacklisted_domains = getattr(settings, 'BLACKLISTED_EMAIL_DOMAINS', [])
        if domain in blacklisted_domains:
            raise ValidationError("该邮箱域名不被允许")
        
        return email
    
    @staticmethod
    def validate_password(password):
        """验证密码强度"""
        if not password:
            raise ValidationError("密码不能为空")
        
        if len(password) < 8:
            raise ValidationError("密码长度至少8个字符")
        
        # 检查密码复杂度
        if not re.search(r'[A-Z]', password):
            raise ValidationError("密码必须包含至少一个大写字母")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("密码必须包含至少一个小写字母")
        
        if not re.search(r'\d', password):
            raise ValidationError("密码必须包含至少一个数字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("密码必须包含至少一个特殊字符")
        
        # 检查常见弱密码
        weak_passwords = ['password', '123456', 'qwerty', 'admin']
        if password.lower() in weak_passwords:
            raise ValidationError("密码过于简单")
        
        return password
    
    @staticmethod
    def validate_text_content(content, max_length=10000):
        """验证文本内容"""
        if not content:
            raise ValidationError("内容不能为空")
        
        if len(content) > max_length:
            raise ValidationError(f"内容长度不能超过{max_length}个字符")
        
        # 检查是否包含恶意脚本
        if '<script' in content.lower():
            raise ValidationError("内容包含恶意脚本")
        
        # 检查是否包含SQL注入关键词
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION']
        for keyword in sql_keywords:
            if keyword.lower() in content.lower():
                raise ValidationError("内容包含不允许的关键词")
        
        return content


class XSSProtector:
    """XSS防护器"""
    
    @staticmethod
    def sanitize_html(html_content):
        """清理HTML内容，移除危险标签和属性"""
        if not html_content:
            return html_content
        
        # 移除所有HTML标签
        clean_content = strip_tags(html_content)
        
        # HTML实体编码
        clean_content = html.escape(clean_content)
        
        return clean_content
    
    @staticmethod
    def validate_html(html_content):
        """验证HTML内容是否安全"""
        if not html_content:
            return True
        
        # 检查危险标签
        dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
        for tag in dangerous_tags:
            if f'<{tag}' in html_content.lower():
                return False
        
        # 检查危险属性
        dangerous_attrs = ['onclick', 'onload', 'onerror', 'javascript:']
        for attr in dangerous_attrs:
            if attr in html_content.lower():
                return False
        
        return True


class SQLInjectionProtector:
    """SQL注入防护器"""
    
    @staticmethod
    def check_sql_injection(input_string):
        """检查是否包含SQL注入关键词"""
        if not input_string:
            return False
        
        # SQL注入关键词模式
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)',
            r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\')',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*--)',
            r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'--)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*#)',
            r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'#)',
            r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*/\*)',
            r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'/\*)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_sql_input(input_string):
        """清理SQL输入"""
        if not input_string:
            return input_string
        
        # 移除SQL注释
        input_string = re.sub(r'--.*$', '', input_string, flags=re.MULTILINE)
        input_string = re.sub(r'/\*.*?\*/', '', input_string, flags=re.DOTALL)
        input_string = re.sub(r'#.*$', '', input_string, flags=re.MULTILINE)
        
        # 移除分号
        input_string = input_string.replace(';', '')
        
        # 移除引号
        input_string = input_string.replace("'", "''")
        input_string = input_string.replace('"', '""')
        
        return input_string


class CSRFProtector:
    """CSRF防护器"""
    
    @staticmethod
    def validate_csrf_token(request):
        """验证CSRF令牌"""
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        csrf_token = request.POST.get('csrfmiddlewaretoken') or request.headers.get('X-CSRFToken')
        if not csrf_token:
            return False
        
        # 这里可以实现更复杂的CSRF令牌验证逻辑
        return True
    
    @staticmethod
    def generate_csrf_token():
        """生成CSRF令牌"""
        import secrets
        return secrets.token_urlsafe(32)


class RateLimiter:
    """频率限制器"""
    
    def __init__(self):
        self.request_counts = {}
    
    def check_rate_limit(self, identifier, max_requests=100, window_seconds=3600):
        """检查频率限制"""
        import time
        current_time = time.time()
        
        if identifier not in self.request_counts:
            self.request_counts[identifier] = []
        
        # 清理过期的请求记录
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if current_time - req_time < window_seconds
        ]
        
        # 检查是否超过限制
        if len(self.request_counts[identifier]) >= max_requests:
            return False
        
        # 添加当前请求
        self.request_counts[identifier].append(current_time)
        return True
    
    def get_remaining_requests(self, identifier, max_requests=100, window_seconds=3600):
        """获取剩余请求次数"""
        import time
        current_time = time.time()
        
        if identifier not in self.request_counts:
            return max_requests
        
        # 清理过期的请求记录
        self.request_counts[identifier] = [
            req_time for req_time in self.request_counts[identifier]
            if current_time - req_time < window_seconds
        ]
        
        return max(0, max_requests - len(self.request_counts[identifier]))


# 全局实例
rate_limiter = RateLimiter()


def security_decorator(func):
    """安全装饰器"""
    def wrapper(request, *args, **kwargs):
        # 输入验证
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str):
                    # 检查SQL注入
                    if SQLInjectionProtector.check_sql_injection(value):
                        logger.warning(f"检测到SQL注入尝试: {key}={value}")
                        return HttpResponseForbidden("Invalid input detected")
                    
                    # 检查XSS
                    if not XSSProtector.validate_html(value):
                        logger.warning(f"检测到XSS尝试: {key}={value}")
                        return HttpResponseForbidden("Invalid input detected")
        
        # 频率限制
        identifier = request.META.get('REMOTE_ADDR', 'unknown')
        if not rate_limiter.check_rate_limit(identifier):
            logger.warning(f"频率限制触发: {identifier}")
            return HttpResponseForbidden("Rate limit exceeded")
        
        return func(request, *args, **kwargs)
    
    return wrapper 