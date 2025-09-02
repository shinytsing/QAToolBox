# QAToolbox/apps/tools/views/food_views.py

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
def api_foods(request):
    """获取食物列表API - 真实实现"""
    try:
        # 获取查询参数
        query = request.GET.get('query', '')
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 200))
        
        # 获取真实的食物数据
        from apps.tools.models.legacy_models import FoodItem
        
        food_database = []
        try:
            # 获取所有食物
            foods = FoodItem.objects.all()
            for food in foods:
                                       food_database.append({
                           'id': food.id,
                           'name': food.name,
                           'english_name': '',  # 模型中没有这个字段
                           'category': food.cuisine or 'other',
                           'calories': food.calories or 0,
                           'protein': food.protein or 0,
                           'fat': food.fat or 0,
                           'carbohydrates': food.carbohydrates or 0,
                           'fiber': food.fiber or 0,
                           'sugar': food.sugar or 0,
                           'vitamin_c': 0,  # 模型中没有这个字段
                           'potassium': 0,  # 模型中没有这个字段
                           'image_url': food.image_url or '/static/img/food/default-food.svg',
                           'description': food.description or '',
                           'tags': food.tags if isinstance(food.tags, list) else []
                       })
        except Exception as e:
            # 如果数据库中没有数据，返回空数组
            food_database = []
        
        # 应用筛选
        filtered_foods = food_database
        
        # 按查询条件筛选
        if query:
            filtered_foods = [food for food in filtered_foods if query.lower() in food['name'].lower()]
        
        if category != 'all':
            filtered_foods = [food for food in filtered_foods if food['category'] == category]
        
        # 限制结果数量
        filtered_foods = filtered_foods[:limit]
        
        logger.info(f"获取食物列表: 查询 '{query}', 类别 '{category}', 返回 {len(filtered_foods)} 条记录")
        
        return JsonResponse(filtered_foods, safe=False)
        
    except Exception as e:
        logger.error(f"获取食物列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物列表失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_food_photo_bindings(request):
    """获取食物照片绑定API - 真实实现"""
    try:
        # 获取查询参数
        user_id = request.GET.get('user_id', request.user.id)
        limit = int(request.GET.get('limit', 20))
        
        # 获取真实的食物照片绑定数据
        from apps.tools.models.legacy_models import FoodPhotoBinding
        
        bindings_data = []
        try:
            # 获取所有绑定关系
            photo_bindings = FoodPhotoBinding.objects.all()
            for binding in photo_bindings:
                bindings_data.append({
                    'id': binding.id,
                    'food_id': binding.food_item.id if binding.food_item else None,
                    'food_name': binding.food_item.name if binding.food_item else '未知食物',
                    'photo_name': binding.photo_name,
                    'photo_url': binding.photo_url,
                    'created_at': binding.created_at.isoformat() if binding.created_at else None,
                })
        except Exception as e:
            # 如果数据库中没有数据，返回空数组
            bindings_data = []
        
        # 限制结果数量
        bindings_data = bindings_data[:limit]
        
        # 计算统计信息
        total_bindings = len(bindings_data)
        
        logger.info(f"获取食物照片绑定: 用户 {user_id}, 返回 {total_bindings} 条记录")
        
        return JsonResponse(bindings_data, safe=False)
        
    except Exception as e:
        logger.error(f"获取食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物照片绑定失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_save_food_photo_bindings(request):
    """保存食物照片绑定API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        bindings = data.get('bindings', [])
        
        if not bindings:
            return JsonResponse({
                'success': False,
                'error': '没有提供绑定数据'
            }, status=400)
        
        # 验证绑定数据
        for binding in bindings:
            required_fields = ['food_id', 'photo_name']
            for field in required_fields:
                if field not in binding:
                    return JsonResponse({
                        'success': False,
                        'error': f'缺少必需字段: {field}'
                    }, status=400)
        
        # 获取真实的食物照片绑定数据
        from apps.tools.models.legacy_models import FoodPhotoBinding, FoodItem
        
        saved_bindings = []
        for binding in bindings:
            try:
                # 获取食物对象
                food_item = FoodItem.objects.get(id=binding['food_id'])
                
                # 查找或创建绑定记录
                photo_binding, created = FoodPhotoBinding.objects.get_or_create(
                    food_item=food_item,
                    defaults={
                        'photo_name': binding['photo_name'],
                        'photo_url': f'/media/food_photos/{binding["photo_name"]}',
                        'accuracy_score': 1.0,  # 手动绑定的准确度为1.0
                        'created_by': request.user,
                        'binding_source': 'manual',
                    }
                )
                
                if not created:
                    # 更新现有绑定
                    photo_binding.photo_name = binding['photo_name']
                    photo_binding.photo_url = f'/media/food_photos/{binding["photo_name"]}'
                    photo_binding.accuracy_score = 1.0
                    photo_binding.binding_source = 'manual'
                    photo_binding.save()
                
                saved_bindings.append({
                    'id': photo_binding.id,
                    'food_id': food_item.id,
                    'food_name': food_item.name,
                    'photo_name': photo_binding.photo_name,
                    'photo_url': photo_binding.photo_url,
                    'created': created
                })
                
            except FoodItem.DoesNotExist:
                logger.warning(f"食物ID {binding['food_id']} 不存在")
                continue
            except Exception as e:
                logger.error(f"保存绑定失败: {str(e)}")
                continue
        
        logger.info(f"保存食物照片绑定: 用户 {request.user.id}, 保存 {len(saved_bindings)} 条记录")
        
        return JsonResponse({
            'success': True,
            'message': f'成功保存 {len(saved_bindings)} 条绑定记录',
            'bindings': saved_bindings
        })
        
    except Exception as e:
        logger.error(f"保存食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_upload_food_photo(request):
    """上传食物照片API"""
    try:
        if 'photo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': '没有上传文件'
            }, status=400)
        
        photo_file = request.FILES['photo']
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if photo_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': '不支持的文件类型，请上传图片文件'
            }, status=400)
        
        # 验证文件大小 (最大10MB)
        if photo_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': '文件大小不能超过10MB'
            }, status=400)
        
        # 生成文件名
        import uuid
        import os
        from django.core.files.storage import default_storage
        
        file_extension = os.path.splitext(photo_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 保存文件
        file_path = f"food_photos/{unique_filename}"
        saved_path = default_storage.save(file_path, photo_file)
        
        # 获取文件URL
        file_url = default_storage.url(saved_path)
        
        logger.info(f"上传食物照片: 用户 {request.user.id}, 文件 {unique_filename}")
        
        return JsonResponse({
            'success': True,
            'message': '照片上传成功',
            'data': {
                'filename': unique_filename,
                'url': file_url,
                'size': photo_file.size,
                'content_type': photo_file.content_type
            }
        })
        
    except Exception as e:
        logger.error(f"上传食物照片失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_remove_food_photo_binding(request):
    """删除食物照片绑定API"""
    try:
        data = json.loads(request.body)
        photo_name = data.get('photo_name')
        
        if not photo_name:
            return JsonResponse({
                'success': False,
                'error': '缺少照片名称'
            }, status=400)
        
        from apps.tools.models.legacy_models import FoodPhotoBinding
        
        # 查找并删除绑定
        bindings = FoodPhotoBinding.objects.filter(photo_name=photo_name)
        deleted_count = bindings.count()
        
        if deleted_count > 0:
            bindings.delete()
            logger.info(f"删除食物照片绑定: 用户 {request.user.id}, 照片 {photo_name}, 删除 {deleted_count} 条记录")
            
            return JsonResponse({
                'success': True,
                'message': f'成功删除 {deleted_count} 条绑定记录',
                'deleted_count': deleted_count
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '未找到要删除的绑定'
            }, status=404)
            
    except Exception as e:
        logger.error(f"删除食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }, status=500)

@login_required
def food_photo_binding_view(request):
    """食物照片绑定页面"""
    from django.shortcuts import render
    return render(request, 'tools/food_photo_binding.html')