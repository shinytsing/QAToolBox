from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
import json

from .error_monitor import error_monitor
from .performance_monitor import system_performance_monitor, api_performance_monitor
from .user_behavior_analyzer import user_behavior_analyzer

class MonitoringDashboardView(View):
    """监控仪表板视图"""
    
    @method_decorator(staff_member_required)
    def get(self, request):
        """显示监控仪表板"""
        context = {
            'title': '系统监控仪表板',
            'current_time': timezone.now().isoformat(),
        }
        return render(request, 'monitoring/dashboard.html', context)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_system_health(request):
    """获取系统健康状态"""
    try:
        health_data = error_monitor.get_system_health()
        return Response({
            'success': True,
            'data': health_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取系统健康状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_performance_metrics(request):
    """获取性能指标"""
    try:
        hours = int(request.GET.get('hours', 24))
        
        # 获取系统性能数据
        system_data = system_performance_monitor.get_performance_dashboard()
        
        # 获取API性能数据
        api_data = api_performance_monitor.get_api_stats(hours)
        
        # 获取系统信息
        system_info = system_performance_monitor.get_system_info()
        
        performance_data = {
            'system': system_data,
            'api': api_data,
            'system_info': system_info,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': performance_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取性能指标失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_error_statistics(request):
    """获取错误统计"""
    try:
        hours = int(request.GET.get('hours', 24))
        
        error_stats = error_monitor.get_error_stats(hours)
        
        return Response({
            'success': True,
            'data': error_stats
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取错误统计失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_analytics(request):
    """获取用户分析数据"""
    try:
        days = int(request.GET.get('days', 30))
        
        # 获取平台分析数据
        platform_analytics = user_behavior_analyzer.get_platform_analytics(days)
        
        return Response({
            'success': True,
            'data': platform_analytics
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取用户分析数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_behavior_profile(request, user_id):
    """获取用户行为画像"""
    try:
        days = int(request.GET.get('days', 30))
        
        user_profile = user_behavior_analyzer.get_user_behavior_profile(user_id, days)
        
        return Response({
            'success': True,
            'data': user_profile
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取用户行为画像失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_monitoring_alerts(request):
    """获取监控告警"""
    try:
        # 获取系统健康状态
        health_data = error_monitor.get_system_health()
        
        # 获取性能数据
        performance_data = system_performance_monitor.get_performance_dashboard()
        
        alerts = []
        
        # 检查系统健康告警
        if health_data.get('status') != 'healthy':
            alerts.append({
                'type': 'system_health',
                'level': 'critical',
                'title': '系统健康异常',
                'message': f"系统状态: {health_data.get('status')}",
                'timestamp': timezone.now().isoformat()
            })
        
        # 检查性能告警
        current_metrics = performance_data.get('current_metrics', {})
        if current_metrics.get('cpu_percent', 0) > 80:
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'title': 'CPU使用率过高',
                'message': f"当前CPU使用率: {current_metrics.get('cpu_percent', 0):.1f}%",
                'timestamp': timezone.now().isoformat()
            })
        
        if current_metrics.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'title': '内存使用率过高',
                'message': f"当前内存使用率: {current_metrics.get('memory_percent', 0):.1f}%",
                'timestamp': timezone.now().isoformat()
            })
        
        if current_metrics.get('disk_percent', 0) > 90:
            alerts.append({
                'type': 'performance',
                'level': 'critical',
                'title': '磁盘使用率过高',
                'message': f"当前磁盘使用率: {current_metrics.get('disk_percent', 0):.1f}%",
                'timestamp': timezone.now().isoformat()
            })
        
        return Response({
            'success': True,
            'data': {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
                'warning_alerts': len([a for a in alerts if a['level'] == 'warning'])
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取监控告警失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def start_monitoring(request):
    """启动监控"""
    try:
        # 启动系统性能监控
        system_performance_monitor.start_monitoring()
        
        return Response({
            'success': True,
            'message': '监控已启动'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'启动监控失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def stop_monitoring(request):
    """停止监控"""
    try:
        # 停止系统性能监控
        system_performance_monitor.stop_monitoring()
        
        return Response({
            'success': True,
            'message': '监控已停止'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'停止监控失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_monitoring_status(request):
    """获取监控状态"""
    try:
        status_data = {
            'system_monitoring': system_performance_monitor.is_monitoring,
            'monitoring_interval': system_performance_monitor.monitoring_interval,
            'alert_thresholds': system_performance_monitor.alert_thresholds,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': status_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取监控状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_real_time_metrics(request):
    """获取实时指标"""
    try:
        # 获取当前系统指标
        current_metrics = {}
        for metric_name in ['cpu_percent', 'memory_percent', 'disk_percent', 'active_users']:
            current_metrics[metric_name] = system_performance_monitor._get_current_metric(metric_name)
        
        # 获取API性能指标
        api_stats = api_performance_monitor.get_api_stats(1)  # 最近1小时
        
        real_time_data = {
            'system_metrics': current_metrics,
            'api_metrics': api_stats,
            'timestamp': timezone.now().isoformat()
        }
        
        return Response({
            'success': True,
            'data': real_time_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取实时指标失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_historical_data(request):
    """获取历史数据"""
    try:
        hours = int(request.GET.get('hours', 24))
        metric_type = request.GET.get('type', 'all')
        
        historical_data = {}
        
        if metric_type in ['all', 'system']:
            # 获取系统历史数据
            system_data = system_performance_monitor.get_performance_dashboard()
            historical_data['system'] = system_data
        
        if metric_type in ['all', 'api']:
            # 获取API历史数据
            api_data = api_performance_monitor.get_api_stats(hours)
            historical_data['api'] = api_data
        
        if metric_type in ['all', 'users']:
            # 获取用户历史数据
            user_data = user_behavior_analyzer.get_platform_analytics(hours // 24)
            historical_data['users'] = user_data
        
        return Response({
            'success': True,
            'data': historical_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取历史数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_alert_thresholds(request):
    """更新告警阈值"""
    try:
        thresholds = request.data.get('thresholds', {})
        
        # 更新系统性能监控阈值
        for key, value in thresholds.items():
            if key in system_performance_monitor.alert_thresholds:
                system_performance_monitor.alert_thresholds[key] = float(value)
        
        return Response({
            'success': True,
            'message': '告警阈值已更新',
            'data': system_performance_monitor.alert_thresholds
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'更新告警阈值失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_monitoring_data(request):
    """导出监控数据"""
    try:
        data_type = request.GET.get('type', 'all')
        format_type = request.GET.get('format', 'json')
        hours = int(request.GET.get('hours', 24))
        
        export_data = {}
        
        if data_type in ['all', 'system']:
            export_data['system'] = system_performance_monitor.get_performance_dashboard()
        
        if data_type in ['all', 'api']:
            export_data['api'] = api_performance_monitor.get_api_stats(hours)
        
        if data_type in ['all', 'users']:
            export_data['users'] = user_behavior_analyzer.get_platform_analytics(hours // 24)
        
        if format_type == 'json':
            return JsonResponse({
                'success': True,
                'data': export_data
            })
        else:
            # 其他格式的导出实现
            return Response({
                'success': False,
                'message': '不支持的导出格式'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'导出监控数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
