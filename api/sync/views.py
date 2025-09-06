from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.core.cache import cache
import json

from .models import SyncLog, DataVersion
from .serializers import SyncLogSerializer, DataVersionSerializer
from .utils import (
    sync_fitness_data,
    sync_life_data,
    sync_social_data,
    sync_geek_data,
    get_last_sync_time,
    update_sync_time,
    resolve_conflicts
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_data(request):
    """数据同步接口"""
    try:
        sync_type = request.data.get('sync_type', 'all')
        device_id = request.data.get('device_id', '')
        last_sync_time = request.data.get('last_sync_time')
        data = request.data.get('data', {})
        
        # 验证设备ID
        if not device_id:
            return Response({
                'success': False,
                'message': '设备ID不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取上次同步时间
        if not last_sync_time:
            last_sync_time = get_last_sync_time(request.user, device_id)
        
        sync_result = {
            'fitness': {},
            'life': {},
            'social': {},
            'geek': {},
            'conflicts': []
        }
        
        with transaction.atomic():
            # 同步健身数据
            if sync_type in ['all', 'fitness']:
                fitness_result = sync_fitness_data(
                    request.user, 
                    data.get('fitness', {}), 
                    last_sync_time
                )
                sync_result['fitness'] = fitness_result
            
            # 同步生活数据
            if sync_type in ['all', 'life']:
                life_result = sync_life_data(
                    request.user, 
                    data.get('life', {}), 
                    last_sync_time
                )
                sync_result['life'] = life_result
            
            # 同步社交数据
            if sync_type in ['all', 'social']:
                social_result = sync_social_data(
                    request.user, 
                    data.get('social', {}), 
                    last_sync_time
                )
                sync_result['social'] = social_result
            
            # 同步极客工具数据
            if sync_type in ['all', 'geek']:
                geek_result = sync_geek_data(
                    request.user, 
                    data.get('geek', {}), 
                    last_sync_time
                )
                sync_result['geek'] = geek_result
            
            # 处理冲突
            conflicts = resolve_conflicts(request.user, sync_result)
            sync_result['conflicts'] = conflicts
            
            # 更新同步时间
            update_sync_time(request.user, device_id)
            
            # 记录同步日志
            SyncLog.objects.create(
                user=request.user,
                device_id=device_id,
                sync_type=sync_type,
                status='success',
                data_count=sum(len(v) for v in sync_result.values() if isinstance(v, dict))
            )
        
        return Response({
            'success': True,
            'message': '数据同步成功',
            'data': sync_result,
            'sync_time': timezone.now().isoformat()
        })
        
    except Exception as e:
        # 记录失败日志
        SyncLog.objects.create(
            user=request.user,
            device_id=device_id,
            sync_type=sync_type,
            status='failed',
            error_message=str(e)
        )
        
        return Response({
            'success': False,
            'message': f'数据同步失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sync_status(request):
    """获取同步状态"""
    try:
        device_id = request.query_params.get('device_id', '')
        
        # 获取各模块的数据版本
        versions = DataVersion.objects.filter(user=request.user)
        version_data = DataVersionSerializer(versions, many=True).data
        
        # 获取上次同步时间
        last_sync_time = get_last_sync_time(request.user, device_id)
        
        # 获取同步日志
        recent_logs = SyncLog.objects.filter(
            user=request.user,
            device_id=device_id
        ).order_by('-created_at')[:10]
        
        log_data = SyncLogSerializer(recent_logs, many=True).data
        
        return Response({
            'success': True,
            'data': {
                'versions': version_data,
                'last_sync_time': last_sync_time,
                'recent_logs': log_data
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'获取同步状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_conflict(request):
    """解决数据冲突"""
    try:
        conflict_id = request.data.get('conflict_id')
        resolution = request.data.get('resolution')  # 'server', 'client', 'merge'
        
        if not conflict_id or not resolution:
            return Response({
                'success': False,
                'message': '冲突ID和解决方案不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取冲突数据
        conflict_data = cache.get(f'conflict_{conflict_id}')
        if not conflict_data:
            return Response({
                'success': False,
                'message': '冲突数据不存在或已过期'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 根据解决方案处理冲突
        if resolution == 'server':
            # 使用服务器数据
            result = conflict_data['server_data']
        elif resolution == 'client':
            # 使用客户端数据
            result = conflict_data['client_data']
        elif resolution == 'merge':
            # 合并数据
            result = merge_data(
                conflict_data['server_data'],
                conflict_data['client_data']
            )
        else:
            return Response({
                'success': False,
                'message': '无效的解决方案'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存解决后的数据
        save_resolved_data(request.user, conflict_data['data_type'], result)
        
        # 清除冲突缓存
        cache.delete(f'conflict_{conflict_id}')
        
        return Response({
            'success': True,
            'message': '冲突解决成功',
            'data': result
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'解决冲突失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_sync(request):
    """强制同步所有数据"""
    try:
        device_id = request.data.get('device_id', '')
        
        if not device_id:
            return Response({
                'success': False,
                'message': '设备ID不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 清除缓存
        cache.delete(f'last_sync_{request.user.id}_{device_id}')
        
        # 获取所有数据
        all_data = {
            'fitness': get_all_fitness_data(request.user),
            'life': get_all_life_data(request.user),
            'social': get_all_social_data(request.user),
            'geek': get_all_geek_data(request.user)
        }
        
        # 更新数据版本
        for data_type, data in all_data.items():
            DataVersion.objects.update_or_create(
                user=request.user,
                data_type=data_type,
                defaults={
                    'version': timezone.now().timestamp(),
                    'data_count': len(data) if isinstance(data, list) else 1
                }
            )
        
        return Response({
            'success': True,
            'message': '强制同步成功',
            'data': all_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'强制同步失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def merge_data(server_data, client_data):
    """合并数据"""
    # 简单的合并策略：以时间戳为准，保留最新的数据
    if isinstance(server_data, dict) and isinstance(client_data, dict):
        merged = server_data.copy()
        for key, value in client_data.items():
            if key not in merged or value.get('updated_at', 0) > merged.get(key, {}).get('updated_at', 0):
                merged[key] = value
        return merged
    elif isinstance(server_data, list) and isinstance(client_data, list):
        # 对于列表，合并并去重
        merged = server_data.copy()
        for item in client_data:
            if item not in merged:
                merged.append(item)
        return merged
    else:
        # 对于其他类型，返回客户端数据
        return client_data

def save_resolved_data(user, data_type, data):
    """保存解决后的数据"""
    # 根据数据类型保存到相应的模型
    if data_type == 'fitness':
        # 保存健身数据
        pass
    elif data_type == 'life':
        # 保存生活数据
        pass
    elif data_type == 'social':
        # 保存社交数据
        pass
    elif data_type == 'geek':
        # 保存极客工具数据
        pass

def get_all_fitness_data(user):
    """获取所有健身数据"""
    from api.v1.fitness.models import FitnessWorkout, FitnessProfile
    # 实现获取所有健身数据的逻辑
    return []

def get_all_life_data(user):
    """获取所有生活数据"""
    from api.v1.life.models import LifeDiary, CheckIn
    # 实现获取所有生活数据的逻辑
    return []

def get_all_social_data(user):
    """获取所有社交数据"""
    from api.v1.social.models import ChatMessage, HeartLink
    # 实现获取所有社交数据的逻辑
    return []

def get_all_geek_data(user):
    """获取所有极客工具数据"""
    from api.v1.tools.models import PDFConversion, WebCrawler
    # 实现获取所有极客工具数据的逻辑
    return []
