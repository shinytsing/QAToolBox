"""
健康检查API视图
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from apps.tools.services.auto_test_runner import health_checker, auto_test_runner
from apps.tools.services.monitoring_service import HealthCheckService
from apps.tools.services.performance_optimizer import performance_optimizer
from apps.tools.services.database_sharding import shard_monitoring
import json


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """健康检查API"""
    try:
        # 运行健康检查
        results = health_checker.run_health_check()
        
        # 检查是否有失败的检查
        failed_checks = [r for r in results.values() if not r['healthy']]
        
        if failed_checks:
            return Response({
                'status': 'unhealthy',
                'message': f'发现 {len(failed_checks)} 个健康检查失败',
                'failed_checks': failed_checks,
                'results': results
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({
                'status': 'healthy',
                'message': '所有健康检查通过',
                'results': results
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'健康检查异常: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def auto_test_status(request):
    """自动化测试状态API"""
    try:
        # 获取测试摘要
        summary = auto_test_runner.get_test_summary()
        
        return Response({
            'auto_test_status': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取测试状态异常: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def run_auto_tests(request):
    """手动运行自动化测试API"""
    try:
        # 启动自动化测试
        auto_test_runner.start_auto_testing()
        
        return Response({
            'status': 'success',
            'message': '自动化测试已启动'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'启动自动化测试失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request):
    """系统状态API"""
    try:
        # 获取各种系统状态
        health_results = health_checker.run_health_check()
        test_summary = auto_test_runner.get_test_summary()
        performance_summary = performance_optimizer.get_optimization_summary()
        
        # 计算整体状态
        health_failures = len([r for r in health_results.values() if not r['healthy']])
        test_failures = test_summary.get('critical_issues', 0)
        
        if health_failures == 0 and test_failures == 0:
            overall_status = 'healthy'
        elif health_failures == 0:
            overall_status = 'warning'
        else:
            overall_status = 'unhealthy'
        
        return Response({
            'overall_status': overall_status,
            'health_check': {
                'status': 'healthy' if health_failures == 0 else 'unhealthy',
                'failed_checks': health_failures,
                'results': health_results
            },
            'auto_test': test_summary,
            'performance': performance_summary,
            'timestamp': test_summary.get('timestamp')
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取系统状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def performance_status(request):
    """性能状态API"""
    try:
        # 获取性能优化摘要
        summary = performance_optimizer.get_optimization_summary()
        
        return Response({
            'performance_status': summary
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取性能状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def shard_status(request):
    """分片状态API"""
    try:
        # 获取分片统计信息
        stats = shard_monitoring.get_shard_stats()
        
        return Response({
            'shard_status': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取分片状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def detailed_health_check(request):
    """详细健康检查API"""
    try:
        # 运行所有健康检查
        health_results = health_checker.run_health_check()
        test_results = auto_test_runner.get_test_results()
        
        # 获取系统资源信息
        import psutil
        system_info = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
        
        # 获取数据库连接信息
        from django.db import connection
        db_info = {
            'connections': len(connection.queries) if hasattr(connection, 'queries') else 0,
        }
        
        # 获取缓存信息
        from django.core.cache import cache
        cache_info = {
            'cache_available': True,
        }
        try:
            cache.set('health_check_test', 'ok', timeout=10)
            cache_info['cache_working'] = cache.get('health_check_test') == 'ok'
        except:
            cache_info['cache_working'] = False
        
        return Response({
            'health_check': health_results,
            'auto_test': test_results,
            'system_info': system_info,
            'database_info': db_info,
            'cache_info': cache_info,
            'timestamp': health_results.get('timestamp') if health_results else None
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'详细健康检查失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 兼容旧版本的视图
@csrf_exempt
@require_http_methods(["GET"])
def legacy_health_check(request):
    """兼容旧版本的健康检查"""
    try:
        results = health_checker.run_health_check()
        failed_checks = [r for r in results.values() if not r['healthy']]
        
        response_data = {
            'status': 'healthy' if len(failed_checks) == 0 else 'unhealthy',
            'timestamp': results.get('timestamp') if results else None,
            'results': results
        }
        
        status_code = 200 if len(failed_checks) == 0 else 503
        
        return JsonResponse(response_data, status=status_code)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


class HealthCheckView(View):
    """健康检查类视图"""
    
    def get(self, request):
        """GET请求处理"""
        try:
            results = health_checker.run_health_check()
            failed_checks = [r for r in results.values() if not r['healthy']]
            
            response_data = {
                'status': 'healthy' if len(failed_checks) == 0 else 'unhealthy',
                'timestamp': results.get('timestamp') if results else None,
                'results': results
            }
            
            status_code = 200 if len(failed_checks) == 0 else 503
            
            return JsonResponse(response_data, status=status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    def post(self, request):
        """POST请求处理"""
        try:
            # 手动触发健康检查
            results = health_checker.run_health_check()
            
            return JsonResponse({
                'status': 'success',
                'message': '健康检查已执行',
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
