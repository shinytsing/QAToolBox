"""
自定义CORS头部中间件
"""
from django.utils.deprecation import MiddlewareMixin

class CustomCORSHeadersMiddleware(MiddlewareMixin):
    """
    添加自定义CORS头部，解决Cross-Origin-Opener-Policy警告
    """
    
    def process_response(self, request, response):
        # 添加CORS头部
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        # 添加安全头部
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # 完全移除Cross-Origin-Opener-Policy头部，避免在HTTP环境下的警告
        # 这些头部只在HTTPS环境下才有意义，在HTTP环境下会产生警告
        
        return response
