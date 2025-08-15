from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import time
import random
import subprocess
import socket
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# 代理服务器配置（基于提供的Clash配置）
PROXY_SERVERS = [
    {
        'name': 'HongKong-IPLC-HK-1',
        'type': 'trojan',
        'server': 'iplc-hk-1.trojanwheel.com',
        'port': 465,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Hong Kong',
        'category': 'IPLC'
    },
    {
        'name': 'HongKong-IPLC-HK-2',
        'type': 'trojan',
        'server': 'iplc-hk-2.trojanwheel.com',
        'port': 465,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Hong Kong',
        'category': 'IPLC'
    },
    {
        'name': 'Japan-TY-1',
        'type': 'trojan',
        'server': 'ty-1.rise-fuji.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Japan',
        'category': 'Premium'
    },
    {
        'name': 'UnitedStates-US-1',
        'type': 'trojan',
        'server': 'us-1.regentgrandvalley.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'United States',
        'category': 'Premium'
    },
    {
        'name': 'Singapore-SG-1',
        'type': 'trojan',
        'server': 'sg-1.victoriamitrepeak.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Singapore',
        'category': 'Premium'
    },
    {
        'name': 'Australia-AU-1',
        'type': 'trojan',
        'server': 'au-1.australiastudio.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Australia',
        'category': 'Premium'
    }
]

class ProxyManager:
    """代理管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.test_urls = [
            'https://www.google.com',
            'https://www.youtube.com',
            'https://www.facebook.com',
            'https://twitter.com',
            'https://github.com'
        ]
    
    def test_trojan_connection(self, proxy_config: Dict) -> Dict:
        """测试Trojan代理连接"""
        try:
            # 测试TCP连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            start_time = time.time()
            result = sock.connect_ex((proxy_config['server'], proxy_config['port']))
            response_time = time.time() - start_time
            sock.close()
            
            if result == 0:
                return {
                    'success': True,
                    'proxy': proxy_config['name'],
                    'response_time': round(response_time, 2),
                    'ip': proxy_config['server'],
                    'status': 'connected',
                    'message': 'TCP连接成功'
                }
            else:
                return {
                    'success': False,
                    'proxy': proxy_config['name'],
                    'error': f'TCP连接失败 (错误码: {result})',
                    'status': 'failed'
                }
                
        except socket.timeout:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': '连接超时',
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'连接错误: {str(e)}',
                'status': 'error'
            }
    
    def test_proxy(self, proxy_config: Dict) -> Dict:
        """测试单个代理"""
        # 对于Trojan协议，只测试TCP连接
        if proxy_config['type'] == 'trojan':
            return self.test_trojan_connection(proxy_config)
        
        # 对于HTTP/HTTPS代理，使用原有逻辑
        try:
            # 构建代理URL
            proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
            
            # 设置代理
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # 测试连接
            start_time = time.time()
            response = self.session.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'proxy': proxy_config['name'],
                    'response_time': round(response_time, 2),
                    'ip': response.json().get('origin', ''),
                    'status': 'working'
                }
            else:
                return {
                    'success': False,
                    'proxy': proxy_config['name'],
                    'error': f'HTTP {response.status_code}',
                    'status': 'failed'
                }
                
        except requests.exceptions.ProxyError as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'代理连接失败: {str(e)}',
                'status': 'failed'
            }
        except requests.exceptions.Timeout as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'连接超时: {str(e)}',
                'status': 'timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'未知错误: {str(e)}',
                'status': 'error'
            }
    
    def test_all_proxies(self) -> List[Dict]:
        """测试所有代理"""
        results = []
        for proxy in PROXY_SERVERS:
            result = self.test_proxy(proxy)
            results.append(result)
            time.sleep(0.5)  # 避免请求过快
        return results
    
    def get_working_proxies(self) -> List[Dict]:
        """获取可用的代理列表"""
        results = self.test_all_proxies()
        working_proxies = [r for r in results if r['success']]
        return working_proxies
    
    def test_website_accessibility(self, url: str, proxy_config: Dict = None) -> Dict:
        """测试网站可访问性"""
        try:
            if proxy_config:
                proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
                proxies = {'http': proxy_url, 'https': proxy_url}
            else:
                proxies = None
            
            start_time = time.time()
            response = self.session.get(url, proxies=proxies, timeout=10)
            response_time = time.time() - start_time
            
            return {
                'accessible': True,
                'url': url,
                'status_code': response.status_code,
                'response_time': round(response_time, 2),
                'proxy_used': proxy_config['name'] if proxy_config else 'Direct'
            }
            
        except Exception as e:
            return {
                'accessible': False,
                'url': url,
                'error': str(e),
                'proxy_used': proxy_config['name'] if proxy_config else 'Direct'
            }
    
    def get_current_ip(self, proxy_config: Dict = None) -> Dict:
        """获取当前IP地址"""
        try:
            if proxy_config:
                # 对于Trojan协议，需要特殊处理
                if proxy_config['type'] == 'trojan':
                    return {
                        'success': False,
                        'error': 'Trojan协议需要通过专用客户端使用',
                        'ip': 'N/A',
                        'proxy_used': proxy_config['name']
                    }
                else:
                    proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
                    proxies = {'http': proxy_url, 'https': proxy_url}
            else:
                proxies = None
            
            # 尝试多个IP查询服务
            ip_services = [
                'https://httpbin.org/ip',
                'https://api.ipify.org?format=json',
                'https://icanhazip.com',
                'https://jsonip.com'
            ]
            
            ip_data = None
            for service in ip_services:
                try:
                    response = self.session.get(service, proxies=proxies, timeout=5)
                    if response.status_code == 200:
                        if service == 'https://icanhazip.com':
                            ip_data = {'origin': response.text.strip()}
                        else:
                            ip_data = response.json()
                        break
                except:
                    continue
            
            if not ip_data:
                return {
                    'success': False,
                    'error': '无法获取IP地址',
                    'proxy_used': proxy_config['name'] if proxy_config else 'Direct'
                }
            
            # 获取地理位置信息（可选）
            try:
                geo_response = self.session.get(f"http://ip-api.com/json/{ip_data.get('origin', ip_data.get('ip', ''))}", timeout=5)
                geo_data = geo_response.json()
            except:
                geo_data = {}
            
            return {
                'success': True,
                'ip': ip_data.get('origin', ip_data.get('ip', '')),
                'country': geo_data.get('country', ''),
                'region': geo_data.get('regionName', ''),
                'city': geo_data.get('city', ''),
                'isp': geo_data.get('isp', ''),
                'proxy_used': proxy_config['name'] if proxy_config else 'Direct'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'proxy_used': proxy_config['name'] if proxy_config else 'Direct'
            }

    def test_real_proxy_request(self, proxy_config: Dict, target_url: str = 'https://www.google.com') -> Dict:
        """测试真实代理请求"""
        try:
            # 对于Trojan协议，返回说明信息
            if proxy_config['type'] == 'trojan':
                return {
                    'success': False,
                    'proxy': proxy_config['name'],
                    'error': 'Trojan协议需要通过专用客户端（如Clash、V2Ray）使用',
                    'status': 'protocol_not_supported',
                    'solution': '请使用Clash、V2Ray等客户端配置代理'
                }
            
            # 构建代理URL
            proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # 测试连接
            start_time = time.time()
            response = self.session.get(
                target_url,
                proxies=proxies,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'proxy': proxy_config['name'],
                    'response_time': round(response_time, 2),
                    'status_code': response.status_code,
                    'status': 'working',
                    'target_url': target_url
                }
            else:
                return {
                    'success': False,
                    'proxy': proxy_config['name'],
                    'error': f'HTTP {response.status_code}',
                    'status': 'failed',
                    'target_url': target_url
                }
                
        except requests.exceptions.ProxyError as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'代理连接失败: {str(e)}',
                'status': 'failed',
                'target_url': target_url
            }
        except requests.exceptions.Timeout as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'连接超时: {str(e)}',
                'status': 'timeout',
                'target_url': target_url
            }
        except Exception as e:
            return {
                'success': False,
                'proxy': proxy_config['name'],
                'error': f'未知错误: {str(e)}',
                'status': 'error',
                'target_url': target_url
            }

    def get_ip_comparison(self) -> Dict:
        """获取直连和代理的IP对比"""
        try:
            # 获取直连IP
            direct_ip_result = self.get_current_ip()
            
            # 获取代理IP（使用第一个可用的代理）
            proxy_ip_result = None
            for proxy in PROXY_SERVERS:
                if proxy['type'] != 'trojan':  # 跳过Trojan协议
                    proxy_ip_result = self.get_current_ip(proxy)
                    if proxy_ip_result.get('success'):
                        break
            
            # 如果没有找到可用的代理，设置默认值
            if not proxy_ip_result:
                proxy_ip_result = {
                    'success': False,
                    'error': '无可用代理',
                    'proxy_used': 'None'
                }
            
            return {
                'success': True,
                'direct_ip': direct_ip_result,
                'proxy_ip': proxy_ip_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'获取IP对比失败: {str(e)}'
            }

# 全局代理管理器实例
proxy_manager = ProxyManager()

@login_required
def proxy_dashboard(request):
    """代理翻墙功能主页面"""
    return render(request, 'tools/proxy_dashboard.html')

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def proxy_status_api(request):
    """获取代理状态API"""
    try:
        # 获取当前IP（直连）
        current_ip = proxy_manager.get_current_ip()
        
        # 测试所有代理
        proxy_results = proxy_manager.test_all_proxies()
        
        # 统计信息
        total_proxies = len(proxy_results)
        working_proxies = len([p for p in proxy_results if p['success']])
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_ip': current_ip,
                'proxy_results': proxy_results,
                'statistics': {
                    'total_proxies': total_proxies,
                    'working_proxies': working_proxies,
                    'success_rate': round(working_proxies / total_proxies * 100, 2) if total_proxies > 0 else 0
                },
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"代理状态API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取代理状态失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def test_website_api(request):
    """测试网站可访问性API"""
    try:
        data = json.loads(request.body)
        url = data.get('url', '')
        proxy_name = data.get('proxy', '')
        
        if not url:
            return JsonResponse({
                'success': False,
                'error': '请提供要测试的URL'
            })
        
        # 查找指定的代理
        proxy_config = None
        if proxy_name:
            for proxy in PROXY_SERVERS:
                if proxy['name'] == proxy_name:
                    proxy_config = proxy
                    break
        
        # 测试网站访问性
        result = proxy_manager.test_website_accessibility(url, proxy_config)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"测试网站API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'测试网站失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def proxy_list_api(request):
    """获取代理列表API"""
    try:
        # 按国家分组代理
        proxies_by_country = {}
        for proxy in PROXY_SERVERS:
            country = proxy['country']
            if country not in proxies_by_country:
                proxies_by_country[country] = []
            proxies_by_country[country].append({
                'name': proxy['name'],
                'type': proxy['type'],
                'server': proxy['server'],
                'port': proxy['port'],
                'category': proxy['category']
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'proxies_by_country': proxies_by_country,
                'total_proxies': len(PROXY_SERVERS)
            }
        })
        
    except Exception as e:
        logger.error(f"代理列表API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取代理列表失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def test_proxy_api(request):
    """测试指定代理API"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get('proxy', '')
        
        if not proxy_name:
            return JsonResponse({
                'success': False,
                'error': '请提供要测试的代理名称'
            })
        
        # 查找指定的代理
        proxy_config = None
        for proxy in PROXY_SERVERS:
            if proxy['name'] == proxy_name:
                proxy_config = proxy
                break
        
        if not proxy_config:
            return JsonResponse({
                'success': False,
                'error': '未找到指定的代理'
            })
        
        # 测试代理
        result = proxy_manager.test_proxy(proxy_config)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"测试代理API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'测试代理失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_ip_info_api(request):
    """获取IP信息API"""
    try:
        proxy_name = request.GET.get('proxy', '')
        
        # 查找指定的代理
        proxy_config = None
        if proxy_name:
            for proxy in PROXY_SERVERS:
                if proxy['name'] == proxy_name:
                    proxy_config = proxy
                    break
        
        # 获取IP信息
        ip_info = proxy_manager.get_current_ip(proxy_config)
        
        return JsonResponse({
            'success': True,
            'data': ip_info
        })
        
    except Exception as e:
        logger.error(f"获取IP信息API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取IP信息失败: {str(e)}'
        })

@login_required
def proxy_guide(request):
    """代理使用指南页面"""
    context = {
        'proxy_servers': PROXY_SERVERS,
        'total_proxies': len(PROXY_SERVERS),
        'trojan_proxies': [p for p in PROXY_SERVERS if p['type'] == 'trojan'],
        'http_proxies': [p for p in PROXY_SERVERS if p['type'] != 'trojan']
    }
    return render(request, 'tools/proxy_guide.html', context)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def proxy_connection_test_api(request):
    """代理连接测试API - 仅测试TCP连接"""
    try:
        results = []
        for proxy in PROXY_SERVERS:
            result = proxy_manager.test_proxy(proxy)
            results.append(result)
            time.sleep(0.5)  # 避免请求过快
        
        # 统计信息
        total_proxies = len(results)
        connected_proxies = len([r for r in results if r['success']])
        
        return JsonResponse({
            'success': True,
            'data': {
                'proxy_results': results,
                'statistics': {
                    'total_proxies': total_proxies,
                    'connected_proxies': connected_proxies,
                    'connection_rate': round(connected_proxies / total_proxies * 100, 2) if total_proxies > 0 else 0
                },
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"代理连接测试API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'代理连接测试失败: {str(e)}'
        })

# 添加新的API视图函数
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_ip_comparison_api(request):
    """获取IP对比API"""
    try:
        ip_comparison = proxy_manager.get_ip_comparison()
        
        return JsonResponse({
            'success': True,
            'data': ip_comparison
        })
        
    except Exception as e:
        logger.error(f"获取IP对比API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取IP对比失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def test_real_proxy_api(request):
    """测试真实代理请求API"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get('proxy', '')
        target_url = data.get('url', 'https://www.google.com')
        
        if not proxy_name:
            return JsonResponse({
                'success': False,
                'error': '请提供要测试的代理名称'
            })
        
        # 查找指定的代理
        proxy_config = None
        for proxy in PROXY_SERVERS:
            if proxy['name'] == proxy_name:
                proxy_config = proxy
                break
        
        if not proxy_config:
            return JsonResponse({
                'success': False,
                'error': '未找到指定的代理'
            })
        
        # 测试真实代理请求
        result = proxy_manager.test_real_proxy_request(proxy_config, target_url)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"测试真实代理API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'测试真实代理失败: {str(e)}'
        })
