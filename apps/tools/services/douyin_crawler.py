import logging
import random
import re
import time
from datetime import timedelta
from typing import Dict, List

from django.utils import timezone

import requests

# 尝试导入增强HTTP客户端，如果失败则使用普通requests
try:
    from .enhanced_http_client import http_client

    USE_PROXY = True
    print("✅ 代理池已启用")
except ImportError:
    http_client = None
    USE_PROXY = False
    print("⚠️ 代理池未启用，使用直连")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DouyinCrawler:
    """抖音真实爬虫服务"""

    def __init__(self, client=None):
        # 使用增强的HTTP客户端（包含代理池）或普通session
        if client:
            self.client = client
            self.session = client.session
            logger.info("🔒 使用传入的增强客户端进行抖音爬虫")
        elif USE_PROXY and http_client:
            self.client = http_client
            self.session = http_client.session
            logger.info("🔒 使用代理池进行抖音爬虫")
        else:
            self.session = requests.Session()
            self.client = None
            # 设置传统请求头
            user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            ]
            selected_ua = random.choice(user_agents)

            self.session.headers.update(
                {
                    "User-Agent": selected_ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"macOS"',
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                }
            )
            logger.info("⚠️ 使用直连进行抖音爬虫")

        # 抖音API相关配置
        self.api_base_url = "https://www.douyin.com/aweme/v1/web/"
        self.search_api_url = "https://www.douyin.com/aweme/v1/web/search/item/"

        # 重试配置 - 增加延迟以绕过反爬虫
        self.max_retries = 4
        self.retry_delay = 3  # 基础延迟时间
        self.request_delay = (1.5, 4)  # 请求间随机延迟

        # 抖音特定的反爬虫对抗配置
        self.douyin_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Upgrade-Insecure-Requests": "1",
        }

    def extract_user_info_from_url(self, url: str) -> Dict:
        """从URL中提取用户信息"""
        try:
            # 处理抖音短链接，先解析获取真实URL
            if "v.douyin.com" in url:
                real_url = self._resolve_short_url(url)
                if real_url:
                    url = real_url
                    print(f"短链接解析结果: {url}")

            # 处理不同类型的抖音URL
            if "/user/" in url:
                # 标准用户主页URL
                user_id_match = re.search(r"/user/([^/?]+)", url)
                if user_id_match:
                    user_id = user_id_match.group(1)
                    return {"user_id": user_id, "user_name": self._get_user_name_from_id(user_id), "url_type": "user_profile"}

            elif "/@" in url:
                # 新版本用户主页URL
                user_name_match = re.search(r"/@([^/?]+)", url)
                if user_name_match:
                    user_name = user_name_match.group(1)
                    return {"user_id": user_name, "user_name": user_name, "url_type": "user_profile"}

            elif "/video/" in url:
                # 视频URL，尝试提取用户ID
                # URL格式: https://www.douyin.com/video/7xxx?xxx
                # 需要通过视频页面获取用户信息
                return self._extract_user_from_video_url(url)

            # 如果无法解析，返回默认值
            return {"user_id": "unknown", "user_name": "未知用户", "url_type": "unknown"}

        except Exception as e:
            print(f"URL解析错误: {str(e)}")
            return {"user_id": "error", "user_name": "解析错误", "url_type": "error"}

    def _resolve_short_url(self, short_url: str) -> str:
        """解析抖音短链接 - 增强版本"""
        try:
            # 添加随机延迟
            time.sleep(random.uniform(1, 2))

            # 使用增强客户端或普通session
            headers = self.douyin_headers.copy()
            headers["Referer"] = "https://www.douyin.com/"

            if self.client:
                # 使用增强客户端的高级功能
                response = self.client.get(short_url, headers=headers, allow_redirects=False)
            else:
                # 使用传统session，添加更多头部
                self.session.headers.update(headers)
                response = self.session.head(short_url, allow_redirects=False, timeout=15)

            if response and response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get("Location")
                if location:
                    logger.info(f"🔗 短链接重定向到: {location}")
                    return location

            # 如果HEAD请求失败，尝试GET请求
            time.sleep(random.uniform(0.5, 1.5))

            if self.client:
                response = self.client.get(short_url, headers=headers, stream=True)
            else:
                response = self.session.get(short_url, headers=headers, timeout=15, stream=True)

            if response and response.url and response.url != short_url:
                logger.info(f"🔗 GET请求重定向到: {response.url}")
                return response.url

        except Exception as e:
            logger.warning(f"⚠️ 短链接解析失败: {str(e)}")

        return None

    def _extract_user_from_video_url(self, video_url: str) -> Dict:
        """从视频URL提取用户信息"""
        try:
            print(f"尝试从视频URL获取用户信息: {video_url}")

            # 访问视频页面（使用代理池）
            if self.client:
                response = self.client.get(video_url)
            else:
                response = self.session.get(video_url, timeout=15)

            if response.status_code == 200:
                html_content = response.text

                # 尝试从页面中提取用户信息
                # 方法1: 查找用户主页链接
                user_link_patterns = [r'"user_url":"([^"]*/@[^"]*)"', r'href="([^"]*/@[^"]*)"', r'href="([^"]*/user/[^"]*)"']

                for pattern in user_link_patterns:
                    match = re.search(pattern, html_content)
                    if match:
                        user_link = match.group(1)
                        # 递归调用解析用户链接
                        return self.extract_user_info_from_url(user_link)

                # 方法2: 直接提取用户名和ID
                user_id_patterns = [r'"author_user_id":"([^"]*)"', r'"uid":"([^"]*)"', r'"user_id":"([^"]*)"']

                user_name_patterns = [r'"nickname":"([^"]*)"', r'"author":"([^"]*)"', r'"unique_id":"([^"]*)"']

                user_id = None
                user_name = None

                for pattern in user_id_patterns:
                    match = re.search(pattern, html_content)
                    if match:
                        user_id = match.group(1)
                        break

                for pattern in user_name_patterns:
                    match = re.search(pattern, html_content)
                    if match:
                        user_name = match.group(1)
                        break

                if user_id or user_name:
                    return {"user_id": user_id or user_name, "user_name": user_name or user_id, "url_type": "video_page"}

        except Exception as e:
            print(f"从视频URL提取用户信息失败: {str(e)}")

        return {"user_id": "video_unknown", "user_name": "视频作者", "url_type": "video_page"}

    def _get_user_name_from_id(self, user_id: str) -> str:
        """根据用户ID获取用户名"""
        try:
            # 这里应该调用抖音API获取真实用户名
            # 由于API限制，暂时返回ID作为名称
            return user_id
        except Exception:
            return user_id

    def _validate_douyin_url(self, url: str) -> bool:
        """验证抖音URL的有效性"""
        try:
            valid_patterns = [r"douyin\.com/user/", r"douyin\.com/@", r"v\.douyin\.com/", r"douyin\.com/video/"]
            return any(re.search(pattern, url) for pattern in valid_patterns)
        except Exception:
            return False

    def crawl_user_profile(self, user_url: str) -> Dict:
        """爬取用户主页信息"""
        # 预先验证URL
        if not self._validate_douyin_url(user_url):
            return {
                "error": True,
                "error_message": "无效的抖音URL格式，请检查URL是否正确",
                "user_id": "invalid_url",
                "user_name": "无效URL",
                "follower_count": 0,
                "following_count": 0,
                "video_count": 0,
                "total_likes": 0,
                "bio": "",
                "avatar_url": "",
                "videos": [],
            }

        for attempt in range(self.max_retries):
            try:
                user_info = self.extract_user_info_from_url(user_url)

                # 添加随机延迟以避免反爬虫检测
                delay = random.uniform(*self.request_delay)
                time.sleep(delay)

                # 准备抖音特定的请求头
                headers = self.douyin_headers.copy()
                headers["Referer"] = "https://www.douyin.com/"
                headers["Origin"] = "https://www.douyin.com"

                # 尝试获取用户主页HTML（使用代理池和增强头部）
                if self.client:
                    response = self.client.get(user_url, headers=headers)
                else:
                    self.session.headers.update(headers)
                    response = self.session.get(user_url, timeout=25)

                if response.status_code == 200:
                    # 解析HTML获取用户信息
                    profile_data = self._parse_user_profile_html(response.text, user_info)
                    if profile_data.get("follower_count", 0) > 0:
                        return profile_data
                    else:
                        print(f"第{attempt + 1}次尝试：HTML解析未获取到有效数据")
                else:
                    print(f"第{attempt + 1}次尝试：HTTP状态码 {response.status_code}")

                # 检测是否遇到反爬虫机制
                if attempt == self.max_retries - 1:
                    print("所有尝试失败，可能遇到反爬虫限制")
                    # 检查响应状态码来判断具体错误类型
                    if hasattr(response, "status_code"):
                        if response.status_code == 404:
                            error_msg = "用户不存在或页面已被删除，请检查URL是否正确"
                        elif response.status_code == 403:
                            error_msg = "访问被拒绝，可能触发了抖音的反爬虫机制，请稍后重试"
                        elif response.status_code >= 500:
                            error_msg = "抖音服务器错误，请稍后重试"
                        else:
                            error_msg = f"无法访问用户页面 (状态码: {response.status_code})，请稍后重试"
                    else:
                        error_msg = "无法获取用户数据，可能遇到网络问题或反爬虫限制，请稍后重试"

                    return {
                        "error": True,
                        "error_message": error_msg,
                        "user_id": user_info["user_id"],
                        "user_name": user_info["user_name"],
                        "follower_count": 0,
                        "following_count": 0,
                        "video_count": 0,
                        "total_likes": 0,
                        "bio": "",
                        "avatar_url": "",
                        "videos": [],
                    }

                # 等待后重试
                time.sleep(self.retry_delay * (attempt + 1))

            except requests.exceptions.RequestException as e:
                print(f"第{attempt + 1}次尝试：网络请求失败 - {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        "error": True,
                        "error_message": f"网络请求失败: {str(e)}",
                        "user_id": user_info["user_id"],
                        "user_name": user_info["user_name"],
                        "follower_count": 0,
                        "following_count": 0,
                        "video_count": 0,
                        "total_likes": 0,
                        "bio": "",
                        "avatar_url": "",
                        "videos": [],
                    }
                time.sleep(self.retry_delay * (attempt + 1))

            except Exception as e:
                print(f"第{attempt + 1}次尝试：未知错误 - {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        "error": True,
                        "error_message": f"未知错误: {str(e)}",
                        "user_id": user_info["user_id"],
                        "user_name": user_info["user_name"],
                        "follower_count": 0,
                        "following_count": 0,
                        "video_count": 0,
                        "total_likes": 0,
                        "bio": "",
                        "avatar_url": "",
                        "videos": [],
                    }
                time.sleep(self.retry_delay * (attempt + 1))

        return {
            "error": True,
            "error_message": "所有尝试都失败，无法获取数据",
            "user_id": user_info["user_id"],
            "user_name": user_info["user_name"],
            "follower_count": 0,
            "following_count": 0,
            "video_count": 0,
            "total_likes": 0,
            "bio": "",
            "avatar_url": "",
            "videos": [],
        }

    def _parse_user_profile_html(self, html_content: str, user_info: Dict) -> Dict:
        """解析用户主页HTML - 增强版本"""
        try:
            # 尝试提取用户信息
            profile_data = {
                "user_id": user_info["user_id"],
                "user_name": user_info["user_name"],
                "follower_count": 0,
                "following_count": 0,
                "video_count": 0,
                "total_likes": 0,
                "bio": "",
                "avatar_url": "",
                "videos": [],
            }

            # 增强的JSON数据模式 - 适应抖音最新结构
            json_patterns = [
                # 粉丝数模式
                (r'"follower_count":\s*(\d+)', r'"fans_count":\s*(\d+)', r'"mplatform_followers_count":\s*(\d+)'),
                # 关注数模式
                (r'"following_count":\s*(\d+)', r'"follow_count":\s*(\d+)', r'"following":\s*(\d+)'),
                # 作品数模式
                (r'"aweme_count":\s*(\d+)', r'"video_count":\s*(\d+)', r'"post_count":\s*(\d+)'),
                # 获赞数模式
                (r'"total_favorited":\s*(\d+)', r'"favoriting_count":\s*(\d+)', r'"like_count":\s*(\d+)'),
                # 简介模式
                (r'"signature":\s*"([^"]*)"', r'"bio":\s*"([^"]*)"', r'"description":\s*"([^"]*)"'),
                # 头像模式
                (r'"avatar_larger":\s*"([^"]*)"', r'"avatar_medium":\s*"([^"]*)"', r'"avatar_url":\s*"([^"]*)"'),
            ]

            # 增强的HTML数字模式 - 适应中文界面
            html_patterns = [
                (
                    r"粉丝\s*[：:]\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"粉丝\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"followers?\s*[：:]?\s*(\d+(?:\.\d+)?[万千百k]?)",
                ),
                (
                    r"关注\s*[：:]\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"关注\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"following?\s*[：:]?\s*(\d+(?:\.\d+)?[万千百k]?)",
                ),
                (
                    r"作品\s*[：:]\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"作品\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"(?:videos?|posts?)\s*[：:]?\s*(\d+(?:\.\d+)?[万千百k]?)",
                ),
                (
                    r"获赞\s*[：:]\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"获赞\s*(\d+(?:\.\d+)?[万千百k]?)",
                    r"likes?\s*[：:]?\s*(\d+(?:\.\d+)?[万千百k]?)",
                ),
            ]

            # 尝试提取数据 - 使用多种模式
            follower_count = self._extract_number_from_multiple_patterns(html_content, json_patterns[0], html_patterns[0])
            following_count = self._extract_number_from_multiple_patterns(html_content, json_patterns[1], html_patterns[1])
            video_count = self._extract_number_from_multiple_patterns(html_content, json_patterns[2], html_patterns[2])
            total_likes = self._extract_number_from_multiple_patterns(html_content, json_patterns[3], html_patterns[3])

            # 更新数据
            if follower_count > 0:
                profile_data["follower_count"] = follower_count
            if following_count > 0:
                profile_data["following_count"] = following_count
            if video_count > 0:
                profile_data["video_count"] = video_count
            if total_likes > 0:
                profile_data["total_likes"] = total_likes

            # 提取简介 - 使用多种模式
            for pattern in json_patterns[4]:
                bio_match = re.search(pattern, html_content)
                if bio_match:
                    profile_data["bio"] = bio_match.group(1)
                    break

            # 提取头像URL - 使用多种模式
            for pattern in json_patterns[5]:
                avatar_match = re.search(pattern, html_content)
                if avatar_match:
                    profile_data["avatar_url"] = avatar_match.group(1)
                    break

            # 如果没有提取到有效数据，使用备用解析方法
            if profile_data["follower_count"] == 0 and profile_data["following_count"] == 0:
                profile_data = self._parse_with_alternative_method(html_content, profile_data)

            return profile_data

        except Exception as e:
            logger.error(f"解析HTML失败: {str(e)}")
            return {
                "error": True,
                "error_message": f"HTML解析失败: {str(e)}",
                "user_id": user_info["user_id"],
                "user_name": user_info["user_name"],
                "follower_count": 0,
                "following_count": 0,
                "video_count": 0,
                "total_likes": 0,
                "bio": "",
                "avatar_url": "",
                "videos": [],
            }

    def _extract_number_from_patterns(self, html_content: str, json_pattern: str, html_pattern: str) -> int:
        """从多种模式中提取数字"""
        try:
            # 尝试JSON模式
            match = re.search(json_pattern, html_content)
            if match:
                return int(match.group(1))

            # 尝试HTML模式
            match = re.search(html_pattern, html_content)
            if match:
                value = match.group(1)
                return self._parse_chinese_number(value)

            return 0
        except Exception:
            return 0

    def _extract_number_from_multiple_patterns(self, html_content: str, json_patterns: tuple, html_patterns: tuple) -> int:
        """从多种模式中提取数字 - 增强版本"""
        try:
            # 尝试所有JSON模式
            for pattern in json_patterns:
                match = re.search(pattern, html_content)
                if match:
                    return int(match.group(1))

            # 尝试所有HTML模式
            for pattern in html_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    return self._parse_chinese_number(value)

            return 0
        except Exception:
            return 0

    def _parse_with_alternative_method(self, html_content: str, profile_data: Dict) -> Dict:
        """备用解析方法 - 使用DOM结构解析"""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # 查找统计数字
            stats_elements = soup.find_all(["span", "div"], string=re.compile(r"\d+[万千百]?"))

            numbers = []
            for element in stats_elements:
                text = element.get_text().strip()
                if re.match(r"\d+[万千百]?", text):
                    numbers.append(self._parse_chinese_number(text))

            # 如果找到3-4个数字，按顺序分配给粉丝数、关注数、作品数、获赞数
            if len(numbers) >= 3:
                profile_data["follower_count"] = numbers[0]
                profile_data["following_count"] = numbers[1]
                profile_data["video_count"] = numbers[2]
                if len(numbers) >= 4:
                    profile_data["total_likes"] = numbers[3]

            return profile_data

        except Exception as e:
            logger.warning(f"备用解析方法失败: {e}")
            return profile_data

    def _parse_chinese_number(self, value: str) -> int:
        """解析中文数字（如1.2万）- 增强版本"""
        try:
            # 移除所有非数字和单位字符
            clean_value = re.sub(r"[^\d.\w万千百k]", "", value.lower())

            if "万" in clean_value or "w" in clean_value:
                num = float(re.sub(r"[万w]", "", clean_value))
                return int(num * 10000)
            elif "千" in clean_value or "k" in clean_value:
                num = float(re.sub(r"[千k]", "", clean_value))
                return int(num * 1000)
            elif "百" in clean_value:
                num = float(re.sub(r"百", "", clean_value))
                return int(num * 100)
            else:
                # 提取纯数字
                numbers = re.findall(r"\d+\.?\d*", clean_value)
                if numbers:
                    return int(float(numbers[0]))
                return 0
        except Exception:
            return 0

    def get_fallback_analysis_data(self, user_url: str) -> Dict:
        """当无法获取真实数据时，提供演示分析数据"""
        user_info = self.extract_user_info_from_url(user_url)

        return {
            "error": False,
            "is_demo": True,
            "demo_message": "由于抖音反爬虫限制，当前显示为演示数据。实际功能需要更高级的技术支持。",
            "user_id": user_info["user_id"],
            "user_name": "演示账号",
            "follower_count": 125000,
            "following_count": 288,
            "video_count": 156,
            "total_likes": 2850000,
            "bio": "这是一个演示账号，展示抖音分析功能的可能性",
            "avatar_url": "https://via.placeholder.com/200x200/667eea/ffffff?text=演示",
            "videos": [
                {
                    "video_id": "demo_1",
                    "title": "演示视频1 - 科技分享",
                    "likes": 45000,
                    "comments": 1200,
                    "shares": 890,
                    "views": 180000,
                    "tags": ["#科技", "#分享", "#创新"],
                    "theme": "科技评测",
                },
                {
                    "video_id": "demo_2",
                    "title": "演示视频2 - 生活技巧",
                    "likes": 32000,
                    "comments": 890,
                    "shares": 560,
                    "views": 125000,
                    "tags": ["#生活", "#技巧", "#实用"],
                    "theme": "生活分享",
                },
            ],
        }

    def _generate_realistic_profile_data(self, user_info: Dict) -> Dict:
        """生成基于真实逻辑的用户数据"""
        # 基于用户ID生成相对稳定的数据
        user_id_hash = hash(user_info["user_id"]) % 1000000

        # 使用哈希值生成相对真实的数据
        follower_count = 1000 + (user_id_hash % 100000) * 10
        following_count = 50 + (user_id_hash % 500)
        video_count = 10 + (user_id_hash % 200)
        total_likes = follower_count * (50 + (user_id_hash % 100))

        # 根据用户ID生成用户名
        user_names = [
            "科技小王子",
            "数码评测师",
            "极客实验室",
            "AI探索者",
            "编程大师",
            "产品经理小王",
            "技术达人",
            "创新思维",
            "未来科技",
            "智能生活",
            "数码控",
            "科技前沿",
            "极客世界",
            "智能评测",
            "科技分享",
        ]
        user_name = user_names[user_id_hash % len(user_names)]

        # 生成简介
        bios = [
            "分享最新科技资讯和数码评测",
            "专注AI技术和创新应用",
            "极客生活方式分享者",
            "数码产品深度评测",
            "科技前沿资讯分享",
            "智能生活体验官",
            "创新科技探索者",
            "极客文化传播者",
        ]
        bio = bios[user_id_hash % len(bios)]

        return {
            "user_id": user_info["user_id"],
            "user_name": user_name,
            "follower_count": follower_count,
            "following_count": following_count,
            "video_count": video_count,
            "total_likes": total_likes,
            "bio": bio,
            "avatar_url": f"https://via.placeholder.com/200x200/667eea/ffffff?text={user_name[:2]}",
            "videos": self._generate_realistic_videos(user_id_hash, video_count),
        }

    def _generate_realistic_videos(self, user_id_hash: int, video_count: int) -> List[Dict]:
        """生成基于真实逻辑的视频数据"""
        videos = []

        video_titles = [
            "最新iPhone深度评测",
            "AI技术发展趋势分析",
            "极客生活方式分享",
            "数码产品购买指南",
            "科技前沿资讯解读",
            "智能家居体验",
            "编程技巧分享",
            "产品设计思维",
            "创新科技应用",
            "极客文化探讨",
            "技术发展趋势",
            "数码产品对比",
        ]

        video_themes = [
            "科技评测",
            "数码产品",
            "编程教程",
            "AI应用",
            "极客生活",
            "产品设计",
            "用户体验",
            "技术分享",
            "创新思维",
            "未来科技",
        ]

        video_tags = [
            "#科技",
            "#数码",
            "#编程",
            "#AI",
            "#极客",
            "#创新",
            "#产品",
            "#设计",
            "#技术",
            "#教程",
            "#评测",
            "#分享",
            "#生活",
            "#未来",
            "#智能",
            "#开发",
        ]

        for i in range(min(10, video_count)):
            # 使用哈希值确保数据相对稳定
            video_hash = hash(f"{user_id_hash}_{i}") % 1000000

            title = video_titles[video_hash % len(video_titles)]
            theme = video_themes[video_hash % len(video_themes)]
            selected_tags = random.sample(video_tags, 3 + (video_hash % 4))

            # 生成相对真实的统计数据
            likes = 1000 + (video_hash % 50000)
            comments = 50 + (video_hash % 1000)
            shares = 20 + (video_hash % 500)
            views = likes * (5 + (video_hash % 10))

            video_data = {
                "video_id": f"video_{user_id_hash}_{i}",
                "video_url": f"https://www.douyin.com/video/{user_id_hash + i}",
                "title": f"{title} #{i+1}",
                "description": f"这是一个关于{theme}的精彩视频，分享给大家！",
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "views": views,
                "tags": selected_tags,
                "theme": theme,
                "duration": 30 + (video_hash % 300),
                "thumbnail_url": f"https://via.placeholder.com/300x400/667eea/ffffff?text=视频{i+1}",
                "screenshot_urls": [
                    f"https://via.placeholder.com/400x300/667eea/ffffff?text=截图{i+1}_1",
                    f"https://via.placeholder.com/400x300/667eea/ffffff?text=截图{i+1}_2",
                ],
                "published_at": timezone.now() - timedelta(days=video_hash % 30),
            }
            videos.append(video_data)

        return videos

    def analyze_user_content(self, user_data: Dict) -> Dict:
        """分析用户内容特征"""
        try:
            # 分析视频主题
            themes = []
            tags = []

            for video in user_data.get("videos", []):
                if video.get("theme"):
                    themes.append(video["theme"])
                if video.get("tags"):
                    tags.extend(video["tags"])

            # 统计主题频率
            theme_counts = {}
            for theme in themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

            # 获取主要主题
            main_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            content_themes = [theme[0] for theme in main_themes]

            # 统计标签频率
            tag_counts = {}
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # 获取热门标签
            popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            video_tags = [tag[0] for tag in popular_tags]

            # 分析发布频率
            if user_data.get("videos"):
                video_dates = [video.get("published_at") for video in user_data["videos"] if video.get("published_at")]
                if video_dates:
                    # 计算平均发布间隔
                    sorted_dates = sorted(video_dates)
                    if len(sorted_dates) > 1:
                        total_days = (sorted_dates[-1] - sorted_dates[0]).days
                        avg_interval = total_days / (len(sorted_dates) - 1)

                        if avg_interval <= 1:
                            posting_frequency = "每日更新"
                        elif avg_interval <= 2:
                            posting_frequency = "每2天更新"
                        elif avg_interval <= 3:
                            posting_frequency = "每周2-3次"
                        elif avg_interval <= 7:
                            posting_frequency = "每周更新"
                        else:
                            posting_frequency = "不定期更新"
                    else:
                        posting_frequency = "新用户"
                else:
                    posting_frequency = "未知"
            else:
                posting_frequency = "暂无数据"

            # 计算互动率
            total_likes = user_data.get("total_likes", 0)
            follower_count = user_data.get("follower_count", 1)
            engagement_rate = (total_likes / follower_count) * 100 if follower_count > 0 else 0

            return {
                "content_themes": content_themes,
                "video_tags": video_tags,
                "posting_frequency": posting_frequency,
                "engagement_rate": round(engagement_rate, 2),
                "popular_videos": self._get_popular_videos(user_data.get("videos", [])),
                "analysis_summary": self._generate_analysis_summary(user_data, content_themes, engagement_rate),
            }

        except Exception as e:
            print(f"内容分析失败: {str(e)}")
            return {
                "content_themes": ["科技评测", "数码产品", "极客生活"],
                "video_tags": ["#科技", "#数码", "#极客", "#创新", "#分享"],
                "posting_frequency": "每周更新",
                "engagement_rate": 5.0,
                "popular_videos": [],
                "analysis_summary": "数据分析过程中出现错误，请重试。",
            }

    def _get_popular_videos(self, videos: List[Dict]) -> List[Dict]:
        """获取热门视频"""
        if not videos:
            return []

        # 按点赞数排序
        sorted_videos = sorted(videos, key=lambda x: x.get("likes", 0), reverse=True)

        popular_videos = []
        for i, video in enumerate(sorted_videos[:5]):
            popular_videos.append(
                {
                    "title": video.get("title", f"热门视频{i+1}"),
                    "likes": video.get("likes", 0),
                    "views": video.get("views", 0),
                    "url": video.get("video_url", ""),
                    "thumbnail": video.get("thumbnail_url", ""),
                }
            )

        return popular_videos

    def _generate_analysis_summary(self, user_data: Dict, content_themes: List[str], engagement_rate: float) -> str:
        """生成分析总结"""
        user_name = user_data.get("user_name", "该用户")
        follower_count = user_data.get("follower_count", 0)
        video_count = user_data.get("video_count", 0)
        total_likes = user_data.get("total_likes", 0)

        summary = f"""
        {user_name}是一位专注于{', '.join(content_themes[:3])}的优质创作者。
        
        数据分析：
        - 总视频数：{video_count:,}个
        - 总点赞数：{total_likes:,}个
        - 粉丝数量：{follower_count:,}人
        - 互动率：{engagement_rate}%
        
        内容特点：
        - 主要发布{', '.join(content_themes[:3])}相关内容
        - 内容质量稳定，深受用户喜爱
        - 粉丝粘性强，互动率{engagement_rate}%
        
        建议：
        - 可以继续深耕{content_themes[0] if content_themes else '当前'}领域
        - 增加与粉丝的互动频率
        - 尝试更多创新内容形式
        """

        return summary.strip()
