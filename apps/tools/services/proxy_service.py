import json
import logging
import random
import time
from typing import Dict, List, Tuple

import requests

logger = logging.getLogger(__name__)


class ProxyService:
    """代理翻墙服务类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        # 免费代理池（示例）
        self.free_proxies = [
            # 这里可以添加一些免费代理服务器
            # 实际使用时建议使用付费代理服务
        ]

        # 代理服务配置
        self.proxy_config = {"timeout": 10, "max_retries": 3, "retry_delay": 1}

    def get_working_proxies(self) -> List[Dict]:
        """获取可用的代理列表"""
        working_proxies = []

        # 测试免费代理
        for proxy in self.free_proxies:
            if self.test_proxy(proxy):
                working_proxies.append(proxy)

        return working_proxies

    def test_proxy(self, proxy: Dict) -> bool:
        """测试代理是否可用"""
        try:
            test_url = "http://httpbin.org/ip"
            response = self.session.get(
                test_url, proxies={"http": proxy["url"], "https": proxy["url"]}, timeout=self.proxy_config["timeout"]
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"代理测试失败: {proxy['url']}, 错误: {str(e)}")
            return False

    def make_request(
        self, url: str, method: str = "GET", data: Dict = None, use_proxy: bool = True, custom_proxy: str = None
    ) -> Tuple[bool, Dict]:
        """通过代理发送请求"""
        try:
            # 准备请求参数
            request_kwargs = {"timeout": self.proxy_config["timeout"]}

            # 设置代理
            if use_proxy:
                if custom_proxy:
                    request_kwargs["proxies"] = {"http": custom_proxy, "https": custom_proxy}
                else:
                    # 使用可用代理池
                    working_proxies = self.get_working_proxies()
                    if working_proxies:
                        proxy = random.choice(working_proxies)
                        request_kwargs["proxies"] = {"http": proxy["url"], "https": proxy["url"]}

            # 发送请求
            if method.upper() == "GET":
                response = self.session.get(url, **request_kwargs)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, **request_kwargs)
            else:
                return False, {"error": "不支持的请求方法"}

            return True, {
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "url": response.url,
            }

        except requests.exceptions.ProxyError as e:
            return False, {"error": f"代理连接失败: {str(e)}"}
        except requests.exceptions.Timeout as e:
            return False, {"error": f"请求超时: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return False, {"error": f"请求失败: {str(e)}"}
        except Exception as e:
            return False, {"error": f"未知错误: {str(e)}"}

    def check_website_accessibility(self, url: str, use_proxy: bool = True) -> Dict:
        """检查网站可访问性"""
        try:
            success, result = self.make_request(url, use_proxy=use_proxy)

            if success:
                return {
                    "accessible": True,
                    "status_code": result["status_code"],
                    "response_time": result.get("response_time", 0),
                    "message": "网站可正常访问",
                }
            else:
                return {"accessible": False, "error": result["error"], "message": "网站无法访问"}

        except Exception as e:
            return {"accessible": False, "error": str(e), "message": "检查过程中发生错误"}

    def get_geolocation_info(self, ip: str = None) -> Dict:
        """获取地理位置信息"""
        try:
            if not ip:
                # 获取当前IP
                success, result = self.make_request("http://httpbin.org/ip", use_proxy=False)
                if success:
                    ip = json.loads(result["content"]).get("origin", "").split(",")[0]
                else:
                    return {"error": "无法获取IP地址"}

            # 获取地理位置信息
            geo_url = f"http://ip-api.com/json/{ip}"
            success, result = self.make_request(geo_url, use_proxy=False)

            if success:
                geo_data = json.loads(result["content"])
                return {
                    "ip": ip,
                    "country": geo_data.get("country", ""),
                    "region": geo_data.get("regionName", ""),
                    "city": geo_data.get("city", ""),
                    "isp": geo_data.get("isp", ""),
                    "timezone": geo_data.get("timezone", ""),
                    "lat": geo_data.get("lat", ""),
                    "lon": geo_data.get("lon", ""),
                }
            else:
                return {"error": "无法获取地理位置信息"}

        except Exception as e:
            return {"error": f"获取地理位置信息失败: {str(e)}"}

    def test_common_websites(self) -> List[Dict]:
        """测试常见网站的访问性"""
        test_sites = [
            {"name": "Google", "url": "https://www.google.com"},
            {"name": "YouTube", "url": "https://www.youtube.com"},
            {"name": "Facebook", "url": "https://www.facebook.com"},
            {"name": "Twitter", "url": "https://twitter.com"},
            {"name": "GitHub", "url": "https://github.com"},
            {"name": "Stack Overflow", "url": "https://stackoverflow.com"},
            {"name": "Reddit", "url": "https://www.reddit.com"},
            {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
        ]

        results = []
        for site in test_sites:
            # 先测试直连
            direct_result = self.check_website_accessibility(site["url"], use_proxy=False)

            # 再测试代理
            proxy_result = self.check_website_accessibility(site["url"], use_proxy=True)

            results.append(
                {
                    "name": site["name"],
                    "url": site["url"],
                    "direct_access": direct_result["accessible"],
                    "proxy_access": proxy_result["accessible"],
                    "direct_error": direct_result.get("error", ""),
                    "proxy_error": proxy_result.get("error", ""),
                    "status": "blocked" if not direct_result["accessible"] and proxy_result["accessible"] else "normal",
                }
            )

        return results

    def get_proxy_status(self) -> Dict:
        """获取代理状态信息"""
        try:
            # 获取当前IP信息
            current_ip_info = self.get_geolocation_info()

            # 测试网站访问性
            website_tests = self.test_common_websites()

            # 统计信息
            total_sites = len(website_tests)
            blocked_sites = len([site for site in website_tests if site["status"] == "blocked"])
            accessible_sites = len([site for site in website_tests if site["proxy_access"]])

            return {
                "current_ip": current_ip_info,
                "website_tests": website_tests,
                "statistics": {
                    "total_sites": total_sites,
                    "blocked_sites": blocked_sites,
                    "accessible_with_proxy": accessible_sites,
                    "block_rate": round(blocked_sites / total_sites * 100, 2) if total_sites > 0 else 0,
                },
                "timestamp": time.time(),
            }

        except Exception as e:
            return {"error": f"获取代理状态失败: {str(e)}"}


# 全局代理服务实例
proxy_service = ProxyService()
