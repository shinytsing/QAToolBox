from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import time
import subprocess
import socket
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# 代理服务器配置（商业化翻墙服务）
PROXY_SERVERS = [
    # Trojan高级代理（客户端专用）
    {
        'name': 'HongKong-IPLC-HK-1',
        'type': 'trojan',
        'server': 'iplc-hk-1.trojanwheel.com',
        'port': 465,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Hong Kong',
        'category': 'Premium'
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
    }
]

# 可用的代理服务（基于您的Clash配置）
PUBLIC_PROXY_SERVERS = [
    # 本地Clash代理（优先使用）
    {
        'name': 'Local-Clash-HTTP',
        'type': 'http',
        'server': '127.0.0.1',
        'port': 7890,
        'country': 'Local',
        'category': 'Clash'
    },
    {
        'name': 'Local-Clash-SOCKS',
        'type': 'socks5',
        'server': '127.0.0.1',
        'port': 7891,
        'country': 'Local',
        'category': 'Clash'
    }
]

class ProxyManager:
    """简化的代理管理器 - 专注IP检测和一键代理访问"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def create_proxy_url(self, proxy_config: Dict, target_url: str) -> str:
        """创建代理访问链接"""
        try:
            # 确保目标URL有正确的协议
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url
            
            # 对于Trojan协议，返回配置信息
            if proxy_config['type'] == 'trojan':
                return f"trojan://{proxy_config['password']}@{proxy_config['server']}:{proxy_config['port']}#{target_url}"
            
            # 对于HTTP代理，返回代理服务器信息
            return f"http://{proxy_config['server']}:{proxy_config['port']}"
            
        except Exception as e:
            logger.error(f"创建代理URL失败: {str(e)}")
            return ""
    
    def generate_clash_config(self, proxy_config: Dict) -> str:
        """生成Clash配置文件"""
        try:
            clash_config = {
                "port": 7890,
                "socks-port": 7891,
                "allow-lan": True,
                "mode": "rule",
                "log-level": "info",
                "external-controller": "127.0.0.1:9090",
                "proxies": [{
                    "name": proxy_config['name'],
                    "type": "trojan",
                    "server": proxy_config['server'],
                    "port": proxy_config['port'],
                    "password": proxy_config['password'],
                    "sni": proxy_config['server'],
                    "skip-cert-verify": True,
                    "udp": True
                }],
                "proxy-groups": [{
                    "name": "PROXY",
                    "type": "select",
                    "proxies": [proxy_config['name'], "DIRECT"]
                }, {
                    "name": "Auto",
                    "type": "url-test",
                    "url": "https://www.youtube.com/favicon.ico",
                    "interval": 300,
                    "proxies": [proxy_config['name']]
                }],
                "rules": [
                    "DOMAIN-KEYWORD,google,PROXY",
                    "DOMAIN-KEYWORD,youtube,PROXY",
                    "DOMAIN-KEYWORD,facebook,PROXY",
                    "DOMAIN-KEYWORD,twitter,PROXY",
                    "DOMAIN-KEYWORD,instagram,PROXY",
                    "DOMAIN-KEYWORD,github,PROXY",
                    "DOMAIN-SUFFIX,googleapis.com,PROXY",
                    "DOMAIN-SUFFIX,gstatic.com,PROXY",
                    "DOMAIN-SUFFIX,ytimg.com,PROXY",
                    "DOMAIN-SUFFIX,googlevideo.com,PROXY",
                    "GEOIP,CN,DIRECT",
                    "MATCH,PROXY"
                ]
            }
            
            try:
                import yaml
                return yaml.dump(clash_config, default_flow_style=False, allow_unicode=True)
            except ImportError:
                logger.warning("PyYAML未安装，使用JSON格式返回配置")
                import json
                return json.dumps(clash_config, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"生成Clash配置失败: {str(e)}")
            return ""
    
    def generate_v2ray_config(self, proxy_config: Dict) -> str:
        """生成V2Ray配置文件"""
        try:
            v2ray_config = {
                "log": {"loglevel": "warning"},
                "inbounds": [{
                    "port": 10808,
                    "protocol": "socks",
                    "settings": {"udp": True}
                }, {
                    "port": 10809,
                    "protocol": "http"
                }],
                "outbounds": [{
                    "protocol": "trojan",
                    "settings": {
                        "servers": [{
                            "address": proxy_config['server'],
                            "port": proxy_config['port'],
                            "password": proxy_config['password']
                        }]
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "tls",
                        "tlsSettings": {
                            "serverName": proxy_config['server'],
                            "allowInsecure": True
                        }
                    }
                }, {
                    "protocol": "freedom",
                    "tag": "direct"
                }],
                "routing": {
                    "rules": [{
                        "type": "field",
                        "domain": ["geosite:cn"],
                        "outboundTag": "direct"
                    }, {
                        "type": "field",
                        "ip": ["geoip:private", "geoip:cn"],
                        "outboundTag": "direct"
                    }]
                }
            }
            
            return json.dumps(v2ray_config, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"生成V2Ray配置失败: {str(e)}")
            return ""
    
    def get_current_ip(self, proxy_config: Dict = None) -> Dict:
        """获取当前IP地址"""
        try:
            if proxy_config:
                # 对于Trojan协议，需要通过客户端使用
                if proxy_config['type'] == 'trojan':
                    return {
                        'success': False,
                        'error': 'Trojan协议需要通过专用客户端使用',
                        'ip': 'N/A',
                        'proxy_used': proxy_config['name']
                    }
                elif proxy_config['type'] == 'http':
                    proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
                    proxies = {'http': proxy_url, 'https': proxy_url}
                elif proxy_config['type'] == 'socks5':
                    proxy_url = f"socks5://{proxy_config['server']}:{proxy_config['port']}"
                    proxies = {'http': proxy_url, 'https': proxy_url}
                else:
                    proxies = None
            else:
                proxies = None
            
            # 尝试多个IP查询服务
            ip_services = [
                'https://httpbin.org/ip',
                'https://api.ipify.org?format=json',
                'https://icanhazip.com'
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
            
            # 获取地理位置信息
            try:
                ip_address = ip_data.get('origin', ip_data.get('ip', ''))
                geo_response = self.session.get(f"http://ip-api.com/json/{ip_address}", timeout=5)
                geo_data = geo_response.json() if geo_response.status_code == 200 else {}
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

    def get_ip_comparison(self) -> Dict:
        """获取本地IP和代理IP的对比"""
        try:
            # 获取本地直连IP
            direct_ip_result = self.get_current_ip()
            
            # 优先尝试本地Clash提供的HTTP/SOCKS代理
            proxy_ip_result = None
            for proxy in PUBLIC_PROXY_SERVERS:
                if proxy['type'] in ('http', 'socks5'):
                    proxy_ip_result = self.get_current_ip(proxy)
                    if proxy_ip_result.get('success'):
                        break
            
            # 如果没有可用的HTTP代理，记录信息
            if not proxy_ip_result or not proxy_ip_result.get('success'):
                proxy_ip_result = {
                    'success': False,
                    'error': '未检测到可用的本地代理，请确保Clash已启动且端口7890/7891可用',
                    'proxy_used': 'Local-Clash',
                    'ip': 'N/A'
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
    
    def get_best_proxy_for_website(self, target_url: str) -> Dict:
        """为特定网站推荐最佳代理"""
        try:
            # 基于域名进行简单匹配，推荐适合的代理
            domain_proxy_map = {
                'google.com': 'HongKong-IPLC-HK-1',
                'youtube.com': 'HongKong-IPLC-HK-1',
                'facebook.com': 'UnitedStates-US-1',
                'twitter.com': 'UnitedStates-US-1',
                'instagram.com': 'UnitedStates-US-1',
                'github.com': 'Singapore-SG-1',
                'stackoverflow.com': 'Singapore-SG-1',
                'reddit.com': 'UnitedStates-US-1',
                'netflix.com': 'Japan-TY-1',
                'amazon.com': 'UnitedStates-US-1'
            }
            
            # 默认使用香港代理
            recommended_proxy_name = 'HongKong-IPLC-HK-1'
            
            # 检查是否有特定的推荐
            for domain, proxy_name in domain_proxy_map.items():
                if domain in target_url.lower():
                    recommended_proxy_name = proxy_name
                    break
            
            # 找到推荐的代理配置
            recommended_proxy = None
            for proxy in PROXY_SERVERS:
                if proxy['name'] == recommended_proxy_name:
                    recommended_proxy = proxy
                    break
            
            if recommended_proxy:
                return {
                    'success': True,
                    'recommended_proxy': recommended_proxy,
                    'proxy_url': self.create_proxy_url(recommended_proxy, target_url),
                    'reason': f'基于域名匹配推荐 {recommended_proxy["country"]} 节点'
                }
            else:
                return {
                    'success': False,
                    'error': '找不到推荐的代理服务器'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'获取代理推荐失败: {str(e)}'
            }

# 全局代理管理器实例
proxy_manager = ProxyManager()

@login_required
def proxy_dashboard(request):
    """代理翻墙系统主页面"""
    return render(request, 'tools/proxy_dashboard.html')

# IP对比API - 核心功能1
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_ip_comparison_api(request):
    """获取本地IP和代理IP对比API"""
    try:
        ip_comparison = proxy_manager.get_ip_comparison()
        
        return JsonResponse({
            'success': True,
            'data': ip_comparison
        })
        
    except Exception as e:
        logger.error(f"IP对比API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取IP对比失败: {str(e)}'
        })

# 一键代理设置API - 核心功能2
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def setup_proxy_api(request):
    """一键设置网页VPN代理API"""
    try:
        data = json.loads(request.body)
        target_url = data.get('url', 'https://www.google.com')
        
        # 获取最佳代理推荐
        result = proxy_manager.get_best_proxy_for_website(target_url)
        
        return JsonResponse({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"一键代理设置API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'一键代理设置失败: {str(e)}'
        })

# 代理列表API - 辅助功能
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

# 创建代理访问链接API - 辅助功能
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_proxy_url_api(request):
    """创建代理访问链接API"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get('proxy', '')
        target_url = data.get('url', '')
        
        if not proxy_name or not target_url:
            return JsonResponse({
                'success': False,
                'error': '请提供代理名称和目标URL'
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
        
        # 创建代理URL
        proxy_url = proxy_manager.create_proxy_url(proxy_config, target_url)
        
        if proxy_url:
            return JsonResponse({
                'success': True,
                'data': {
                    'proxy_url': proxy_url,
                    'proxy_config': proxy_config,
                    'target_url': target_url
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '创建代理URL失败'
            })
        
    except Exception as e:
        logger.error(f"创建代理URL API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'创建代理URL失败: {str(e)}'
        })

# 配置文件下载API
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def download_clash_config_api(request):
    """下载Clash配置文件API"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get('proxy', '')
        
        if not proxy_name:
            return JsonResponse({
                'success': False,
                'error': '请提供代理名称'
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
        
        # 生成Clash配置
        config_content = proxy_manager.generate_clash_config(proxy_config)
        
        if config_content:
            from django.http import HttpResponse
            response = HttpResponse(config_content, content_type='application/x-yaml')
            response['Content-Disposition'] = f'attachment; filename="{proxy_config["name"]}_clash.yaml"'
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': '生成配置文件失败'
            })
        
    except Exception as e:
        logger.error(f"下载Clash配置API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'下载配置失败: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def download_v2ray_config_api(request):
    """下载V2Ray配置文件API"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get('proxy', '')
        
        if not proxy_name:
            return JsonResponse({
                'success': False,
                'error': '请提供代理名称'
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
        
        # 生成V2Ray配置
        config_content = proxy_manager.generate_v2ray_config(proxy_config)
        
        if config_content:
            from django.http import HttpResponse
            response = HttpResponse(config_content, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{proxy_config["name"]}_v2ray.json"'
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': '生成配置文件失败'
            })
        
    except Exception as e:
        logger.error(f"下载V2Ray配置API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'下载配置失败: {str(e)}'
        })

# Web代理服务API - 专业翻墙服务
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def web_proxy_api(request):
    """Web翻墙浏览API - 商业化服务"""
    try:
        data = json.loads(request.body)
        target_url = data.get('url', '')
        
        if not target_url:
            return JsonResponse({
                'success': False,
                'error': '请提供目标URL'
            })
        
        # 确保URL格式正确
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        # 自动选择最佳代理策略
        proxy_config = None
        proxies = None
        
        # 智能代理选择 - 使用本地Clash代理
        proxy_working = False
        if any(domain in target_url.lower() for domain in ['youtube.com', 'google.com', 'facebook.com', 'twitter.com', 'instagram.com', 'github.com']):
            # 对于外网站点，优先使用本地Clash代理
            for proxy in PUBLIC_PROXY_SERVERS:
                try:
                    # 测试代理是否可用 - 使用更简单的测试
                    test_url = 'http://httpbin.org/get'
                    
                    if proxy['type'] == 'http':
                        proxy_url = f"http://{proxy['server']}:{proxy['port']}"
                        test_proxies = {'http': proxy_url, 'https': proxy_url}
                    elif proxy['type'] == 'socks5':
                        proxy_url = f"socks5://{proxy['server']}:{proxy['port']}"
                        test_proxies = {'http': proxy_url, 'https': proxy_url}
                    else:
                        continue
                    
                    test_response = requests.get(
                        test_url, 
                        proxies=test_proxies, 
                        timeout=5, 
                        verify=False,
                        headers={'Accept-Encoding': 'identity'}  # 禁用压缩
                    )
                    if test_response.status_code == 200:
                        proxy_config = proxy
                        if proxy['type'] == 'http':
                            proxy_url = f"http://{proxy['server']}:{proxy['port']}"
                            proxies = {'http': proxy_url, 'https': proxy_url}
                        elif proxy['type'] == 'socks5':
                            proxy_url = f"socks5://{proxy['server']}:{proxy['port']}"
                            proxies = {'http': proxy_url, 'https': proxy_url}
                        
                        logger.info(f"代理连接成功: {proxy['name']} ({proxy['server']}:{proxy['port']})")
                        proxy_working = True
                        break
                except Exception as e:
                    logger.warning(f"代理 {proxy['name']} 连接失败: {e}")
                    continue
            
            # 如果代理不可用，记录警告但继续尝试直接连接
            if not proxy_working:
                logger.warning("所有代理都不可用，将尝试直接连接")
                proxy_config = None
                proxies = None
        else:
            # 对于其他网站，如果代理可用也使用代理
            if proxy_working:
                logger.info("使用已验证的代理访问其他网站")
            else:
                # 对于其他网站，也尝试使用本地Clash代理
                for proxy in PUBLIC_PROXY_SERVERS:
                    try:
                        test_url = 'http://httpbin.org/get'
                        
                        if proxy['type'] == 'http':
                            proxy_url = f"http://{proxy['server']}:{proxy['port']}"
                            test_proxies = {'http': proxy_url, 'https': proxy_url}
                        elif proxy['type'] == 'socks5':
                            proxy_url = f"socks5://{proxy['server']}:{proxy['port']}"
                            test_proxies = {'http': proxy_url, 'https': proxy_url}
                        else:
                            continue
                        
                        test_response = requests.get(
                            test_url, 
                            proxies=test_proxies, 
                            timeout=5, 
                            verify=False,
                            headers={'Accept-Encoding': 'identity'}
                        )
                        if test_response.status_code == 200:
                            proxy_config = proxy
                            if proxy['type'] == 'http':
                                proxy_url = f"http://{proxy['server']}:{proxy['port']}"
                                proxies = {'http': proxy_url, 'https': proxy_url}
                            elif proxy['type'] == 'socks5':
                                proxy_url = f"socks5://{proxy['server']}:{proxy['port']}"
                                proxies = {'http': proxy_url, 'https': proxy_url}
                            proxy_working = True
                            break
                    except:
                        continue
        
        # 增强的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'identity',  # 禁用压缩以避免解码问题
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # 使用自定义session配置
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            logger.info(f"尝试访问: {target_url}, 代理: {proxy_config['name'] if proxy_config else 'Direct'}")
            
            # 先尝试直接访问（如果代理失败）
            try:
                response = session.get(
                    target_url,
                    proxies=proxies,
                    timeout=30,
                    verify=False,  # 忽略SSL验证
                    allow_redirects=True
                )
                logger.info(f"代理访问成功: {response.status_code}")
            except Exception as proxy_error:
                logger.warning(f"代理访问失败: {proxy_error}, 尝试直接访问")
                # 代理失败时，尝试直接访问
                response = session.get(
                    target_url,
                    timeout=30,
                    verify=False,
                    allow_redirects=True
                )
                logger.info(f"直接访问成功: {response.status_code}")
            
            if response.status_code == 200:
                # 获取响应内容和类型
                content_type = response.headers.get('content-type', '').lower()
                raw_content = response.content
                
                # 调试信息
                logger.info(f"响应内容类型: {content_type}")
                logger.info(f"响应内容长度: {len(raw_content)}")
                
                # 检测和处理编码
                try:
                    # 优先使用响应头中的编码信息
                    charset = None
                    if 'charset=' in content_type:
                        charset = content_type.split('charset=')[1].split(';')[0].strip()
                    
                    # 如果没有指定编码，尝试检测
                    if not charset:
                        import chardet
                        detected = chardet.detect(raw_content)
                        charset = detected.get('encoding', 'utf-8')
                        logger.info(f"检测到的编码: {charset}, 置信度: {detected.get('confidence', 0)}")
                    
                    # 使用检测到的编码解码内容
                    if charset:
                        try:
                            content = raw_content.decode(charset, errors='replace')
                        except (UnicodeDecodeError, LookupError):
                            content = raw_content.decode('utf-8', errors='replace')
                    else:
                        content = raw_content.decode('utf-8', errors='replace')
                        
                except ImportError:
                    # 如果没有chardet库，使用简单的编码处理
                    logger.warning("chardet库未安装，使用简单编码处理")
                    try:
                        # 尝试常见编码
                        for encoding in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                            try:
                                content = raw_content.decode(encoding)
                                logger.info(f"成功使用编码: {encoding}")
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            # 如果都失败了，强制使用utf-8
                            content = raw_content.decode('utf-8', errors='replace')
                            logger.warning("所有编码尝试失败，使用UTF-8强制解码")
                    except Exception as e:
                        logger.error(f"编码处理失败: {e}")
                        content = str(raw_content, errors='replace')
                
                # 对HTML内容进行处理
                if 'text/html' in content_type:
                    # 处理相对路径URL
                    import re
                    from urllib.parse import urljoin, urlparse
                    
                    parsed_url = urlparse(target_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    
                    # 确保HTML头部包含正确的编码声明
                    if '<head>' in content and 'charset' not in content:
                        content = content.replace('<head>', '<head><meta charset="UTF-8">')
                    elif '<html>' in content and '<head>' not in content:
                        content = content.replace('<html>', '<html><head><meta charset="UTF-8"></head>')
                    elif not content.startswith('<!DOCTYPE') and not content.startswith('<html>'):
                        content = f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>{content}</body></html>'
                    
                    # 修复相对路径 - 更安全的处理方式
                    try:
                        content = re.sub(r'href="/', f'href="{base_url}/', content)
                        content = re.sub(r'src="/', f'src="{base_url}/', content)
                        content = re.sub(r"href='/", f"href='{base_url}/", content)
                        content = re.sub(r"src='/", f"src='{base_url}/", content)
                        
                        # 修复JavaScript和CSS中的相对路径
                        content = re.sub(r'url\("/', f'url("{base_url}/', content)
                        content = re.sub(r"url\('/", f"url('{base_url}/", content)
                        
                        # 移除可能导致问题的脚本和不安全内容
                        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                        content = re.sub(r'javascript:', 'void(0); //', content, flags=re.IGNORECASE)
                        
                    except Exception as regex_error:
                        logger.warning(f"URL替换失败: {regex_error}, 使用原始内容")
                
                # 最终检查：确保内容是字符串格式
                if isinstance(content, bytes):
                    content = content.decode('utf-8', errors='replace')
                
                # 检查内容是否为空或过短
                if not content or len(content.strip()) < 10:
                    logger.warning("获取的内容为空或过短，可能存在问题")
                    return JsonResponse({
                        'success': False,
                        'error': '获取的网页内容为空，请检查网址是否正确或稍后重试'
                    })
                
                # 检查是否为二进制内容（可能被错误处理了）
                if len([c for c in content[:100] if ord(c) > 127]) > 50:  # 如果前100个字符中超过50个非ASCII字符
                    logger.warning("内容可能包含大量二进制数据，尝试重新处理")
                    # 尝试重新获取，这次明确请求text/html
                    try:
                        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                        retry_response = session.get(
                            target_url,
                            proxies=proxies,
                            timeout=30,
                            verify=False,
                            allow_redirects=True,
                            headers=headers
                        )
                        if retry_response.status_code == 200:
                            retry_content = retry_response.text
                            if len(retry_content) > len(content):
                                content = retry_content
                                logger.info("重新获取成功，使用新内容")
                    except Exception as retry_error:
                        logger.warning(f"重新获取失败: {retry_error}")
                
                return JsonResponse({
                    'success': True,
                    'data': {
                        'content': content,
                        'url': target_url,
                        'status_code': response.status_code,
                        'content_type': content_type,
                        'proxy_used': proxy_config['name'] if proxy_config else 'Direct',
                        'final_url': str(response.url),
                        'content_length': len(content),
                        'charset_used': charset if 'charset' in locals() else 'unknown'
                    }
                })
            else:
                logger.warning(f"目标网站响应错误: {response.status_code}")
                return JsonResponse({
                    'success': False,
                    'error': f'目标网站响应错误: {response.status_code}，请稍后重试'
                })
                
        except requests.exceptions.Timeout:
            return JsonResponse({
                'success': False,
                'error': '网络连接超时，请检查网址或稍后重试，github不能作为测试的网站，用youtube做测试网站'
            })
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                'success': False,
                'error': '网络连接失败，请检查代理服务状态'
            })
        except Exception as e:
            logger.error(f"Web代理访问异常: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'访问失败: {str(e)}'
            })
        
    except Exception as e:
        logger.error(f"Web代理API错误: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'服务暂时不可用，请稍后重试'
        })

# ============================================================================
# 商业化翻墙服务系统 API
# 1. IP状态检测功能
# 2. Web翻墙浏览功能 (核心商业服务)
# 3. 专业代理列表管理
# 4. 安全访问链接创建
# ============================================================================
