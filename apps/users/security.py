import re
import html
import logging
import time
from collections import defaultdict
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, HttpResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class SecurityMiddleware(MiddlewareMixin):
    """安全中间件，提供多种安全防护"""

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.ip_attack_counts = defaultdict(list)
        self.suspicious_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<form[^>]*>",
            r"<input[^>]*>",
            r"<textarea[^>]*>",
            r"<select[^>]*>",
            r"<button[^>]*>",
            r"<a[^>]*>",
            r"<img[^>]*>",
            r"<video[^>]*>",
            r"<audio[^>]*>",
            r"<canvas[^>]*>",
            r"<svg[^>]*>",
            r"<math[^>]*>",
            r"<applet[^>]*>",
            r"<base[^>]*>",
            r"<bgsound[^>]*>",
            r"<command[^>]*>",
            r"<details[^>]*>",
            r"<dialog[^>]*>",
            r"<fieldset[^>]*>",
            r"<figure[^>]*>",
            r"<figcaption[^>]*>",
            r"<footer[^>]*>",
            r"<header[^>]*>",
            r"<hgroup[^>]*>",
            r"<keygen[^>]*>",
            r"<legend[^>]*>",
            r"<map[^>]*>",
            r"<menu[^>]*>",
            r"<menuitem[^>]*>",
            r"<meter[^>]*>",
            r"<nav[^>]*>",
            r"<noscript[^>]*>",
            r"<optgroup[^>]*>",
            r"<option[^>]*>",
            r"<output[^>]*>",
            r"<param[^>]*>",
            r"<progress[^>]*>",
            r"<ruby[^>]*>",
            r"<rt[^>]*>",
            r"<rp[^>]*>",
            r"<samp[^>]*>",
            r"<section[^>]*>",
            r"<source[^>]*>",
            r"<summary[^>]*>",
            r"<time[^>]*>",
            r"<track[^>]*>",
            r"<wbr[^>]*>",
        ]

    def process_request(self, request):
        """处理请求前的安全检查"""
        client_ip = self._get_client_ip(request)

        # 检查IP黑名单
        if self._is_blacklisted_ip(client_ip):
            logger.warning(f"黑名单IP访问被拒绝: {client_ip}")
            return HttpResponseForbidden("Access denied")

        # 检查攻击频率
        if self._is_attack_frequency_exceeded(client_ip):
            logger.warning(f"IP攻击频率过高: {client_ip}")
            return HttpResponseForbidden("Rate limit exceeded")

        # 检查请求来源
        if not self._is_valid_origin(request):
            logger.warning(f"可疑请求来源: {request.META.get('HTTP_REFERER', 'Unknown')} from {client_ip}")
            return HttpResponseForbidden("Invalid request origin")

        # 检查可疑请求头
        if self._has_suspicious_headers(request):
            logger.warning(f"可疑请求头: {client_ip}")
            return HttpResponseForbidden("Suspicious request headers")

        # 检查请求内容
        if self._has_malicious_content(request):
            logger.warning(f"恶意内容检测: {client_ip}")
            return HttpResponseForbidden("Malicious content detected")

        # 记录请求
        self._record_request(client_ip)

        return None

    def _get_client_ip(self, request):
        """获取客户端真实IP"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _is_blacklisted_ip(self, ip):
        """检查是否为黑名单IP"""
        blacklisted_ips = getattr(settings, "BLACKLISTED_IPS", [])
        return ip in blacklisted_ips

    def _is_attack_frequency_exceeded(self, ip):
        """检查攻击频率是否超限"""
        current_time = time.time()
        # 清理超过1小时的记录
        self.ip_attack_counts[ip] = [t for t in self.ip_attack_counts[ip] if current_time - t < 3600]

        # 如果1小时内请求超过1000次，认为是攻击
        if len(self.ip_attack_counts[ip]) > 1000:
            return True

        return False

    def _record_request(self, ip):
        """记录请求"""
        current_time = time.time()
        self.ip_attack_counts[ip].append(current_time)

    def _is_valid_origin(self, request):
        """检查请求来源是否有效"""
        referer = request.META.get("HTTP_REFERER", "")
        if not referer:
            return True  # 允许直接访问

        # 检查是否来自允许的域名
        allowed_domains = getattr(settings, "ALLOWED_REFERER_DOMAINS", [])
        if allowed_domains:
            from urllib.parse import urlparse

            try:
                parsed = urlparse(referer)
                return parsed.netloc in allowed_domains
            except:
                return False

        return True

    def _has_suspicious_headers(self, request):
        """检查是否有可疑的请求头"""
        suspicious_headers = [
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "HTTP_CLIENT_IP",
            "HTTP_X_CLUSTER_CLIENT_IP",
            "HTTP_FORWARDED",
            "HTTP_VIA",
            "HTTP_PROXY_CONNECTION",
        ]

        for header in suspicious_headers:
            if header in request.META:
                value = request.META[header]
                if self._is_suspicious_ip(value):
                    return True

        return False

    def _is_suspicious_ip(self, ip):
        """检查是否为可疑IP"""
        # 在开发环境中允许本地访问
        if settings.DEBUG:
            return False

        # 检查是否为私有IP
        private_ip_patterns = [
            r"^10\.",
            r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
            r"^192\.168\.",
            r"^127\.",
            r"^169\.254\.",
            r"^::1$",
            r"^fe80:",
        ]

        for pattern in private_ip_patterns:
            if re.match(pattern, ip):
                return True

        return False

    def _has_malicious_content(self, request):
        """检查是否包含恶意内容"""
        # 检查POST数据
        if request.method == "POST":
            for key, value in request.POST.items():
                if isinstance(value, str):
                    if self._contains_malicious_pattern(value):
                        return True

        # 检查GET参数
        for key, value in request.GET.items():
            if isinstance(value, str):
                if self._contains_malicious_pattern(value):
                    return True

        # 检查请求头
        for key, value in request.META.items():
            if isinstance(value, str):
                if self._contains_malicious_pattern(value):
                    return True

        return False

    def _contains_malicious_pattern(self, content):
        """检查是否包含恶意模式"""
        content_lower = content.lower()

        # 检查XSS模式
        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True

        # 检查SQL注入模式
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\')",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*--)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'--)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*#)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'#)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*/\*)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'/\*)",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False


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
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError("用户名只能包含字母、数字和下划线")

        # 检查是否包含敏感词
        sensitive_words = ["admin", "root", "system", "test"]
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
        domain = email.split("@")[1] if "@" in email else ""
        blacklisted_domains = getattr(settings, "BLACKLISTED_EMAIL_DOMAINS", [])
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
        if not re.search(r"[A-Z]", password):
            raise ValidationError("密码必须包含至少一个大写字母")

        if not re.search(r"[a-z]", password):
            raise ValidationError("密码必须包含至少一个小写字母")

        if not re.search(r"\d", password):
            raise ValidationError("密码必须包含至少一个数字")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("密码必须包含至少一个特殊字符")

        # 检查常见弱密码
        weak_passwords = ["password", "123456", "qwerty", "admin"]
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
        if "<script" in content.lower():
            raise ValidationError("内容包含恶意脚本")

        # 检查是否包含SQL注入关键词
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "UNION"]
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
        dangerous_tags = ["script", "iframe", "object", "embed", "form"]
        for tag in dangerous_tags:
            if f"<{tag}" in html_content.lower():
                return False

        # 检查危险属性
        dangerous_attrs = ["onclick", "onload", "onerror", "javascript:"]
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
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\')",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*--)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'--)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*#)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'#)",
            r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*/\*)",
            r"(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'/\*)",
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
        input_string = re.sub(r"--.*$", "", input_string, flags=re.MULTILINE)
        input_string = re.sub(r"/\*.*?\*/", "", input_string, flags=re.DOTALL)
        input_string = re.sub(r"#.*$", "", input_string, flags=re.MULTILINE)

        # 移除分号
        input_string = input_string.replace(";", "")

        # 移除引号
        input_string = input_string.replace("'", "''")
        input_string = input_string.replace('"', '""')

        return input_string


class CSRFProtector:
    """CSRF防护器"""

    @staticmethod
    def validate_csrf_token(request):
        """验证CSRF令牌"""
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        csrf_token = request.POST.get("csrfmiddlewaretoken") or request.headers.get("X-CSRFToken")
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
            req_time for req_time in self.request_counts[identifier] if current_time - req_time < window_seconds
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
            req_time for req_time in self.request_counts[identifier] if current_time - req_time < window_seconds
        ]

        return max(0, max_requests - len(self.request_counts[identifier]))


# 全局实例
rate_limiter = RateLimiter()


def security_decorator(func):
    """安全装饰器"""

    def wrapper(request, *args, **kwargs):
        # 输入验证
        if request.method == "POST":
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
        identifier = request.META.get("REMOTE_ADDR", "unknown")
        if not rate_limiter.check_rate_limit(identifier):
            logger.warning(f"频率限制触发: {identifier}")
            return HttpResponseForbidden("Rate limit exceeded")

        return func(request, *args, **kwargs)

    return wrapper
