from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import FeatureAccess, UserFeatureAccess
from apps.users.models import UserRole

def admin_required(view_func):
    """管理员权限装饰器"""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # 检查是否为超级用户
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # 检查是否有管理员角色
        try:
            user_role = UserRole.objects.get(user=request.user)
            if user_role.role == 'admin':
                return view_func(request, *args, **kwargs)
        except UserRole.DoesNotExist:
            pass
        
        # 没有权限，返回403
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("您没有权限访问此页面")
    
    return _wrapped_view

# 食物照片绑定管理
@login_required
@admin_required
def admin_food_photo_binding(request):
    """管理员食物照片绑定管理页面"""
    return render(request, 'content/admin_food_photo_binding.html', {
        'page_title': '食物照片绑定管理'
    })

# 功能入口管理
@login_required
@admin_required
def admin_feature_management(request):
    """管理员功能入口管理页面"""
    features = FeatureAccess.objects.all().order_by('sort_order', 'feature_name')
    
    context = {
        'features': features,
        'total_features': features.count(),
        'enabled_features': features.filter(is_active=True, status='enabled').count(),
        'disabled_features': features.filter(is_active=False).count(),
        'page_title': '功能入口管理'
    }
    
    return render(request, 'content/admin_feature_management.html', context)

# 功能入口管理API
@csrf_exempt
@require_http_methods(["GET"])
@login_required
@admin_required
def admin_feature_list_api(request):
    """获取功能入口列表API"""
    try:
        features = FeatureAccess.objects.all().order_by('sort_order', 'feature_name')
        
        features_data = []
        for feature in features:
            features_data.append({
                'id': feature.id,
                'feature_key': feature.feature_key,
                'feature_name': feature.feature_name,
                'description': feature.description,
                'url_path': feature.url_path,
                'icon': feature.icon,
                'status': feature.status,
                'status_display': feature.get_status_display(),
                'visibility': feature.visibility,
                'visibility_display': feature.get_visibility_display(),
                'sort_order': feature.sort_order,
                'is_active': feature.is_active,
                'access_count': feature.access_count,
                'created_at': feature.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'features': features_data,
            'total': len(features_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_batch_update_features_api(request):
    """批量更新功能状态API"""
    try:
        data = json.loads(request.body)
        feature_ids = data.get('feature_ids', [])
        action = data.get('action')
        
        if not feature_ids or not action:
            return JsonResponse({
                'success': False,
                'error': '缺少必要参数'
            }, status=400)
        
        features = FeatureAccess.objects.filter(id__in=feature_ids)
        updated_count = 0
        
        if action == 'enable':
            updated_count = features.update(is_active=True, status='enabled')
        elif action == 'disable':
            updated_count = features.update(is_active=False, status='disabled')
        elif action == 'set_public':
            updated_count = features.update(visibility='public')
        elif action == 'set_registered':
            updated_count = features.update(visibility='registered')
        elif action == 'set_admin':
            updated_count = features.update(visibility='admin')
        elif action == 'set_hidden':
            updated_count = features.update(visibility='hidden')
        elif action == 'set_maintenance':
            updated_count = features.update(status='maintenance')
        elif action == 'set_beta':
            updated_count = features.update(status='beta')
        else:
            return JsonResponse({
                'success': False,
                'error': '无效的操作'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': f'已成功更新 {updated_count} 个功能',
            'updated_count': updated_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_update_feature_api(request):
    """更新单个功能API"""
    try:
        data = json.loads(request.body)
        feature_id = data.get('feature_id')
        
        if not feature_id:
            return JsonResponse({
                'success': False,
                'error': '缺少功能ID'
            }, status=400)
        
        feature = FeatureAccess.objects.get(id=feature_id)
        
        # 更新字段
        if 'feature_name' in data:
            feature.feature_name = data['feature_name']
        if 'description' in data:
            feature.description = data['description']
        if 'url_path' in data:
            feature.url_path = data['url_path']
        if 'icon' in data:
            feature.icon = data['icon']
        if 'status' in data:
            feature.status = data['status']
        if 'visibility' in data:
            feature.visibility = data['visibility']
        if 'sort_order' in data:
            feature.sort_order = data['sort_order']
        if 'is_active' in data:
            feature.is_active = data['is_active']
        
        feature.save()
        
        return JsonResponse({
            'success': True,
            'message': '功能更新成功',
            'feature': {
                'id': feature.id,
                'feature_name': feature.feature_name,
                'status': feature.status,
                'status_display': feature.get_status_display(),
                'visibility': feature.visibility,
                'visibility_display': feature.get_visibility_display(),
                'is_active': feature.is_active,
            }
        })
        
    except FeatureAccess.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '功能不存在'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_create_feature_api(request):
    """创建新功能API"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['feature_key', 'feature_name']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必要字段: {field}'
                }, status=400)
        
        # 检查feature_key是否已存在
        if FeatureAccess.objects.filter(feature_key=data['feature_key']).exists():
            return JsonResponse({
                'success': False,
                'error': '功能标识已存在'
            }, status=400)
        
        feature = FeatureAccess.objects.create(
            feature_key=data['feature_key'],
            feature_name=data['feature_name'],
            description=data.get('description', ''),
            url_path=data.get('url_path', ''),
            icon=data.get('icon', 'fas fa-cog'),
            status=data.get('status', 'enabled'),
            visibility=data.get('visibility', 'public'),
            sort_order=data.get('sort_order', 0),
            is_active=data.get('is_active', True),
        )
        
        return JsonResponse({
            'success': True,
            'message': '功能创建成功',
            'feature': {
                'id': feature.id,
                'feature_key': feature.feature_key,
                'feature_name': feature.feature_name,
                'status': feature.status,
                'visibility': feature.visibility,
                'is_active': feature.is_active,
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
@admin_required
def admin_delete_feature_api(request, feature_id):
    """删除功能API"""
    try:
        feature = FeatureAccess.objects.get(id=feature_id)
        feature_name = feature.feature_name
        feature.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'功能 "{feature_name}" 已删除'
        })
        
    except FeatureAccess.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '功能不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def admin_init_default_features_api(request):
    """初始化默认功能API"""
    try:
        default_features = [
            {
                'feature_key': 'food_randomizer',
                'feature_name': '食物随机器',
                'description': '随机推荐美食',
                'url_path': '/tools/food_randomizer/',
                'icon': 'fas fa-utensils',
                'sort_order': 1
            },
            {
                'feature_key': 'meditation_guide',
                'feature_name': '冥想指南',
                'description': '冥想练习和指导',
                'url_path': '/tools/meditation-guide/',
                'icon': 'fas fa-leaf',
                'sort_order': 2
            },
            {
                'feature_key': 'guitar_training',
                'feature_name': '吉他训练',
                'description': '吉他学习和练习',
                'url_path': '/tools/guitar-training/',
                'icon': 'fas fa-guitar',
                'sort_order': 3
            },
            {
                'feature_key': 'life_diary',
                'feature_name': '生活日记',
                'description': '记录生活点滴',
                'url_path': '/tools/life_diary_progressive/',
                'icon': 'fas fa-book',
                'sort_order': 4
            },
            {
                'feature_key': 'food_photo_binding',
                'feature_name': '食物照片绑定',
                'description': '管理食物与照片的映射关系',
                'url_path': '/tools/food-photo-binding/',
                'icon': 'fas fa-camera',
                'visibility': 'admin',
                'sort_order': 100
            },
            {
                'feature_key': 'admin_dashboard',
                'feature_name': '管理员仪表盘',
                'description': '系统管理和监控',
                'url_path': '/content/admin/dashboard/',
                'icon': 'fas fa-tachometer-alt',
                'visibility': 'admin',
                'sort_order': 101
            },
        ]
        
        created_count = 0
        for feature_data in default_features:
            feature, created = FeatureAccess.objects.get_or_create(
                feature_key=feature_data['feature_key'],
                defaults=feature_data
            )
            if created:
                created_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'已创建 {created_count} 个默认功能',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# 用户功能访问管理
@login_required
@admin_required
def admin_user_feature_access(request, user_id):
    """管理员用户功能访问管理页面"""
    user = get_object_or_404(User, id=user_id)
    features = FeatureAccess.objects.all().order_by('sort_order', 'feature_name')
    user_accesses = UserFeatureAccess.objects.filter(user=user).select_related('feature')
    
    context = {
        'target_user': user,
        'features': features,
        'user_accesses': user_accesses,
        'page_title': f'{user.username} 的功能访问权限'
    }
    
    return render(request, 'content/admin_user_feature_access.html', context)

# API函数别名，用于URL配置
feature_list_api = admin_feature_list_api
update_feature_status_api = admin_update_feature_api
batch_update_feature_status_api = admin_batch_update_features_api

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def update_user_feature_access_api(request):
    """更新单个用户功能访问权限API"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        feature_id = data.get('feature_id')
        is_enabled = data.get('is_enabled', True)
        
        if not user_id or not feature_id:
            return JsonResponse({'success': False, 'error': '缺少必要参数'})
        
        user = get_object_or_404(User, id=user_id)
        feature = get_object_or_404(FeatureAccess, id=feature_id)
        
        user_access, created = UserFeatureAccess.objects.get_or_create(
            user=user,
            feature=feature,
            defaults={'is_enabled': is_enabled}
        )
        
        if not created:
            user_access.is_enabled = is_enabled
            user_access.save()
        
        return JsonResponse({
            'success': True,
            'message': f'用户 {user.username} 的功能访问权限已更新'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@admin_required
def batch_update_user_feature_access_api(request):
    """批量更新用户功能访问权限API"""
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        feature_ids = data.get('feature_ids', [])
        action = data.get('action')  # 'enable', 'disable'
        
        if not user_ids or not feature_ids or not action:
            return JsonResponse({'success': False, 'error': '参数不完整'})
        
        updated_count = 0
        for user_id in user_ids:
            for feature_id in feature_ids:
                user_access, created = UserFeatureAccess.objects.get_or_create(
                    user_id=user_id,
                    feature_id=feature_id,
                    defaults={'is_enabled': action == 'enable'}
                )
                if not created:
                    user_access.is_enabled = action == 'enable'
                    user_access.save()
                updated_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'成功更新 {updated_count} 条用户功能访问权限'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
