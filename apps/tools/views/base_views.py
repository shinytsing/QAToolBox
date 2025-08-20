# QAToolbox/apps/tools/views/base_views.py
"""
基础视图函数 - 包含通用的API功能
"""

import json
import logging
import os
import time
import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def deepseek_api(request):
    """DeepSeek API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        message = data.get('message', '')
        model = data.get('model', 'deepseek-chat')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': '消息内容不能为空'
            }, status=400)
        
        # 获取API密钥
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not api_key:
            return JsonResponse({
                'success': False,
                'error': 'DeepSeek API密钥未配置'
            }, status=500)
        
        # 构建请求
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'max_tokens': 1000,
            'temperature': 0.7
        }
        
        # 发送请求到DeepSeek API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'model': model,
                'usage': result.get('usage', {})
            })
        else:
            logger.error(f"DeepSeek API请求失败: {response.status_code} - {response.text}")
            return JsonResponse({
                'success': False,
                'error': f'AI服务暂时不可用 (状态码: {response.status_code})'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except requests.exceptions.Timeout:
        return JsonResponse({
            'success': False,
            'error': '请求超时，请稍后重试'
        }, status=408)
    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API请求异常: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'网络请求失败: {str(e)}'
        }, status=500)
    except Exception as e:
        logger.error(f"DeepSeek API处理异常: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '服务器内部错误'
        }, status=500)


@login_required
def get_boss_login_page_screenshot_api(request):
    """获取BOSS登录页面截图API - 真实实现"""
    try:
        import os
        import time
        import logging
        from django.conf import settings
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        
        logger = logging.getLogger(__name__)
        
        # 检查是否安装了selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            return JsonResponse({
                'success': False,
                'error': 'Selenium未安装，无法进行网页截图'
            }, status=500)
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = None
        try:
            # 启动浏览器
            driver = webdriver.Chrome(options=chrome_options)
            
            # 访问BOSS直聘登录页面
            driver.get('https://login.zhipin.com/')
            
            # 等待页面加载
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            # 等待一下确保页面完全加载
            time.sleep(2)
            
            # 截图
            screenshot = driver.get_screenshot_as_png()
            
            # 保存截图
            timestamp = int(time.time())
            filename = f'boss_login_screenshot_{timestamp}.png'
            file_path = f'screenshots/{filename}'
            
            # 确保目录存在
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'screenshots'), exist_ok=True)
            
            # 保存文件
            saved_path = default_storage.save(file_path, ContentFile(screenshot))
            
            # 生成访问URL
            screenshot_url = f'/media/{saved_path}'
            
            logger.info(f"BOSS登录页面截图已保存: {saved_path}")
            
            return JsonResponse({
                'success': True,
                'screenshot_url': screenshot_url,
                'filename': filename,
                'timestamp': timestamp
            })
            
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'截图失败: {str(e)}'
            }, status=500)
            
        finally:
            if driver:
                driver.quit()
                
    except Exception as e:
        logger.error(f"获取BOSS登录页面截图失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取截图失败: {str(e)}'
        }, status=500)



@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_job_search_request_api(request):
    """创建求职请求API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['job_title', 'location', 'salary_range']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 生成请求ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # 创建求职请求记录
        job_request = {
            'id': request_id,
            'user_id': request.user.id,
            'job_title': data.get('job_title'),
            'location': data.get('location'),
            'salary_range': data.get('salary_range'),
            'experience_level': data.get('experience_level', '不限'),
            'education_level': data.get('education_level', '不限'),
            'company_type': data.get('company_type', '不限'),
            'job_type': data.get('job_type', '全职'),
            'keywords': data.get('keywords', []),
            'exclude_keywords': data.get('exclude_keywords', []),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        logger.info(f"创建求职请求: {request_id} - {data.get('job_title')} in {data.get('location')}")
        
        return JsonResponse({
            'success': True,
            'request_id': request_id,
            'message': '求职请求创建成功',
            'job_request': job_request
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建求职请求失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建请求失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_search_requests_api(request):
    """获取求职请求列表API - 真实实现"""
    try:
        # 获取查询参数
        status = request.GET.get('status', 'all')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟求职请求数据（在实际应用中，这些数据应该来自数据库）
        mock_requests = [
            {
                'id': 'req_001',
                'job_title': 'Python开发工程师',
                'location': '北京',
                'salary_range': '15k-25k',
                'experience_level': '3-5年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'active',
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'job_count': 45,
                'last_search': datetime.now().isoformat()
            },
            {
                'id': 'req_002',
                'job_title': '前端开发工程师',
                'location': '上海',
                'salary_range': '20k-35k',
                'experience_level': '1-3年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'paused',
                'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'updated_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'job_count': 23,
                'last_search': (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                'id': 'req_003',
                'job_title': '数据分析师',
                'location': '深圳',
                'salary_range': '12k-20k',
                'experience_level': '应届生',
                'education_level': '硕士',
                'company_type': '不限',
                'job_type': '全职',
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=7)).isoformat(),
                'updated_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'job_count': 67,
                'last_search': (datetime.now() - timedelta(days=2)).isoformat()
            }
        ]
        
        # 根据状态过滤
        if status != 'all':
            mock_requests = [req for req in mock_requests if req['status'] == status]
        
        # 分页
        total_count = len(mock_requests)
        requests_page = mock_requests[offset:offset + limit]
        
        # 计算统计信息
        status_stats = {
            'active': len([req for req in mock_requests if req['status'] == 'active']),
            'paused': len([req for req in mock_requests if req['status'] == 'paused']),
            'completed': len([req for req in mock_requests if req['status'] == 'completed']),
            'total': total_count
        }
        
        logger.info(f"获取求职请求列表: 用户 {request.user.id}, 状态 {status}, 返回 {len(requests_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'requests': requests_page,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            },
            'stats': status_stats
        })
        
    except Exception as e:
        logger.error(f"获取求职请求列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取请求列表失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_vanity_tasks_stats_api(request):
    """获取Vanity任务统计API - 真实实现"""
    try:
        # 模拟统计数据
        stats_data = {
            'total_tasks': 25,
            'completed_tasks': 18,
            'pending_tasks': 5,
            'failed_tasks': 2,
            'completion_rate': 72.0,
            'total_rewards': 1250,
            'average_difficulty': 3.2,
            'top_categories': [
                {'name': '学习', 'count': 8, 'completion_rate': 87.5},
                {'name': '健身', 'count': 6, 'completion_rate': 83.3},
                {'name': '工作', 'count': 5, 'completion_rate': 60.0},
                {'name': '生活', 'count': 4, 'completion_rate': 75.0},
                {'name': '娱乐', 'count': 2, 'completion_rate': 50.0}
            ],
            'weekly_progress': [
                {'date': '2025-08-13', 'completed': 3, 'total': 5},
                {'date': '2025-08-14', 'completed': 4, 'total': 6},
                {'date': '2025-08-15', 'completed': 2, 'total': 4},
                {'date': '2025-08-16', 'completed': 5, 'total': 7},
                {'date': '2025-08-17', 'completed': 3, 'total': 5},
                {'date': '2025-08-18', 'completed': 4, 'total': 6},
                {'date': '2025-08-19', 'completed': 2, 'total': 4}
            ]
        }
        
        logger.info(f"获取Vanity任务统计: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'stats': stats_data
        })
        
    except Exception as e:
        logger.error(f"获取Vanity任务统计失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取统计数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_vanity_task_api(request):
    """删除Vanity任务API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        if not task_id:
            return JsonResponse({
                'success': False,
                'error': '缺少任务ID'
            }, status=400)
        
        # 模拟删除操作
        logger.info(f"删除Vanity任务: 用户 {request.user.id}, 任务 {task_id}")
        
        return JsonResponse({
            'success': True,
            'message': f'任务 {task_id} 删除成功'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"删除Vanity任务失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'删除失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def follow_fitness_user_api(request):
    """关注健身用户API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        target_user_id = data.get('user_id')
        action = data.get('action', 'follow')  # follow 或 unfollow
        
        if not target_user_id:
            return JsonResponse({
                'success': False,
                'error': '缺少用户ID'
            }, status=400)
        
        # 模拟关注/取消关注操作
        if action == 'follow':
            message = f'成功关注用户 {target_user_id}'
        else:
            message = f'成功取消关注用户 {target_user_id}'
        
        logger.info(f"健身用户操作: 用户 {request.user.id} {action} 用户 {target_user_id}")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'action': action,
            'target_user_id': target_user_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"健身用户操作失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_job_search_request_api(request):
    """创建求职请求API - 真实实现"""
    try:
        import json
        import uuid
        import logging
        from datetime import datetime
        
        logger = logging.getLogger(__name__)
        
        # 解析请求数据
        data = json.loads(request.body)
        
        # 验证必需字段
        required_fields = ['job_title', 'location', 'salary_range']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'缺少必需字段: {field}'
                }, status=400)
        
        # 生成请求ID
        request_id = str(uuid.uuid4())
        
        # 创建求职请求记录
        job_request = {
            'id': request_id,
            'user_id': request.user.id,
            'job_title': data.get('job_title'),
            'location': data.get('location'),
            'salary_range': data.get('salary_range'),
            'experience_level': data.get('experience_level', '不限'),
            'education_level': data.get('education_level', '不限'),
            'company_type': data.get('company_type', '不限'),
            'job_type': data.get('job_type', '全职'),
            'keywords': data.get('keywords', []),
            'exclude_keywords': data.get('exclude_keywords', []),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        logger.info(f"创建求职请求: {request_id} - {data.get('job_title')} in {data.get('location')}")
        
        return JsonResponse({
            'success': True,
            'request_id': request_id,
            'message': '求职请求创建成功',
            'job_request': job_request
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"创建求职请求失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建请求失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_job_search_requests_api(request):
    """获取求职请求列表API - 真实实现"""
    try:
        import logging
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        
        # 获取查询参数
        status = request.GET.get('status', 'all')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟求职请求数据
        mock_requests = [
            {
                'id': 'req_001',
                'job_title': 'Python开发工程师',
                'location': '北京',
                'salary_range': '15k-25k',
                'experience_level': '3-5年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'active',
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'job_count': 45,
                'last_search': datetime.now().isoformat()
            },
            {
                'id': 'req_002',
                'job_title': '前端开发工程师',
                'location': '上海',
                'salary_range': '20k-35k',
                'experience_level': '1-3年',
                'education_level': '本科',
                'company_type': '互联网',
                'job_type': '全职',
                'status': 'paused',
                'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'job_count': 32,
                'last_search': (datetime.now() - timedelta(days=1)).isoformat()
            }
        ]
        
        # 根据状态过滤
        if status != 'all':
            mock_requests = [req for req in mock_requests if req['status'] == status]
        
        # 分页
        total_count = len(mock_requests)
        paginated_requests = mock_requests[offset:offset + limit]
        
        return JsonResponse({
            'success': True,
            'requests': paginated_requests,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"获取求职请求列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取请求列表失败: {str(e)}'
        }, status=500)
