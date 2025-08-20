"""
基础工具视图
包含测试用例生成器、小红书生成器、PDF转换器等基础工具
"""

import json
import os
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from ..services.ip_location_service import IPLocationService
import logging

logger = logging.getLogger(__name__)


@login_required
def test_case_generator(request):
    """测试用例生成器页面"""
    return render(request, 'tools/test_case_generator.html')


@login_required
def redbook_generator(request):
    """小红书文案生成器页面"""
    return render(request, 'tools/redbook_generator.html')


@login_required
def pdf_converter(request):
    """PDF转换器页面"""
    return render(request, 'tools/pdf_converter_modern.html')


def pdf_converter_test(request):
    """PDF转换器测试页面（无需登录）"""
    return render(request, 'tools/pdf_converter_test.html')


@login_required
def fortune_analyzer(request):
    """姻缘分析器页面"""
    return render(request, 'tools/fortune_analyzer.html')


@login_required
def web_crawler(request):
    """社交媒体订阅页面"""
    return render(request, 'tools/web_crawler.html')


def social_subscription_demo(request):
    """社交媒体订阅功能演示页面"""
    return render(request, 'tools/social_subscription_demo.html')


@login_required
def self_analysis(request):
    """人生百态镜页面"""
    return render(request, 'tools/self_analysis.html')


@login_required
def storyboard(request):
    """故事板页面"""
    return render(request, 'tools/storyboard.html')


@login_required
def fitness_center(request):
    """FitMatrix健身矩阵页面"""
    return render(request, 'tools/fitness_center.html')


@login_required
def training_plan_editor(request):
    """训练计划编辑器页面"""
    return render(request, 'tools/training_plan_editor.html')


@csrf_exempt
@require_http_methods(["POST"])
def deepseek_api(request):
    """DeepSeek API接口"""
    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.8)
        
        if not prompt:
            return JsonResponse({'success': False, 'error': '提示词不能为空'}, content_type='application/json')
        
        # DeepSeek API配置
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return JsonResponse({'success': False, 'error': 'DeepSeek API密钥未配置'}, content_type='application/json')
        
        # 调用DeepSeek API
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'model': 'deepseek-chat',
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return JsonResponse({
                'success': True,
                'content': content,
                'usage': result.get('usage', {})
            }, content_type='application/json')
        else:
            return JsonResponse({
                'success': False,
                'error': f'API调用失败: {response.status_code}'
            }, content_type='application/json')
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': '请求超时，请稍后重试'
        }, content_type='application/json')
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'success': False,
            'error': f'网络请求失败: {str(e)}'
        }, content_type='application/json')
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }, content_type='application/json')


@login_required
def self_analysis_api(request):
    """人生百态镜API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            context = data.get('context', '')
            
            if not question:
                return JsonResponse({
                    'success': False,
                    'error': '问题不能为空'
                })
            
            # 构建分析提示词
            prompt = f"""
            作为一个专业的心理咨询师和人生导师，请基于以下信息进行分析：

            用户问题：{question}
            
            背景信息：{context}
            
            请从以下角度进行分析：
            1. 心理层面：情绪状态、思维模式、行为动机
            2. 社会层面：人际关系、环境因素、社会支持
            3. 发展层面：个人成长、目标设定、潜力挖掘
            4. 建议层面：具体行动建议、改善方向、资源推荐
            
            请用温暖、专业、实用的语言回答，帮助用户更好地认识自己和改善现状。
            """
            
            # 调用DeepSeek API进行分析
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return JsonResponse({
                    'success': False,
                    'error': '分析服务暂时不可用'
                })
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'model': 'deepseek-chat',
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                return JsonResponse({
                    'success': True,
                    'analysis': analysis,
                    'timestamp': timezone.now().isoformat()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '分析服务暂时不可用，请稍后重试'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'分析失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': '只支持POST请求'})


@login_required
def storyboard_api(request):
    """故事板API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            story_type = data.get('story_type', '')
            theme = data.get('theme', '')
            characters = data.get('characters', [])
            plot_points = data.get('plot_points', [])
            
            if not story_type or not theme:
                return JsonResponse({
                    'success': False,
                    'error': '故事类型和主题不能为空'
                })
            
            # 构建故事生成提示词
            characters_text = '\n'.join([f"- {char}" for char in characters]) if characters else "默认角色"
            plot_text = '\n'.join([f"- {point}" for point in plot_points]) if plot_points else "自由发展"
            
            prompt = f"""
            作为一个专业的编剧和故事创作者，请基于以下信息创作一个精彩的故事：

            故事类型：{story_type}
            主题：{theme}
            
            角色设定：
            {characters_text}
            
            情节要点：
            {plot_text}
            
            请创作一个包含以下要素的完整故事：
            1. 引人入胜的开头
            2. 清晰的角色发展
            3. 扣人心弦的情节发展
            4. 令人满意的结局
            5. 深刻的主题表达
            
            请用生动、富有感染力的语言讲述这个故事，让读者能够身临其境。
            """
            
            # 调用DeepSeek API生成故事
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return JsonResponse({
                    'success': False,
                    'error': '故事生成服务暂时不可用'
                })
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'model': 'deepseek-chat',
                'max_tokens': 1500,
                'temperature': 0.8
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                story = result['choices'][0]['message']['content']
                
                return JsonResponse({
                    'success': True,
                    'story': story,
                    'story_info': {
                        'type': story_type,
                        'theme': theme,
                        'characters': characters,
                        'plot_points': plot_points,
                        'word_count': len(story.split()),
                        'created_at': timezone.now().isoformat()
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '故事生成服务暂时不可用，请稍后重试'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'故事生成失败: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': '只支持POST请求'})


@csrf_exempt
@require_http_methods(["GET"])
def location_api(request):
    """位置信息API"""
    try:
        ip_service = IPLocationService()
        
        # 获取用户位置信息
        location = ip_service.get_user_location(request)
        
        return JsonResponse({
            'success': True,
            'location': location
        })
    except Exception as e:
        logger.error(f"位置API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '获取位置信息失败',
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_location_api(request):
    """更新用户位置信息API"""
    try:
        data = json.loads(request.body)
        city_name = data.get('city', '').strip()
        
        if not city_name:
            return JsonResponse({
                'success': False,
                'message': '城市名称不能为空'
            }, status=400)
        
        ip_service = IPLocationService()
        location = ip_service.get_location_by_city_name(city_name)
        
        return JsonResponse({
            'success': True,
            'location': location
        })
    except Exception as e:
        logger.error(f"更新位置API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '更新位置信息失败',
            'error': str(e)
        }, status=500)
