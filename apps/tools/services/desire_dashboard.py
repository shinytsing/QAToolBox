"""
欲望仪表盘服务
实现欲望管理、任务完成、AI图片生成等功能
"""

import random
from typing import Dict, List

from django.contrib.auth.models import User
from django.utils import timezone

from ..models import (
    DesireDashboard,
    DesireFulfillment,
    DesireItem,
)


class DesireDashboardService:
    """欲望仪表盘服务类"""

    def __init__(self):
        self.default_desires = [
            {
                "title": "想要玛莎拉蒂",
                "desire_type": "material",
                "description": "拥有一辆豪华跑车，体验速度与激情",
                "intensity": 3,
                "fulfillment_condition": "完成100行代码",
                "ai_prompt_template": "A luxurious Maserati sports car parked in a modern garage, with a satisfied developer sitting in the driver seat, celebrating their coding achievement. High quality, realistic, professional lighting.",
            },
            {
                "title": "想要被网红注目",
                "desire_type": "social",
                "description": "在社交媒体上获得关注和认可",
                "intensity": 2,
                "fulfillment_condition": "完成一次高强度训练",
                "ai_prompt_template": "A social media influencer with millions of followers giving a thumbs up to a fitness enthusiast who just completed an intense workout. Modern, vibrant, Instagram-style photography.",
            },
            {
                "title": "想要三天不写代码",
                "desire_type": "escape",
                "description": "暂时逃离代码世界，享受生活",
                "intensity": 5,
                "fulfillment_condition": "连续完成7天训练",
                "ai_prompt_template": "A peaceful beach scene with a laptop closed and turned off, while the developer enjoys a relaxing vacation. Sunset lighting, serene atmosphere, digital detox theme.",
            },
            {
                "title": "想要成为技术大牛",
                "desire_type": "achievement",
                "description": "在技术领域获得权威地位",
                "intensity": 4,
                "fulfillment_condition": "重构10个函数",
                "ai_prompt_template": "A respected tech leader giving a keynote speech at a major conference, with thousands of developers listening attentively. Professional, inspiring, leadership atmosphere.",
            },
            {
                "title": "想要被老板表扬",
                "desire_type": "recognition",
                "description": "获得上级的认可和赞赏",
                "intensity": 3,
                "fulfillment_condition": "完成一个完整项目",
                "ai_prompt_template": "A supportive boss giving a high-five to an employee who just delivered an excellent project. Office environment, celebration, recognition, professional success.",
            },
        ]

    def get_or_create_dashboard(self, user: User) -> DesireDashboard:
        """获取或创建欲望仪表盘"""
        dashboard, created = DesireDashboard.objects.get_or_create(user=user)

        if created:
            # 创建默认欲望项目
            self._create_default_desires(user)
            self._update_dashboard_stats(user)

        return dashboard

    def _create_default_desires(self, user: User):
        """创建默认欲望项目"""
        for desire_data in self.default_desires:
            DesireItem.objects.get_or_create(
                user=user,
                title=desire_data["title"],
                defaults={
                    "desire_type": desire_data["desire_type"],
                    "description": desire_data["description"],
                    "intensity": desire_data["intensity"],
                    "fulfillment_condition": desire_data["fulfillment_condition"],
                    "ai_generated_image": desire_data["ai_prompt_template"],
                },
            )

    def _update_dashboard_stats(self, user: User):
        """更新仪表盘统计"""
        dashboard = DesireDashboard.objects.get(user=user)
        desires = DesireItem.objects.filter(user=user)

        total_desires = desires.count()
        fulfilled_desires = desires.filter(is_fulfilled=True).count()

        # 计算欲望浓度
        if total_desires > 0:
            # 基于未满足的欲望强度和数量计算
            unfulfilled_desires = desires.filter(is_fulfilled=False)
            total_intensity = sum(d.intensity for d in unfulfilled_desires)
            max_possible_intensity = total_desires * 5

            if max_possible_intensity > 0:
                desire_level = min(100, int((total_intensity / max_possible_intensity) * 100))
            else:
                desire_level = 0
        else:
            desire_level = 50

        dashboard.total_desires = total_desires
        dashboard.fulfilled_desires = fulfilled_desires
        dashboard.current_desire_level = desire_level
        dashboard.save()

    def get_dashboard_data(self, user: User) -> Dict:
        """获取仪表盘数据"""
        dashboard = self.get_or_create_dashboard(user)
        desires = DesireItem.objects.filter(user=user).order_by("-intensity")

        return {
            "dashboard": {
                "current_desire_level": dashboard.current_desire_level,
                "total_desires": dashboard.total_desires,
                "fulfilled_desires": dashboard.fulfilled_desires,
                "last_updated": dashboard.last_updated.strftime("%Y-%m-%d %H:%M"),
            },
            "desires": [
                {
                    "id": d.id,
                    "title": d.title,
                    "type": d.get_desire_type_display(),
                    "intensity": d.intensity,
                    "intensity_stars": d.get_intensity_stars(),
                    "is_fulfilled": d.is_fulfilled,
                    "fulfillment_condition": d.fulfillment_condition,
                    "description": d.description,
                    "created_at": d.created_at.strftime("%Y-%m-%d"),
                }
                for d in desires
            ],
        }

    def add_desire(self, user: User, desire_data: Dict) -> DesireItem:
        """添加新欲望"""
        desire = DesireItem.objects.create(
            user=user,
            desire_type=desire_data.get("desire_type", "material"),
            title=desire_data.get("title", ""),
            description=desire_data.get("description", ""),
            intensity=desire_data.get("intensity", 3),
            fulfillment_condition=desire_data.get("fulfillment_condition", ""),
            ai_generated_image=desire_data.get("ai_prompt_template", ""),
        )

        self._update_dashboard_stats(user)
        return desire

    def check_desire_fulfillment(self, user: User, task_type: str, task_details: str) -> List[Dict]:
        """检查欲望是否满足"""
        unfulfilled_desires = DesireItem.objects.filter(user=user, is_fulfilled=False)
        fulfilled_desires = []

        for desire in unfulfilled_desires:
            if self._check_fulfillment_condition(desire, task_type, task_details):
                fulfillment = self._fulfill_desire(user, desire, task_type, task_details)
                fulfilled_desires.append({"desire": desire, "fulfillment": fulfillment})

        if fulfilled_desires:
            self._update_dashboard_stats(user)

        return fulfilled_desires

    def _check_fulfillment_condition(self, desire: DesireItem, task_type: str, task_details: str) -> bool:
        """检查满足条件"""
        condition = desire.fulfillment_condition.lower()

        if "代码" in condition and task_type == "coding":
            if "100行" in condition:
                # 检查是否写了100行代码
                return "100行" in task_details or "100 lines" in task_details
            elif "重构" in condition:
                # 检查是否重构了函数
                return "重构" in task_details or "refactor" in task_details
            elif "项目" in condition:
                # 检查是否完成了项目
                return "项目" in task_details or "project" in task_details

        elif "训练" in condition and task_type == "fitness":
            if "高强度" in condition:
                # 检查是否完成高强度训练
                return "高强度" in task_details or "intense" in task_details
            elif "连续" in condition and "7天" in condition:
                # 检查是否连续训练7天
                return "连续" in task_details and "7天" in task_details

        return False

    def _fulfill_desire(self, user: User, desire: DesireItem, task_type: str, task_details: str) -> DesireFulfillment:
        """满足欲望"""
        # 生成AI图片提示词
        ai_prompt = self._generate_ai_prompt(desire, task_type, task_details)

        # 创建兑现记录
        fulfillment = DesireFulfillment.objects.create(
            user=user,
            desire=desire,
            task_completed=f"{task_type}任务",
            task_details=task_details,
            ai_prompt=ai_prompt,
            satisfaction_level=random.randint(7, 10),
        )

        # 标记欲望为已满足
        desire.is_fulfilled = True
        desire.fulfilled_at = timezone.now()
        desire.save()

        return fulfillment

    def _generate_ai_prompt(self, desire: DesireItem, task_type: str, task_details: str) -> str:
        """生成AI图片提示词"""
        base_prompt = desire.ai_generated_image or f"A person achieving their desire: {desire.title}"

        # 根据任务类型和欲望类型定制提示词
        if desire.desire_type == "material":
            if "玛莎拉蒂" in desire.title:
                return f"A luxurious Maserati sports car with a satisfied developer celebrating their coding achievement. {task_details}. High quality, realistic, professional lighting."
            else:
                return f"Material success and achievement: {desire.title}. {task_details}. Professional, high-quality photography."

        elif desire.desire_type == "social":
            return f"Social recognition and fame: {desire.title}. {task_details}. Modern, vibrant, social media style."

        elif desire.desire_type == "escape":
            return f"Peaceful escape and relaxation: {desire.title}. {task_details}. Serene, calming atmosphere."

        elif desire.desire_type == "achievement":
            return f"Professional achievement and success: {desire.title}. {task_details}. Inspiring, motivational imagery."

        elif desire.desire_type == "recognition":
            return (
                f"Recognition and praise: {desire.title}. {task_details}. Celebration, appreciation, professional environment."
            )

        return base_prompt

    def get_fulfillment_history(self, user: User) -> List[Dict]:
        """获取兑现历史"""
        fulfillments = DesireFulfillment.objects.filter(user=user).order_by("-created_at")[:10]

        return [
            {
                "id": f.id,
                "desire_title": f.desire.title,
                "task_completed": f.task_completed,
                "task_details": f.task_details,
                "ai_prompt": f.ai_prompt,
                "satisfaction_level": f.satisfaction_level,
                "created_at": f.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for f in fulfillments
        ]

    def generate_ai_image(self, fulfillment_id: int) -> str:
        """生成AI图片（模拟）"""
        # 这里应该调用真实的AI图片生成API
        # 为了演示，我们返回一个模拟的图片URL
        fulfillment = DesireFulfillment.objects.get(id=fulfillment_id)

        # 模拟AI图片生成
        image_url = f"https://via.placeholder.com/800x600/ff6b35/ffffff?text=AI生成图片: {fulfillment.desire.title}"

        # 更新兑现记录
        fulfillment.fulfillment_image_url = image_url
        fulfillment.ai_generated_image = f"AI生成的{fulfillment.desire.title}兑现图片"
        fulfillment.save()

        return image_url

    def get_desire_progress(self, user: User) -> Dict:
        """获取欲望进度"""
        desires = DesireItem.objects.filter(user=user)
        total = desires.count()
        fulfilled = desires.filter(is_fulfilled=True).count()

        return {
            "total": total,
            "fulfilled": fulfilled,
            "progress_percentage": int((fulfilled / total * 100) if total > 0 else 0),
            "remaining": total - fulfilled,
        }


class DesireVisualizationService:
    """欲望可视化服务"""

    @staticmethod
    def generate_desire_bar(level: int) -> str:
        """生成欲望浓度条"""
        filled_blocks = int(level / 10)
        empty_blocks = 10 - filled_blocks
        return "█" * filled_blocks + "░" * empty_blocks

    @staticmethod
    def get_desire_color(level: int) -> str:
        """获取欲望颜色"""
        if level >= 80:
            return "#ff4444"  # 红色 - 高欲望
        elif level >= 60:
            return "#ff6b35"  # 橙色 - 中高欲望
        elif level >= 40:
            return "#ffd700"  # 金色 - 中等欲望
        else:
            return "#00ff00"  # 绿色 - 低欲望

    @staticmethod
    def format_desire_display(desires: List[Dict]) -> str:
        """格式化欲望显示"""
        display = "[当前欲望浓度] "

        # 这里需要从dashboard数据中获取level
        level = 73  # 示例值
        display += f"{DesireVisualizationService.generate_desire_bar(level)} {level}%\n"

        for desire in desires[:3]:  # 只显示前3个
            stars = desire["intensity_stars"]
            display += f"▸ {desire['title']}: {stars}\n"

        return display
