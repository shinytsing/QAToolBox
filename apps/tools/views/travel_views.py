"""
旅游相关视图
包含旅游攻略、旅游API、旅游数据管理等功能
"""

import json
import time
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.cache import cache

# 导入相关模型
try:
    from apps.tools.models import TravelGuide
except ImportError:
    # 如果模型不存在，使用空类
    class TravelGuide:
        pass


def travel_guide(request):
    """旅游攻略页面"""
    return render(request, 'tools/travel_guide.html')


@csrf_exempt
@require_http_methods(["GET"])
def check_local_travel_data_api(request):
    """检测本地旅游数据API"""
    try:
        destination = request.GET.get('destination', '').strip()
        
        if not destination:
            return JsonResponse({
                'has_local_data': False,
                'message': '请输入目的地'
            })
        
        # 检查是否有本地数据
        try:
            from .services.enhanced_travel_service_v2 import MultiAPITravelService
            
            service = MultiAPITravelService()
            has_local_data = destination in service.real_travel_data
            
            return JsonResponse({
                'has_local_data': has_local_data,
                'destination': destination,
                'message': f'{"有" if has_local_data else "没有"}本地数据'
            })
            
        except Exception as e:
            print(f"检测本地数据失败: {e}")
            return JsonResponse({
                'has_local_data': False,
                'message': '检测失败，默认显示标准模式'
            })
            
    except Exception as e:
        return JsonResponse({
            'has_local_data': False,
            'message': f'检测失败: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def travel_guide_api(request):
    """旅游攻略API - 优先使用本地数据，否则使用DeepSeek功能"""
    try:
        # 检查用户是否已登录
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': '请先登录后再使用此功能'
            }, status=401)
        
        data = json.loads(request.body)
        destination = data.get('destination', '').strip()
        travel_style = data.get('travel_style', 'general')
        budget_min = data.get('budget_min', 3000)  # 预算最小值
        budget_max = data.get('budget_max', 8000)  # 预算最大值
        budget_amount = data.get('budget_amount', 5000)  # 新增具体预算金额（平均值）
        budget_range = data.get('budget_range', 'medium')  # 保留分类，用于兼容
        travel_duration = data.get('travel_duration', '3-5天')
        interests = data.get('interests', [])
        fast_mode = data.get('fast_mode', False)  # 新增快速模式选项
        
        # 后端预算范围校验
        validation_error = validate_budget_range(budget_min, budget_max)
        if validation_error:
            return JsonResponse({'error': validation_error}, status=400)
        
        if not destination:
            return JsonResponse({'error': '请输入目的地'}, status=400)
        
        # 生成旅游攻略内容
        try:
            # 使用新的多API服务 - 延迟创建实例以避免启动时的API调用
            from .services.enhanced_travel_service_v2 import MultiAPITravelService
            
            # 只在需要时创建服务实例
            service = None
            try:
                service = MultiAPITravelService()
                
                # 检查是否有本地数据
                has_local_data = destination in service.real_travel_data
                
                # 如果有本地数据，优先使用本地数据
                if has_local_data:
                    print(f"✅ {destination}有本地数据，使用本地数据生成攻略")
                    guide_content = service.get_travel_guide_with_local_data(
                        destination=destination,
                        travel_style=travel_style,
                        budget_min=budget_min,
                        budget_max=budget_max,
                        budget_amount=budget_amount,
                        budget_range=budget_range,
                        travel_duration=travel_duration,
                        interests=interests,
                        fast_mode=fast_mode
                    )
                else:
                    print(f"❌ {destination}没有本地数据，使用DeepSeek功能")
                    guide_content = service.get_travel_guide(
                        destination=destination,
                        travel_style=travel_style,
                        budget_min=budget_min,
                        budget_max=budget_max,
                        budget_amount=budget_amount,
                        budget_range=budget_range,
                        travel_duration=travel_duration,
                        interests=interests,
                        fast_mode=fast_mode
                    )
                    
            except Exception as service_error:
                # 如果服务创建失败，使用备用方案
                print(f"旅游服务创建失败，使用备用方案: {service_error}")
                guide_content = {
                    'must_visit_attractions': [],
                    'food_recommendations': [],
                    'transportation_guide': '暂无交通信息',
                    'hidden_gems': [],
                    'weather_info': {},
                    'best_time_to_visit': '全年适合',
                    'budget_estimate': {},
                    'travel_tips': ['请稍后重试'],
                    'detailed_guide': '服务暂时不可用，请稍后重试',
                    'daily_schedule': [],
                    'activity_timeline': [],
                    'cost_breakdown': {}
                }
            
            # 过滤掉TravelGuide模型中不存在的字段
            valid_fields = {
                'must_visit_attractions', 'food_recommendations', 'transportation_guide',
                'hidden_gems', 'weather_info', 'destination_info', 'currency_info', 'timezone_info',
                'best_time_to_visit', 'budget_estimate', 'travel_tips',
                'detailed_guide', 'daily_schedule', 'activity_timeline', 'cost_breakdown'
            }
            filtered_content = {k: v for k, v in guide_content.items() if k in valid_fields}
            
            # 保存到数据库
            travel_guide = TravelGuide.objects.create(
                user=request.user,
                destination=destination,
                travel_style=travel_style,
                budget_min=budget_min,
                budget_max=budget_max,
                budget_amount=budget_amount,
                budget_range=budget_range,
                travel_duration=travel_duration,
                interests=interests,
                **filtered_content
            )
            
            # 构建响应数据
            response_data = {
                'id': travel_guide.id,
                'destination': travel_guide.destination,
                'must_visit_attractions': travel_guide.must_visit_attractions,
                'food_recommendations': travel_guide.food_recommendations,
                'transportation_guide': travel_guide.transportation_guide,
                'hidden_gems': travel_guide.hidden_gems,
                'weather_info': travel_guide.weather_info,
                'destination_info': travel_guide.destination_info,
                'currency_info': travel_guide.currency_info,
                'timezone_info': travel_guide.timezone_info,
                'best_time_to_visit': travel_guide.best_time_to_visit,
                'budget_estimate': travel_guide.budget_estimate,
                'travel_tips': travel_guide.travel_tips,
                'detailed_guide': travel_guide.detailed_guide,
                'daily_schedule': travel_guide.daily_schedule,
                'activity_timeline': travel_guide.activity_timeline,
                'cost_breakdown': travel_guide.cost_breakdown,
                'created_at': travel_guide.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            
            # 添加缓存和API信息
            if hasattr(guide_content, 'get'):
                response_data.update({
                    'is_cached': guide_content.get('is_cached', False),
                    'api_used': guide_content.get('api_used', 'unknown'),
                    'generation_time': guide_content.get('generation_time', 0),
                    'generation_mode': guide_content.get('generation_mode', 'standard'),
                    'data_quality_score': guide_content.get('data_quality_score', 0.0),
                    'usage_count': guide_content.get('usage_count', 0),
                    'cached_at': guide_content.get('cached_at'),
                    'expires_at': guide_content.get('expires_at'),
                    'data_source': 'local' if has_local_data else 'deepseek'
                })
            
            return JsonResponse({
                'success': True,
                'guide_id': travel_guide.id,
                'guide': response_data
            })
        except Exception as e:
            error_message = str(e)
            if "无法获取有效的旅游数据" in error_message or "API" in error_message:
                return JsonResponse({
                    'error': '服务暂时不可用，请稍后重试。错误详情：' + error_message
                }, status=503)  # 503 Service Unavailable
            else:
                return JsonResponse({
                    'error': '生成攻略失败：' + error_message
                }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        print(f"生成旅游攻略失败: {str(e)}")
        return JsonResponse({'error': f'生成攻略失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_travel_guides_api(request):
    """获取用户的旅游攻略列表"""
    try:
        guides = TravelGuide.objects.filter(user=request.user).order_by('-created_at')
        guides_data = []
        
        for guide in guides:
            try:
                # 安全地获取计数，避免None值错误
                attractions_count = len(guide.must_visit_attractions) if guide.must_visit_attractions else 0
                food_count = len(guide.food_recommendations) if guide.food_recommendations else 0
                hidden_gems_count = len(guide.hidden_gems) if guide.hidden_gems else 0
                
                guides_data.append({
                    'id': guide.id,
                    'destination': guide.destination,
                    'travel_style': guide.travel_style,
                    'budget_range': guide.budget_range,
                    'travel_duration': guide.travel_duration,
                    'attractions_count': attractions_count,
                    'food_count': food_count,
                    'hidden_gems_count': hidden_gems_count,
                    'is_favorite': guide.is_favorite,
                    'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
                })
            except Exception as guide_error:
                print(f"处理攻略 {guide.id} 时出错: {str(guide_error)}")
                # 跳过有问题的攻略，继续处理其他攻略
                continue
        
        return JsonResponse({
            'success': True,
            'guides': guides_data
        })
        
    except Exception as e:
        print(f"获取旅游攻略列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'获取攻略列表失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_travel_guide_detail_api(request, guide_id):
    """获取旅游攻略详情"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'guide': {
                'id': guide.id,
                'destination': guide.destination,
                'must_visit_attractions': guide.must_visit_attractions,
                'food_recommendations': guide.food_recommendations,
                'transportation_guide': guide.transportation_guide,
                'hidden_gems': guide.hidden_gems,
                'weather_info': guide.weather_info,
                'best_time_to_visit': guide.best_time_to_visit,
                'budget_estimate': guide.budget_estimate,
                'travel_tips': guide.travel_tips,
                'travel_style': guide.travel_style,
                'budget_range': guide.budget_range,
                'travel_duration': guide.travel_duration,
                'interests': guide.interests,
                'is_favorite': guide.is_favorite,
                'created_at': guide.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"获取旅游攻略详情失败: {str(e)}")
        return JsonResponse({'error': f'获取攻略详情失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def toggle_favorite_guide_api(request, guide_id):
    """切换攻略收藏状态"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        guide.is_favorite = not guide.is_favorite
        guide.save()
        
        return JsonResponse({
            'success': True,
            'is_favorite': guide.is_favorite
        })
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"切换收藏状态失败: {str(e)}")
        return JsonResponse({'error': f'操作失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_travel_guide_api(request, guide_id):
    """删除旅游攻略"""
    try:
        guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        guide.delete()
        
        return JsonResponse({'success': True})
        
    except TravelGuide.DoesNotExist:
        return JsonResponse({'error': '攻略不存在'}, status=404)
    except Exception as e:
        print(f"删除旅游攻略失败: {str(e)}")
        return JsonResponse({'error': f'删除失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def export_travel_guide_api(request, guide_id):
    """导出旅游攻略为PDF"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # 检查guide_id是否有效
        if not guide_id or str(guide_id) == 'undefined':
            return JsonResponse({
                'success': False,
                'error': '无效的攻略ID'
            }, status=400)
        
        # 尝试获取攻略
        try:
            guide = TravelGuide.objects.get(id=guide_id, user=request.user)
        except TravelGuide.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '攻略不存在或您没有权限访问'
            }, status=404)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': '攻略ID格式错误'
            }, status=400)
        
        # 格式化攻略内容
        formatted_content = format_travel_guide_for_export(guide)
        
        # 检查内容是否为空
        if not formatted_content or len(formatted_content.strip()) < 50:
            return JsonResponse({
                'success': False,
                'error': '攻略内容为空或数据不完整，请重新生成攻略'
            }, status=400)
        
        # 直接返回格式化的文本内容，提供更好的用户体验
        logger.info("✅ 返回格式化的文本内容")
        return JsonResponse({
            'success': True,
            'message': '攻略转换成功！已导出为txt格式',
            'formatted_content': formatted_content,
            'format': 'txt',
            'filename': f"{guide.destination}_旅游攻略_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        })
        
    except Exception as e:
        logger.error(f"导出攻略失败: {e}")
        return JsonResponse({
            'success': False,
            'error': f'导出失败: {str(e)}'
        }, status=500)


def format_travel_guide_for_export(guide):
    """格式化旅游攻略用于导出 - 增强版"""
    content = []
    
    try:
        # 标题
        destination = getattr(guide, 'destination', '未知目的地')
        content.append(f"🗺️ {destination} 旅游攻略")
        content.append("=" * 60)
        content.append("")
        
        # 基本信息
        content.append("📋 基本信息")
        content.append("-" * 30)
        content.append(f"📍 目的地: {destination}")
        content.append(f"🎯 旅行风格: {getattr(guide, 'travel_style', '未指定')}")
        content.append(f"💰 预算范围: {getattr(guide, 'budget_range', '未指定')}")
        content.append(f"⏰ 旅行时长: {getattr(guide, 'travel_duration', '未指定')}")
        
        interests = getattr(guide, 'interests', [])
        if interests and isinstance(interests, list) and len(interests) > 0:
            content.append(f"🎨 兴趣偏好: {', '.join(interests)}")
        else:
            content.append("🎨 兴趣偏好: 无")
        content.append("")
        
        # 最佳旅行时间
        best_time = getattr(guide, 'best_time_to_visit', None)
        if best_time:
            content.append("📅 最佳旅行时间")
            content.append("-" * 30)
            content.append(str(best_time))
            content.append("")
        
        # 天气信息
        weather_info = getattr(guide, 'weather_info', None)
        if weather_info:
            content.append("🌤️ 天气信息")
            content.append("-" * 30)
            try:
                if isinstance(weather_info, dict):
                    for season, info in weather_info.items():
                        content.append(f"• {season}: {info}")
                else:
                    content.append(str(weather_info))
            except:
                content.append(str(weather_info))
            content.append("")
        
        # 必去景点
        attractions = getattr(guide, 'must_visit_attractions', None)
        if attractions:
            content.append("🎯 必去景点")
            content.append("-" * 30)
            try:
                if isinstance(attractions, list):
                    for i, attraction in enumerate(attractions, 1):
                        if isinstance(attraction, dict):
                            name = attraction.get('name', '')
                            description = attraction.get('description', '')
                            ticket_price = attraction.get('ticket_price', '')
                            open_time = attraction.get('open_time', '')
                            
                            content.append(f"{i}. {name}")
                            if description:
                                content.append(f"   描述: {description}")
                            if ticket_price:
                                content.append(f"   门票: {ticket_price}")
                            if open_time:
                                content.append(f"   开放时间: {open_time}")
                            content.append("")
                        else:
                            content.append(f"{i}. {str(attraction)}")
                else:
                    content.append(str(attractions))
            except Exception as e:
                content.append("景点数据解析错误")
            content.append("")
        
        # 美食推荐
        foods = getattr(guide, 'food_recommendations', None)
        if foods:
            content.append("🍜 美食推荐")
            content.append("-" * 30)
            try:
                if isinstance(foods, list):
                    for i, food in enumerate(foods, 1):
                        if isinstance(food, dict):
                            name = food.get('name', '')
                            specialty = food.get('specialty', '')
                            price_range = food.get('price_range', '')
                            recommendation = food.get('recommendation', '')
                            
                            content.append(f"{i}. {name}")
                            if specialty:
                                content.append(f"   特色: {specialty}")
                            if price_range:
                                content.append(f"   价格: {price_range}")
                            if recommendation:
                                content.append(f"   推荐理由: {recommendation}")
                            content.append("")
                        else:
                            content.append(f"{i}. {str(food)}")
                else:
                    content.append(str(foods))
            except Exception as e:
                content.append("美食数据解析错误")
            content.append("")
        
        # 每日行程
        daily_schedule = getattr(guide, 'daily_schedule', None)
        if daily_schedule:
            content.append("🚥 每日行程")
            content.append("-" * 30)
            try:
                if isinstance(daily_schedule, list):
                    for i, day_schedule in enumerate(daily_schedule, 1):
                        content.append(f"第{i}天:")
                        
                        if isinstance(day_schedule, dict):
                            # 早晨
                            morning = day_schedule.get('morning', [])
                            if morning:
                                content.append("   🌅 早晨:")
                                if isinstance(morning, list):
                                    for activity in morning:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(morning)}")
                            
                            # 下午
                            afternoon = day_schedule.get('afternoon', [])
                            if afternoon:
                                content.append("   ☀️ 下午:")
                                if isinstance(afternoon, list):
                                    for activity in afternoon:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(afternoon)}")
                            
                            # 晚上
                            evening = day_schedule.get('evening', [])
                            if evening:
                                content.append("   🌙 晚上:")
                                if isinstance(evening, list):
                                    for activity in evening:
                                        if isinstance(activity, dict):
                                            activity_name = activity.get('activity', '')
                                            location = activity.get('location', '')
                                            time = activity.get('time', '')
                                            cost = activity.get('cost', '')
                                            
                                            content.append(f"     • {activity_name}")
                                            if location:
                                                content.append(f"       地点: {location}")
                                            if time:
                                                content.append(f"       时间: {time}")
                                            if cost:
                                                content.append(f"       费用: {cost}")
                                        else:
                                            content.append(f"     • {str(activity)}")
                                else:
                                    content.append(f"     • {str(evening)}")
                        else:
                            content.append(f"   {str(day_schedule)}")
                        content.append("")
                else:
                    content.append(str(daily_schedule))
            except Exception as e:
                content.append("行程数据解析错误")
            content.append("")
        
        # 交通指南
        transport = getattr(guide, 'transportation_guide', None)
        if transport:
            content.append("🚗 交通指南")
            content.append("-" * 30)
            try:
                if isinstance(transport, dict):
                    for key, value in transport.items():
                        content.append(f"• {key}: {value}")
                else:
                    content.append(str(transport))
            except Exception as e:
                content.append("交通数据解析错误")
            content.append("")
        
        # 预算估算
        budget = getattr(guide, 'budget_estimate', None)
        if budget:
            content.append("💰 预算估算")
            content.append("-" * 30)
            try:
                if isinstance(budget, dict):
                    for budget_type, amount in budget.items():
                        content.append(f"• {budget_type}: {amount}")
                else:
                    content.append(str(budget))
            except Exception as e:
                content.append("预算数据解析错误")
            content.append("")
        
        # 费用明细
        cost_breakdown = getattr(guide, 'cost_breakdown', None)
        if cost_breakdown:
            content.append("💸 费用明细")
            content.append("-" * 30)
            try:
                if isinstance(cost_breakdown, dict):
                    total_cost = cost_breakdown.get('total_cost', 0)
                    content.append(f"总费用: ¥{total_cost}")
                    content.append("")
                    
                    for category, details in cost_breakdown.items():
                        if category != 'total_cost':
                            if isinstance(details, dict):
                                description = details.get('description', category)
                                cost = details.get('total_cost', 0)
                                daily_cost = details.get('daily_cost', 0)
                                
                                content.append(f"• {description}: ¥{cost}")
                                if daily_cost:
                                    content.append(f"  日均: ¥{daily_cost}")
                            else:
                                content.append(f"• {category}: {details}")
                else:
                    content.append(str(cost_breakdown))
            except Exception as e:
                content.append("费用数据解析错误")
            content.append("")
        
        # 隐藏玩法
        hidden_gems = getattr(guide, 'hidden_gems', None)
        if hidden_gems:
            content.append("💎 隐藏玩法")
            content.append("-" * 30)
            try:
                if isinstance(hidden_gems, list):
                    for i, gem in enumerate(hidden_gems, 1):
                        content.append(f"{i}. {str(gem)}")
                else:
                    content.append(str(hidden_gems))
            except Exception as e:
                content.append("隐藏玩法数据解析错误")
            content.append("")
        
        # 旅行贴士
        tips = getattr(guide, 'travel_tips', None)
        if tips:
            content.append("💡 旅行贴士")
            content.append("-" * 30)
            try:
                if isinstance(tips, list):
                    for i, tip in enumerate(tips, 1):
                        content.append(f"{i}. {str(tip)}")
                else:
                    content.append(str(tips))
            except Exception as e:
                content.append("贴士数据解析错误")
            content.append("")
        
        # 详细攻略
        detailed_guide = getattr(guide, 'detailed_guide', None)
        if detailed_guide:
            content.append("📖 详细攻略")
            content.append("-" * 30)
            content.append(str(detailed_guide))
            content.append("")
        
        # 生成时间
        content.append("=" * 60)
        content.append(f"📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        content.append("🎯 由 WanderAI 智能旅游攻略系统生成")
        
    except Exception as e:
        # 如果出现任何错误，返回基本信息
        content = [
            f"🗺️ {getattr(guide, 'destination', '未知目的地')} 旅游攻略",
            "=" * 60,
            "",
            "📋 基本信息",
            "-" * 30,
            f"📍 目的地: {getattr(guide, 'destination', '未知目的地')}",
            f"🎯 旅行风格: {getattr(guide, 'travel_style', '未指定')}",
            f"💰 预算范围: {getattr(guide, 'budget_range', '未指定')}",
            f"⏰ 旅行时长: {getattr(guide, 'travel_duration', '未指定')}",
            "",
            "⚠️ 数据解析出现错误，请重新生成攻略。",
            "",
            "=" * 60,
            f"📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
            "🎯 由 WanderAI 智能旅游攻略系统生成"
        ]
    
    return "\n".join(content)


def validate_budget_range(budget_min, budget_max):
    """验证预算范围"""
    try:
        budget_min = int(budget_min)
        budget_max = int(budget_max)
        
        if budget_min < 0 or budget_max < 0:
            return "预算不能为负数"
        
        if budget_min > budget_max:
            return "预算最小值不能大于最大值"
        
        if budget_max > 100000:
            return "预算最大值不能超过10万元"
        
        return None
    except (ValueError, TypeError):
        return "预算格式错误"
