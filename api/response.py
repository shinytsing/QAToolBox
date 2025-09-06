"""
统一API响应格式
"""
import uuid
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message="操作成功", code=200):
        """成功响应"""
        return Response({
            "success": True,
            "code": code,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }, status=code)
    
    @staticmethod
    def error(message="操作失败", code=400, errors=None, data=None):
        """错误响应"""
        return Response({
            "success": False,
            "code": code,
            "message": message,
            "errors": errors,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        }, status=code)
    
    @staticmethod
    def paginated(data, paginator, page_obj):
        """分页响应"""
        return Response({
            "success": True,
            "code": 200,
            "message": "获取成功",
            "data": data,
            "pagination": {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page_obj.number,
                "page_size": paginator.per_page,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4())
        })


class APIErrorCodes:
    """API错误码定义"""
    
    # 通用错误码
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    
    # 认证相关错误码
    INVALID_CREDENTIALS = 1001
    TOKEN_EXPIRED = 1002
    TOKEN_INVALID = 1003
    USER_NOT_FOUND = 1004
    USER_DISABLED = 1005
    
    # 权限相关错误码
    INSUFFICIENT_PERMISSIONS = 403
    FEATURE_DISABLED = 403
    RATE_LIMIT_EXCEEDED = 429
    
    # 业务相关错误码
    VALIDATION_ERROR = 400
    RESOURCE_NOT_FOUND = 404
    OPERATION_FAILED = 500
    FILE_UPLOAD_FAILED = 400
    FILE_PROCESSING_FAILED = 500
    
    # 第三方服务错误码
    EXTERNAL_SERVICE_ERROR = 502
    API_QUOTA_EXCEEDED = 429
    NETWORK_ERROR = 503


class APIException(Exception):
    """API异常基类"""
    
    def __init__(self, message, code=APIErrorCodes.INTERNAL_SERVER_ERROR, errors=None):
        self.message = message
        self.code = code
        self.errors = errors
        super().__init__(self.message)
