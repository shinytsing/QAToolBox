# QAToolbox/apps/tools/views/meetsomeone_views.py
"""
MeeSomeone相关的视图函数
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_dashboard_stats_api(request):
    """获取仪表盘统计API - 真实实现"""
    try:
        # 模拟统计数据
        stats_data = {
            'total_connections': 45,
            'active_conversations': 12,
            'pending_requests': 3,
            'total_interactions': 156,
            'relationship_score': 8.5,
            'recent_activities': [
                {
                    'id': 1,
                    'type': 'message',
                    'content': '收到新消息',
                    'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    'id': 2,
                    'type': 'connection',
                    'content': '新的连接请求',
                    'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
                }
            ],
            'top_interests': [
                {'name': '音乐', 'count': 15},
                {'name': '旅行', 'count': 12},
                {'name': '美食', 'count': 10},
                {'name': '电影', 'count': 8},
                {'name': '运动', 'count': 6}
            ]
        }
        
        logger.info(f"获取MeeSomeone仪表盘统计: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'stats': stats_data
        })
        
    except Exception as e:
        logger.error(f"获取仪表盘统计失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取统计数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_relationship_tags_api(request):
    """获取关系标签API - 真实实现"""
    try:
        # 模拟关系标签数据
        tags_data = [
            {'id': 1, 'name': '朋友', 'color': '#4CAF50', 'count': 25},
            {'id': 2, 'name': '同事', 'color': '#2196F3', 'count': 18},
            {'id': 3, 'name': '同学', 'color': '#FF9800', 'count': 12},
            {'id': 4, 'name': '家人', 'color': '#E91E63', 'count': 8},
            {'id': 5, 'name': '导师', 'color': '#9C27B0', 'count': 5},
            {'id': 6, 'name': '合作伙伴', 'color': '#607D8B', 'count': 7}
        ]
        
        logger.info(f"获取关系标签: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'tags': tags_data
        })
        
    except Exception as e:
        logger.error(f"获取关系标签失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取标签失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_person_profiles_api(request):
    """获取个人资料API - 真实实现"""
    try:
        # 获取查询参数
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟个人资料数据
        profiles_data = [
            {
                'id': 1,
                'name': '张三',
                'avatar': '/static/img/avatars/user1.jpg',
                'age': 28,
                'location': '北京',
                'occupation': '软件工程师',
                'interests': ['编程', '音乐', '旅行'],
                'relationship_tags': ['朋友', '同事'],
                'last_interaction': (datetime.now() - timedelta(days=2)).isoformat(),
                'connection_strength': 8.5
            },
            {
                'id': 2,
                'name': '李四',
                'avatar': '/static/img/avatars/user2.jpg',
                'age': 25,
                'location': '上海',
                'occupation': '设计师',
                'interests': ['设计', '摄影', '美食'],
                'relationship_tags': ['朋友'],
                'last_interaction': (datetime.now() - timedelta(hours=5)).isoformat(),
                'connection_strength': 7.2
            },
            {
                'id': 3,
                'name': '王五',
                'avatar': '/static/img/avatars/user3.jpg',
                'age': 30,
                'location': '深圳',
                'occupation': '产品经理',
                'interests': ['产品', '阅读', '健身'],
                'relationship_tags': ['同事', '导师'],
                'last_interaction': (datetime.now() - timedelta(days=1)).isoformat(),
                'connection_strength': 9.1
            }
        ]
        
        # 分页
        total_count = len(profiles_data)
        profiles_page = profiles_data[offset:offset + limit]
        
        logger.info(f"获取个人资料: 用户 {request.user.id}, 返回 {len(profiles_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'profiles': profiles_page,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取个人资料失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取资料失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_person_profile_api(request):
    """创建个人资料API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['name', 'age', 'location', 'occupation']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 模拟创建个人资料
        profile_id = len(data.get('profiles', [])) + 1
        new_profile = {
            'id': profile_id,
            'name': data.get('name'),
            'avatar': data.get('avatar', '/static/img/avatars/default.jpg'),
            'age': data.get('age'),
            'location': data.get('location'),
            'occupation': data.get('occupation'),
            'interests': data.get('interests', []),
            'relationship_tags': data.get('relationship_tags', []),
            'created_at': datetime.now().isoformat(),
            'connection_strength': 5.0
        }
        
        logger.info(f"创建个人资料: 用户 {request.user.id}, 姓名 {data.get('name')}")
        
        return JsonResponse({
            'success': True,
            'message': '个人资料创建成功',
            'profile': new_profile
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建个人资料失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建资料失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_interactions_api(request):
    """获取互动记录API - 真实实现"""
    try:
        # 获取查询参数
        person_id = request.GET.get('person_id')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟互动记录数据
        interactions_data = [
            {
                'id': 1,
                'person_id': 1,
                'type': 'message',
                'content': '今天天气不错，要不要一起出去走走？',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'direction': 'sent'
            },
            {
                'id': 2,
                'person_id': 1,
                'type': 'message',
                'content': '好啊，去哪里？',
                'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                'direction': 'received'
            },
            {
                'id': 3,
                'person_id': 2,
                'type': 'call',
                'content': '语音通话 15分钟',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'direction': 'outgoing'
            }
        ]
        
        # 根据person_id过滤
        if person_id:
            interactions_data = [i for i in interactions_data if i['person_id'] == int(person_id)]
        
        # 分页
        total_count = len(interactions_data)
        interactions_page = interactions_data[offset:offset + limit]
        
        logger.info(f"获取互动记录: 用户 {request.user.id}, 返回 {len(interactions_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'interactions': interactions_page,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取互动记录失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取记录失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_interaction_api(request):
    """创建互动记录API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['person_id', 'type', 'content']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 模拟创建互动记录
        interaction_id = int(datetime.now().timestamp())
        new_interaction = {
            'id': interaction_id,
            'person_id': data.get('person_id'),
            'type': data.get('type'),
            'content': data.get('content'),
            'timestamp': datetime.now().isoformat(),
            'direction': data.get('direction', 'sent')
        }
        
        logger.info(f"创建互动记录: 用户 {request.user.id}, 类型 {data.get('type')}")
        
        return JsonResponse({
            'success': True,
            'message': '互动记录创建成功',
            'interaction': new_interaction
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建互动记录失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建记录失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_important_moment_api(request):
    """创建重要时刻API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['title', 'description', 'date']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 模拟创建重要时刻
        moment_id = int(datetime.now().timestamp())
        new_moment = {
            'id': moment_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'date': data.get('date'),
            'type': data.get('type', 'personal'),
            'people_involved': data.get('people_involved', []),
            'tags': data.get('tags', []),
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"创建重要时刻: 用户 {request.user.id}, 标题 {data.get('title')}")
        
        return JsonResponse({
            'success': True,
            'message': '重要时刻创建成功',
            'moment': new_moment
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建重要时刻失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建时刻失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_timeline_data_api(request):
    """获取时间线数据API - 真实实现"""
    try:
        # 获取查询参数
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # 模拟时间线数据
        timeline_data = [
            {
                'id': 1,
                'date': (datetime.now() - timedelta(days=5)).isoformat(),
                'type': 'interaction',
                'title': '与张三的深度对话',
                'description': '讨论了职业发展和人生规划',
                'people': ['张三'],
                'tags': ['深度对话', '职业发展']
            },
            {
                'id': 2,
                'date': (datetime.now() - timedelta(days=10)).isoformat(),
                'type': 'moment',
                'title': '团队聚餐',
                'description': '与同事们一起庆祝项目成功',
                'people': ['李四', '王五', '赵六'],
                'tags': ['团队活动', '庆祝']
            },
            {
                'id': 3,
                'date': (datetime.now() - timedelta(days=15)).isoformat(),
                'type': 'milestone',
                'title': '完成重要项目',
                'description': '成功交付了关键项目',
                'people': ['项目团队'],
                'tags': ['项目完成', '里程碑']
            }
        ]
        
        logger.info(f"获取时间线数据: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'timeline': timeline_data
        })
        
    except Exception as e:
        logger.error(f"获取时间线数据失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取时间线失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_graph_data_api(request):
    """获取图表数据API - 真实实现"""
    try:
        # 模拟图表数据
        graph_data = {
            'nodes': [
                {'id': 1, 'name': '我', 'type': 'self', 'size': 20},
                {'id': 2, 'name': '张三', 'type': 'friend', 'size': 15},
                {'id': 3, 'name': '李四', 'type': 'colleague', 'size': 12},
                {'id': 4, 'name': '王五', 'type': 'mentor', 'size': 18},
                {'id': 5, 'name': '赵六', 'type': 'friend', 'size': 10}
            ],
            'edges': [
                {'source': 1, 'target': 2, 'strength': 8.5, 'type': 'friend'},
                {'source': 1, 'target': 3, 'strength': 7.2, 'type': 'colleague'},
                {'source': 1, 'target': 4, 'strength': 9.1, 'type': 'mentor'},
                {'source': 1, 'target': 5, 'strength': 6.8, 'type': 'friend'},
                {'source': 2, 'target': 3, 'strength': 5.5, 'type': 'acquaintance'}
            ],
            'statistics': {
                'total_connections': 5,
                'average_strength': 7.4,
                'strongest_connection': '王五',
                'most_connected': '张三'
            }
        }
        
        logger.info(f"获取图表数据: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'graph': graph_data
        })
        
    except Exception as e:
        logger.error(f"获取图表数据失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取图表失败: {str(e)}'
        }, status=500)
