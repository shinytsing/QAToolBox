"""
浏览器代理配置视图
"""

import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.browser_proxy_config import browser_proxy_config

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def configure_browser_proxy(request):
    """配置浏览器代理"""
    try:
        data = json.loads(request.body) if request.body else {}
        proxy_host = data.get("proxy_host", "127.0.0.1")
        proxy_port = data.get("proxy_port", 7890)
        browser_type = data.get("browser_type", "all")  # all, chrome, edge, safari, system

        # 创建配置实例
        config = browser_proxy_config.__class__(proxy_host, proxy_port)

        results = {}

        if browser_type == "all":
            # 配置所有浏览器
            results = config.auto_configure_all()
        elif browser_type == "chrome":
            success, message = config.configure_chrome_proxy()
            results["chrome"] = {"success": success, "message": message}
        elif browser_type == "edge":
            success, message = config.configure_edge_proxy()
            results["edge"] = {"success": success, "message": message}
        elif browser_type == "safari":
            success, message = config.configure_safari_proxy()
            results["safari"] = {"success": success, "message": message}
        elif browser_type == "system":
            success, message = config.configure_system_proxy()
            results["system_proxy"] = {"success": success, "message": message}
        else:
            return JsonResponse({"success": False, "message": f"不支持的浏览器类型: {browser_type}"})

        # 检查是否有成功的配置
        success_count = sum(1 for result in results.values() if result.get("success", False))
        total_count = len(results)

        return JsonResponse(
            {"success": success_count > 0, "message": f"成功配置 {success_count}/{total_count} 个代理", "results": results}
        )

    except Exception as e:
        logger.error(f"配置浏览器代理失败: {e}")
        return JsonResponse({"success": False, "message": f"配置失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def disable_browser_proxy(request):
    """禁用浏览器代理"""
    try:
        data = json.loads(request.body) if request.body else {}
        proxy_type = data.get("proxy_type", "all")  # all, system, browsers

        config = browser_proxy_config.__class__()
        results = {}

        if proxy_type == "all" or proxy_type == "system":
            success, message = config.disable_proxy()
            results["system_proxy"] = {"success": success, "message": message}

        if proxy_type == "all" or proxy_type == "browsers":
            # 这里可以添加禁用浏览器代理的逻辑
            # 目前主要禁用系统代理
            pass

        success_count = sum(1 for result in results.values() if result.get("success", False))

        return JsonResponse({"success": success_count > 0, "message": f"成功禁用 {success_count} 个代理", "results": results})

    except Exception as e:
        logger.error(f"禁用浏览器代理失败: {e}")
        return JsonResponse({"success": False, "message": f"禁用失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def get_proxy_status(request):
    """获取代理状态"""
    try:
        config = browser_proxy_config.__class__()
        status = config.get_proxy_status()

        return JsonResponse({"success": True, "data": status})

    except Exception as e:
        logger.error(f"获取代理状态失败: {e}")
        return JsonResponse({"success": False, "message": f"获取状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def test_proxy_connection(request):
    """测试代理连接"""
    try:
        data = json.loads(request.body) if request.body else {}
        proxy_host = data.get("proxy_host", "127.0.0.1")
        proxy_port = data.get("proxy_port", 7890)
        test_url = data.get("test_url", "http://httpbin.org/ip")

        import socket

        import requests

        # 首先测试端口是否开放
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((proxy_host, proxy_port))
            sock.close()

            if result != 0:
                return JsonResponse(
                    {"success": False, "message": f"端口 {proxy_host}:{proxy_port} 未开放", "error": "Port not open"}
                )
        except Exception as e:
            return JsonResponse({"success": False, "message": f"端口测试失败: {str(e)}", "error": str(e)})

        # 测试代理连接
        try:
            proxies = {"http": f"http://{proxy_host}:{proxy_port}", "https": f"http://{proxy_host}:{proxy_port}"}

            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=10,
                verify=True,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            )

            if response.status_code == 200:
                return JsonResponse(
                    {
                        "success": True,
                        "message": f"代理连接成功: {proxy_host}:{proxy_port}",
                        "data": {
                            "proxy_host": proxy_host,
                            "proxy_port": proxy_port,
                            "test_url": test_url,
                            "response_status": response.status_code,
                            "response_data": response.text[:500],  # 限制返回数据长度
                        },
                    }
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"代理连接失败，状态码: {response.status_code}",
                        "error": f"HTTP {response.status_code}",
                    }
                )

        except requests.exceptions.ProxyError as e:
            return JsonResponse({"success": False, "message": f"代理连接错误: {str(e)}", "error": "Proxy connection error"})
        except requests.exceptions.Timeout as e:
            return JsonResponse({"success": False, "message": f"代理连接超时: {str(e)}", "error": "Connection timeout"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"代理测试失败: {str(e)}", "error": str(e)})

    except Exception as e:
        logger.error(f"代理连接测试失败: {e}")
        return JsonResponse({"success": False, "message": f"测试失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def quick_proxy_setup(request):
    """一键代理设置"""
    try:
        data = json.loads(request.body) if request.body else {}
        proxy_host = data.get("proxy_host", "127.0.0.1")
        proxy_port = data.get("proxy_port", 7890)

        # 创建配置实例
        config = browser_proxy_config.__class__(proxy_host, proxy_port)

        # 自动配置所有代理
        results = config.auto_configure_all()

        # 统计结果
        success_count = sum(1 for result in results.values() if result.get("success", False))
        total_count = len(results)

        # 生成使用说明
        instructions = []
        if results.get("system_proxy", {}).get("success"):
            instructions.append("✅ 系统代理已配置")
        if results.get("chrome", {}).get("success"):
            instructions.append("✅ Chrome代理已配置")
        if results.get("edge", {}).get("success"):
            instructions.append("✅ Edge代理已配置")
        if results.get("safari", {}).get("success"):
            instructions.append("✅ Safari代理已配置")

        instructions.extend(
            [
                "",
                "🌐 现在您可以访问以下网站测试代理：",
                "• https://www.youtube.com",
                "• https://www.google.com",
                "• https://www.facebook.com",
                "• https://www.twitter.com",
                "",
                "💡 如果某些网站无法访问，请尝试：",
                "1. 重启浏览器",
                "2. 切换Clash代理节点",
                "3. 检查Clash服务状态",
            ]
        )

        return JsonResponse(
            {
                "success": success_count > 0,
                "message": f"一键代理设置完成！成功配置 {success_count}/{total_count} 个代理",
                "results": results,
                "instructions": instructions,
            }
        )

    except Exception as e:
        logger.error(f"一键代理设置失败: {e}")
        return JsonResponse({"success": False, "message": f"一键设置失败: {str(e)}"})
