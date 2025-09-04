import requests
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from ..models import DouyinVideoAnalysis, DouyinVideo
from .douyin_crawler import DouyinCrawler


class DouyinAnalyzer:
    """抖音视频分析服务"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://www.douyin.com/",
            }
        )
        # 初始化真实爬虫
        self.crawler = DouyinCrawler()

    def analyze_up主(self, up主_url: str, user_id: int) -> Dict:
        """分析抖音UP主"""
        try:
            # 使用真实爬虫获取用户信息
            user_info = self.crawler.extract_user_info_from_url(up主_url)

            # 创建分析记录
            analysis = DouyinVideoAnalysis.objects.create(
                user_id=user_id,
                up主_id=user_info["user_id"],
                up主_name=user_info["user_name"],
                up主_url=up主_url,
                analysis_status="processing",
            )

            # 使用真实爬虫爬取用户数据
            user_data = self.crawler.crawl_user_profile(up主_url)

            # 检查是否有错误
            if user_data.get("error"):
                # 如果是真实数据获取失败，尝试使用演示数据
                if not user_data.get("is_demo"):
                    print("尝试使用演示数据进行分析...")
                    demo_data = self.crawler.get_fallback_analysis_data(up主_url)
                    if demo_data and not demo_data.get("error"):
                        user_data = demo_data
                        analysis.analysis_status = "completed"
                        analysis.error_message = demo_data.get("demo_message", "使用演示数据")
                    else:
                        analysis.analysis_status = "failed"
                        analysis.error_message = user_data.get("error_message", "数据获取失败")
                        analysis.save()

                        return {
                            "success": False,
                            "error": user_data.get("error_message", "数据获取失败"),
                            "analysis_id": analysis.id,
                        }
                else:
                    analysis.analysis_status = "completed"
                    analysis.error_message = user_data.get("demo_message", "使用演示数据")

            # 分析用户内容特征
            content_analysis = self.crawler.analyze_user_content(user_data)

            # 更新分析结果
            analysis.video_count = user_data.get("video_count", 0)
            analysis.total_likes = user_data.get("total_likes", 0)
            analysis.total_comments = 0  # 需要从视频数据中计算
            analysis.total_shares = 0  # 需要从视频数据中计算
            analysis.follower_count = user_data.get("follower_count", 0)
            analysis.content_themes = content_analysis.get("content_themes", [])
            analysis.video_tags = content_analysis.get("video_tags", [])
            analysis.popular_videos = content_analysis.get("popular_videos", [])
            analysis.posting_frequency = content_analysis.get("posting_frequency", "未知")
            analysis.screenshots = self._generate_screenshots(user_data)
            analysis.analysis_summary = content_analysis.get("analysis_summary", "")
            analysis.analysis_status = "completed"
            analysis.completed_at = timezone.now()
            analysis.save()

            # 计算总评论数和分享数
            total_comments = 0
            total_shares = 0
            for video in user_data.get("videos", []):
                total_comments += video.get("comments", 0)
                total_shares += video.get("shares", 0)

            analysis.total_comments = total_comments
            analysis.total_shares = total_shares
            analysis.save()

            # 创建视频记录
            for video_data in user_data.get("videos", []):
                DouyinVideo.objects.create(
                    analysis=analysis,
                    video_id=video_data["video_id"],
                    video_url=video_data["video_url"],
                    title=video_data["title"],
                    description=video_data.get("description", ""),
                    likes=video_data["likes"],
                    comments=video_data["comments"],
                    shares=video_data["shares"],
                    views=video_data["views"],
                    tags=video_data.get("tags", []),
                    theme=video_data.get("theme", ""),
                    duration=video_data.get("duration", 0),
                    thumbnail_url=video_data.get("thumbnail_url", ""),
                    screenshot_urls=video_data.get("screenshot_urls", []),
                    published_at=video_data.get("published_at"),
                )

            return {"success": True, "analysis_id": analysis.id, "message": "分析完成"}

        except Exception as e:
            if "analysis" in locals():
                analysis.analysis_status = "failed"
                analysis.save()

            return {"success": False, "error": str(e)}

    def _generate_screenshots(self, user_data: Dict) -> List[Dict]:
        """生成视频截图数据"""
        screenshots = []
        videos = user_data.get("videos", [])

        for i, video in enumerate(videos[:3]):  # 只取前3个视频的截图
            screenshots.append(
                {
                    "title": f'{video.get("title", f"视频{i+1}")}截图',
                    "url": video.get("thumbnail_url", f"/static/img/douyin_screenshot_{i+1}.jpg"),
                    "description": f'展示了{video.get("title", f"视频{i+1}")}的内容特点',
                }
            )

        return screenshots

    def generate_product_preview(self, analysis_id: int) -> Dict:
        """生成产品功能预览"""
        try:
            analysis = DouyinVideoAnalysis.objects.get(id=analysis_id)

            # 构建DeepSeek提示词
            prompt = self._build_product_preview_prompt(analysis)

            # 调用DeepSeek API生成预览
            product_preview = self._call_deepseek_api(prompt)

            # 更新分析记录
            analysis.product_preview = product_preview
            analysis.save()

            return {"success": True, "product_preview": product_preview}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_product_preview_prompt(self, analysis: DouyinVideoAnalysis) -> str:
        """构建产品功能预览提示词"""
        prompt = f"""
        基于以下抖音UP主的数据分析，请生成一个创新的产品功能预览：

        UP主信息：
        - 名称：{analysis.up主_name}
        - 粉丝数：{analysis.follower_count:,}人
        - 视频总数：{analysis.video_count}个
        - 总点赞数：{analysis.total_likes:,}个
        - 总评论数：{analysis.total_comments:,}个
        - 总分享数：{analysis.total_shares:,}个

        内容分析：
        - 主要主题：{', '.join(analysis.content_themes)}
        - 热门标签：{', '.join(analysis.video_tags)}
        - 发布频率：{analysis.posting_frequency}

        请基于这些数据，设计一个创新的产品功能，要求：
        1. 功能要符合极客主题，具有科技感和创新性
        2. 要能够解决UP主或粉丝的实际需求
        3. 包含详细的功能描述、使用场景和技术特点
        4. 要有吸引人的产品名称和slogan
        5. 包含UI/UX设计建议
        6. 提供技术实现方案
        7. 分析市场前景和商业价值

        请用中文回答，格式要清晰易读。
        """
        return prompt

    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API，带重试机制和更长超时"""
        import os
        import requests
        import time

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "DeepSeek API密钥未配置，无法生成产品预览"

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 2000,
        }

        # 重试配置
        max_retries = 3
        retry_delays = [2, 5, 10]  # 递增重试延迟
        timeout_values = [60, 90, 120]  # 递增超时时间

        for attempt in range(max_retries):
            try:
                print(f"DeepSeek API调用尝试 {attempt + 1}/{max_retries}，超时设置: {timeout_values[attempt]}秒")

                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout_values[attempt],
                )

                if response.status_code == 200:
                    result = response.json()
                    print("DeepSeek API调用成功")
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"API调用失败: {response.status_code} - {response.text}"
                    print(error_msg)

                    # 如果是最后一次尝试，返回错误信息
                    if attempt == max_retries - 1:
                        return error_msg

                    # 否则等待后重试
                    time.sleep(retry_delays[attempt])
                    continue

            except requests.exceptions.Timeout:
                error_msg = f"API调用超时 (尝试 {attempt + 1}/{max_retries}，超时时间: {timeout_values[attempt]}秒)"
                print(error_msg)

                if attempt == max_retries - 1:
                    return f"API调用超时: 所有重试尝试都已超时，请稍后再试"

                # 等待后重试
                time.sleep(retry_delays[attempt])
                continue

            except requests.exceptions.ConnectionError:
                error_msg = f"网络连接错误 (尝试 {attempt + 1}/{max_retries})"
                print(error_msg)

                if attempt == max_retries - 1:
                    return f"网络连接错误: 无法连接到DeepSeek API服务器"

                # 等待后重试
                time.sleep(retry_delays[attempt])
                continue

            except Exception as e:
                error_msg = f"API调用出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}"
                print(error_msg)

                if attempt == max_retries - 1:
                    return f"API调用出错: {str(e)}"

                # 等待后重试
                time.sleep(retry_delays[attempt])
                continue

        return "API调用失败: 所有重试尝试都已失败"
