"""
API版本控制服务
为微服务架构迁移做准备
"""
import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class APIVersionManager:
    """API版本管理器"""
    
    def __init__(self):
        self.versions = {
            'v1': {
                'status': 'stable',
                'deprecated': False,
                'deprecation_date': None,
                'sunset_date': None,
                'features': ['basic_tools', 'user_management', 'social_media'],
                'endpoints': {
                    '/api/v1/tools/': 'GET, POST',
                    '/api/v1/users/': 'GET, POST, PUT, DELETE',
                    '/api/v1/social/': 'GET, POST',
                }
            },
            'v2': {
                'status': 'beta',
                'deprecated': False,
                'deprecation_date': None,
                'sunset_date': None,
                'features': ['basic_tools', 'user_management', 'social_media', 'ai_features', 'analytics'],
                'endpoints': {
                    '/api/v2/tools/': 'GET, POST',
                    '/api/v2/users/': 'GET, POST, PUT, DELETE',
                    '/api/v2/social/': 'GET, POST',
                    '/api/v2/ai/': 'GET, POST',
                    '/api/v2/analytics/': 'GET',
                }
            },
            'v3': {
                'status': 'alpha',
                'deprecated': False,
                'deprecation_date': None,
                'sunset_date': None,
                'features': ['basic_tools', 'user_management', 'social_media', 'ai_features', 'analytics', 'microservices'],
                'endpoints': {
                    '/api/v3/tools/': 'GET, POST',
                    '/api/v3/users/': 'GET, POST, PUT, DELETE',
                    '/api/v3/social/': 'GET, POST',
                    '/api/v3/ai/': 'GET, POST',
                    '/api/v3/analytics/': 'GET',
                    '/api/v3/microservices/': 'GET, POST',
                }
            }
        }
    
    def get_version_info(self, version):
        """获取版本信息"""
        return self.versions.get(version, None)
    
    def get_all_versions(self):
        """获取所有版本信息"""
        return self.versions
    
    def is_version_deprecated(self, version):
        """检查版本是否已弃用"""
        version_info = self.get_version_info(version)
        if not version_info:
            return True
        return version_info.get('deprecated', False)
    
    def get_deprecation_warning(self, version):
        """获取弃用警告信息"""
        version_info = self.get_version_info(version)
        if not version_info or not version_info.get('deprecated'):
            return None
        
        return {
            'warning': f'API版本 {version} 已弃用',
            'deprecation_date': version_info.get('deprecation_date'),
            'sunset_date': version_info.get('sunset_date'),
            'migration_guide': f'/docs/api/migration/{version}',
        }


class MicroserviceRegistry:
    """微服务注册表"""
    
    def __init__(self):
        self.services = {
            'user_service': {
                'url': 'http://user-service:8001',
                'health_check': '/health',
                'version': 'v1',
                'status': 'healthy',
                'last_check': timezone.now(),
                'endpoints': ['/api/users/', '/api/auth/'],
            },
            'tool_service': {
                'url': 'http://tool-service:8002',
                'health_check': '/health',
                'version': 'v1',
                'status': 'healthy',
                'last_check': timezone.now(),
                'endpoints': ['/api/tools/', '/api/analytics/'],
            },
            'social_service': {
                'url': 'http://social-service:8003',
                'health_check': '/health',
                'version': 'v1',
                'status': 'healthy',
                'last_check': timezone.now(),
                'endpoints': ['/api/social/', '/api/notifications/'],
            },
            'ai_service': {
                'url': 'http://ai-service:8004',
                'health_check': '/health',
                'version': 'v1',
                'status': 'healthy',
                'last_check': timezone.now(),
                'endpoints': ['/api/ai/', '/api/chat/'],
            }
        }
    
    def register_service(self, service_name, service_info):
        """注册微服务"""
        self.services[service_name] = {
            **service_info,
            'last_check': timezone.now(),
            'status': 'healthy'
        }
        cache.set(f'microservice_{service_name}', service_info, timeout=300)
    
    def get_service(self, service_name):
        """获取微服务信息"""
        return self.services.get(service_name)
    
    def get_all_services(self):
        """获取所有微服务信息"""
        return self.services
    
    def check_service_health(self, service_name):
        """检查微服务健康状态"""
        import requests
        
        service = self.get_service(service_name)
        if not service:
            return False
        
        try:
            response = requests.get(
                f"{service['url']}{service['health_check']}",
                timeout=5
            )
            is_healthy = response.status_code == 200
            self.services[service_name]['status'] = 'healthy' if is_healthy else 'unhealthy'
            self.services[service_name]['last_check'] = timezone.now()
            return is_healthy
        except Exception as e:
            logger.error(f"微服务健康检查失败 {service_name}: {e}")
            self.services[service_name]['status'] = 'unhealthy'
            self.services[service_name]['last_check'] = timezone.now()
            return False


class ServiceDiscovery:
    """服务发现"""
    
    def __init__(self):
        self.registry = MicroserviceRegistry()
    
    def discover_service(self, service_name):
        """发现服务"""
        return self.registry.get_service(service_name)
    
    def route_request(self, service_name, endpoint, method='GET', data=None):
        """路由请求到微服务"""
        import requests
        
        service = self.discover_service(service_name)
        if not service:
            raise ValueError(f"服务 {service_name} 未找到")
        
        if service['status'] != 'healthy':
            raise ConnectionError(f"服务 {service_name} 不健康")
        
        url = f"{service['url']}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            return {
                'status_code': response.status_code,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'headers': dict(response.headers)
            }
        except Exception as e:
            logger.error(f"微服务请求失败 {service_name}: {e}")
            raise


# 全局实例
api_version_manager = APIVersionManager()
service_discovery = ServiceDiscovery()


class APIVersionView(APIView):
    """API版本视图"""
    
    def get(self, request, version=None):
        """获取API版本信息"""
        if version:
            version_info = api_version_manager.get_version_info(version)
            if not version_info:
                return Response(
                    {'error': f'API版本 {version} 不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 检查是否已弃用
            if api_version_manager.is_version_deprecated(version):
                deprecation_warning = api_version_manager.get_deprecation_warning(version)
                return Response({
                    'version': version,
                    'info': version_info,
                    'deprecation_warning': deprecation_warning
                })
            
            return Response({
                'version': version,
                'info': version_info
            })
        else:
            return Response({
                'versions': api_version_manager.get_all_versions(),
                'current_stable': 'v1',
                'latest': 'v3'
            })


class MicroserviceHealthView(APIView):
    """微服务健康检查视图"""
    
    def get(self, request):
        """获取所有微服务健康状态"""
        services = service_discovery.registry.get_all_services()
        health_status = {}
        
        for service_name, service_info in services.items():
            health_status[service_name] = {
                'status': service_info['status'],
                'last_check': service_info['last_check'],
                'url': service_info['url']
            }
        
        return Response({
            'services': health_status,
            'timestamp': timezone.now()
        })


class ServiceProxyView(APIView):
    """服务代理视图"""
    
    def get(self, request, service_name, path=''):
        """代理GET请求到微服务"""
        try:
            result = service_discovery.route_request(
                service_name, 
                f"/{path}", 
                method='GET'
            )
            return Response(result['data'], status=result['status_code'])
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def post(self, request, service_name, path=''):
        """代理POST请求到微服务"""
        try:
            result = service_discovery.route_request(
                service_name, 
                f"/{path}", 
                method='POST',
                data=request.data
            )
            return Response(result['data'], status=result['status_code'])
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


# 中间件：API版本检查
class APIVersionMiddleware:
    """API版本中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查API版本
        if request.path.startswith('/api/'):
            version = self.extract_version(request.path)
            if version and api_version_manager.is_version_deprecated(version):
                deprecation_warning = api_version_manager.get_deprecation_warning(version)
                request.deprecation_warning = deprecation_warning
        
        response = self.get_response(request)
        
        # 添加版本信息到响应头
        if request.path.startswith('/api/'):
            version = self.extract_version(request.path)
            if version:
                response['X-API-Version'] = version
                response['X-API-Status'] = api_version_manager.get_version_info(version).get('status', 'unknown')
        
        return response
    
    def extract_version(self, path):
        """提取API版本"""
        parts = path.split('/')
        if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
            return parts[2]
        return None


# 定时任务：检查微服务健康状态
def check_microservices_health():
    """检查所有微服务健康状态"""
    services = service_discovery.registry.get_all_services()
    
    for service_name in services.keys():
        try:
            service_discovery.registry.check_service_health(service_name)
            logger.info(f"微服务 {service_name} 健康检查完成")
        except Exception as e:
            logger.error(f"微服务 {service_name} 健康检查失败: {e}")


# 工具函数
def get_api_version_from_request(request):
    """从请求中获取API版本"""
    path = request.path
    parts = path.split('/')
    if len(parts) >= 3 and parts[1] == 'api' and parts[2].startswith('v'):
        return parts[2]
    return 'v1'  # 默认版本


def is_api_deprecated(version):
    """检查API版本是否已弃用"""
    return api_version_manager.is_version_deprecated(version)
