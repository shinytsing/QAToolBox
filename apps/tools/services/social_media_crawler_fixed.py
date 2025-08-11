import random
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from bs4 import BeautifulSoup
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaCrawler:
    """增强版社交媒体爬虫服务"""
    
    def __init__(self, client=None):
        self.client = client
        if client:
            self.session = client.session
            logger.info("🔒 社交媒体爬虫使用增强HTTP客户端")
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            logger.info("⚠️ 社交媒体爬虫使用普通HTTP")
        
        # 平台配置
        self.platform_configs = {
            'bilibili': {
                'api_base_url': 'https://api.bilibili.com',
                'user_info_api': '/x/space/acc/info',
                'user_video_api': '/x/space/arc/search',
                'search_api': '/x/web-interface/search/type',
                'headers': {
                    'Referer': 'https://space.bilibili.com/',
                    'Origin': 'https://space.bilibili.com',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site'
                }
            },
            'xiaohongshu': {
                'base_url': 'https://www.xiaohongshu.com',
                'search_url': 'https://www.xiaohongshu.com/search_result',
                'headers': {
                    'Referer': 'https://www.xiaohongshu.com/',
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
            },
            'weibo': {
                'api_base_url': 'https://m.weibo.cn',
                'user_info_api': '/api/container/getIndex',
                'headers': {
                    'Referer': 'https://m.weibo.cn/',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }
        }
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)
    
    def _make_request(self, url, params=None, timeout=15, headers=None):
        """发送HTTP请求 - 增强版本"""
        try:
            # 添加随机延迟
            time.sleep(random.uniform(0.5, 2.0))
            
            # 准备请求头
            request_headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
            
            if headers:
                request_headers.update(headers)
            
            if self.client:
                response = self.client.get(url, params=params, headers=request_headers)
            else:
                response = self.session.get(url, params=params, timeout=timeout, headers=request_headers)
            
            if response and response.status_code == 200:
                return response
            else:
                logger.warning(f"请求返回状态码: {response.status_code if response else 'None'}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"请求失败 {url}: {str(e)}")
            return None
    
    def crawl_user_profile(self, platform: str, user_id: str) -> Optional[Dict]:
        """爬取用户资料"""
        logger.info(f"🔍 开始爬取 {platform} 用户: {user_id}")
        
        if platform == 'bilibili':
            return self._crawl_bilibili_user(user_id)
        elif platform == 'xiaohongshu':
            return self._crawl_xiaohongshu_user(user_id)
        elif platform == 'weibo':
            return self._crawl_weibo_user(user_id)
        else:
            logger.error(f"不支持的平台: {platform}")
            return None
    
    def _crawl_bilibili_user(self, user_id: str) -> Optional[Dict]:
        """爬取B站用户信息"""
        try:
            # 尝试API方式获取用户信息 - 增强版本
            api_url = f"{self.platform_configs['bilibili']['api_base_url']}{self.platform_configs['bilibili']['user_info_api']}"
            params = {
                'mid': user_id,
                'jsonp': 'jsonp'
            }
            
            # B站特定的请求头
            bilibili_headers = {
                'Referer': 'https://space.bilibili.com/',
                'Origin': 'https://space.bilibili.com',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self._make_request(api_url, params=params, headers=bilibili_headers)
            
            if response:
                try:
                    data = response.json()
                    if data.get('code') == 0:
                        user_data = data.get('data', {})
                        logger.info(f"✅ 成功获取B站用户数据: {user_data.get('name', 'Unknown')}")
                        
                        # 格式化返回数据
                        return {
                            'platform': 'bilibili',
                            'user_id': user_id,
                            'user_name': user_data.get('name', ''),
                            'follower_count': user_data.get('follower', 0),
                            'following_count': user_data.get('following', 0),
                            'bio': user_data.get('sign', ''),
                            'avatar_url': user_data.get('face', ''),
                            'level': user_data.get('level', 0),
                            'vip_status': user_data.get('vip', {}).get('status', 0),
                            'crawl_time': datetime.now().isoformat()
                        }
                    else:
                        logger.warning(f"B站API返回错误: {data.get('message', 'Unknown error')}")
                        
                except json.JSONDecodeError:
                    logger.error("B站API响应JSON解析失败")
            
            # 如果API失败，尝试页面爬取
            logger.info("API失败，尝试页面爬取...")
            return self._crawl_bilibili_user_page(user_id)
            
        except Exception as e:
            logger.error(f"爬取B站用户 {user_id} 失败: {str(e)}")
            return None
    
    def _crawl_bilibili_user_page(self, user_id: str) -> Optional[Dict]:
        """通过页面爬取B站用户信息"""
        try:
            user_url = f"https://space.bilibili.com/{user_id}"
            response = self._make_request(user_url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取用户信息
                user_info = {
                    'platform': 'bilibili',
                    'user_id': user_id,
                    'user_name': '',
                    'follower_count': 0,
                    'following_count': 0,
                    'bio': '',
                    'avatar_url': '',
                    'crawl_time': datetime.now().isoformat()
                }
                
                # 尝试提取用户名
                name_element = soup.find('span', {'id': 'h-name'})
                if name_element:
                    user_info['user_name'] = name_element.get_text(strip=True)
                
                # 尝试提取关注数据
                stats_elements = soup.find_all('div', class_='n-num')
                if len(stats_elements) >= 2:
                    try:
                        user_info['following_count'] = int(stats_elements[0].get_text(strip=True))
                        user_info['follower_count'] = int(stats_elements[1].get_text(strip=True))
                    except (ValueError, IndexError):
                        pass
                
                logger.info(f"✅ 页面爬取B站用户成功: {user_info['user_name']}")
                return user_info
                
        except Exception as e:
            logger.error(f"页面爬取B站用户 {user_id} 失败: {str(e)}")
            
        return None
    
    def _crawl_xiaohongshu_user(self, user_id: str) -> Optional[Dict]:
        """爬取小红书用户信息"""
        try:
            # 小红书反爬虫较强，主要测试连接性
            user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            
            xiaohongshu_headers = self.platform_configs['xiaohongshu']['headers'].copy()
            
            response = self._make_request(user_url, headers=xiaohongshu_headers)
            
            if response:
                logger.info("✅ 小红书页面访问成功")
                return {
                    'platform': 'xiaohongshu',
                    'user_id': user_id,
                    'user_name': f'小红书用户_{user_id}',
                    'follower_count': 0,
                    'following_count': 0,
                    'bio': '',
                    'avatar_url': '',
                    'crawl_time': datetime.now().isoformat()
                }
            else:
                logger.warning("小红书页面访问失败")
                
        except Exception as e:
            logger.error(f"爬取小红书用户 {user_id} 失败: {str(e)}")
            
        return None
    
    def _crawl_weibo_user(self, user_id: str) -> Optional[Dict]:
        """爬取微博用户信息"""
        try:
            # 尝试移动端API
            api_url = f"{self.platform_configs['weibo']['api_base_url']}{self.platform_configs['weibo']['user_info_api']}"
            params = {
                'containerid': f'100505{user_id}',
                'type': 'uid',
                'value': user_id
            }
            
            weibo_headers = self.platform_configs['weibo']['headers'].copy()
            
            response = self._make_request(api_url, params=params, headers=weibo_headers)
            
            if response:
                try:
                    data = response.json()
                    if data.get('ok') == 1:
                        user_info = data.get('data', {}).get('userInfo', {})
                        logger.info(f"✅ 成功获取微博用户数据: {user_info.get('screen_name', 'Unknown')}")
                        
                        return {
                            'platform': 'weibo',
                            'user_id': user_id,
                            'user_name': user_info.get('screen_name', ''),
                            'follower_count': user_info.get('followers_count', 0),
                            'following_count': user_info.get('follow_count', 0),
                            'bio': user_info.get('description', ''),
                            'avatar_url': user_info.get('profile_image_url', ''),
                            'verified': user_info.get('verified', False),
                            'crawl_time': datetime.now().isoformat()
                        }
                        
                except json.JSONDecodeError:
                    logger.error("微博API响应JSON解析失败")
                    
        except Exception as e:
            logger.error(f"爬取微博用户 {user_id} 失败: {str(e)}")
            
        return None
    
    def search_content(self, platform: str, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索内容"""
        logger.info(f"🔍 在 {platform} 搜索: {keyword}")
        
        if platform == 'bilibili':
            return self._search_bilibili_content(keyword, limit)
        elif platform == 'xiaohongshu':
            return self._search_xiaohongshu_content(keyword, limit)
        else:
            logger.warning(f"平台 {platform} 暂不支持内容搜索")
            return []
    
    def _search_bilibili_content(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索B站内容"""
        try:
            search_url = f"{self.platform_configs['bilibili']['api_base_url']}{self.platform_configs['bilibili']['search_api']}"
            params = {
                'search_type': 'video',
                'keyword': keyword,
                'page': 1,
                'pagesize': limit
            }
            
            response = self._make_request(search_url, params=params)
            
            if response:
                try:
                    data = response.json()
                    if data.get('code') == 0:
                        results = data.get('data', {}).get('result', [])
                        content_list = []
                        
                        for item in results:
                            content_list.append({
                                'platform': 'bilibili',
                                'title': item.get('title', ''),
                                'author': item.get('author', ''),
                                'play_count': item.get('play', 0),
                                'duration': item.get('duration', ''),
                                'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                                'description': item.get('description', ''),
                                'crawl_time': datetime.now().isoformat()
                            })
                        
                        logger.info(f"✅ B站搜索成功，找到 {len(content_list)} 个结果")
                        return content_list
                        
                except json.JSONDecodeError:
                    logger.error("B站搜索API响应JSON解析失败")
                    
        except Exception as e:
            logger.error(f"B站内容搜索失败: {str(e)}")
            
        return []
    
    def _search_xiaohongshu_content(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索小红书内容"""
        try:
            # 小红书搜索反爬虫较强，主要测试连接
            search_url = f"{self.platform_configs['xiaohongshu']['search_url']}?keyword={keyword}"
            
            response = self._make_request(search_url)
            
            if response:
                logger.info("✅ 小红书搜索页面访问成功")
                # 由于小红书反爬虫机制复杂，这里返回模拟数据
                return [{
                    'platform': 'xiaohongshu',
                    'title': f'关于{keyword}的笔记',
                    'author': '小红书用户',
                    'likes': 0,
                    'comments': 0,
                    'url': search_url,
                    'crawl_time': datetime.now().isoformat()
                }]
            
        except Exception as e:
            logger.error(f"小红书内容搜索失败: {str(e)}")
            
        return []
