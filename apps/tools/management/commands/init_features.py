#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
初始化功能数据的管理命令
为系统中现有的功能创建Feature记录
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models import Feature


class Command(BaseCommand):
    help = "初始化系统功能数据"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="重置所有功能数据（删除现有数据）",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write("正在重置功能数据...")
            Feature.objects.all().delete()

        # 定义基础功能数据
        features_data = [
            # 工作效率类
            {
                "name": "测试用例生成器",
                "description": "智能生成软件测试用例，提升测试效率",
                "feature_type": "tool",
                "category": "work",
                "url_name": "test_case_generator",
                "icon_class": "fas fa-bug",
                "icon_color": "#e74c3c",
                "recommendation_weight": 75,
            },
            {
                "name": "小红书文案生成器",
                "description": "AI驱动的小红书内容创作工具",
                "feature_type": "tool",
                "category": "creative",
                "url_name": "redbook_generator",
                "icon_class": "fas fa-edit",
                "icon_color": "#ff6b6b",
                "recommendation_weight": 80,
            },
            {
                "name": "PDF转换器",
                "description": "多格式文档转PDF，支持批量处理",
                "feature_type": "tool",
                "category": "work",
                "url_name": "pdf_converter",
                "icon_class": "fas fa-file-pdf",
                "icon_color": "#e74c3c",
                "recommendation_weight": 70,
            },
            {
                "name": "运势分析器",
                "description": "基于数据分析的个人运势预测",
                "feature_type": "tool",
                "category": "entertainment",
                "url_name": "fortune_analyzer",
                "icon_class": "fas fa-crystal-ball",
                "icon_color": "#9b59b6",
                "recommendation_weight": 60,
            },
            {
                "name": "网页爬虫",
                "description": "智能网页数据抓取工具",
                "feature_type": "tool",
                "category": "analysis",
                "url_name": "web_crawler",
                "icon_class": "fas fa-spider",
                "icon_color": "#34495e",
                "recommendation_weight": 65,
            },
            {
                "name": "自我分析",
                "description": "深度自我认知和心理分析工具",
                "feature_type": "tool",
                "category": "health",
                "url_name": "self_analysis",
                "icon_class": "fas fa-brain",
                "icon_color": "#3498db",
                "recommendation_weight": 70,
            },
            {
                "name": "故事板",
                "description": "创意故事构思和情节设计工具",
                "feature_type": "tool",
                "category": "creative",
                "url_name": "storyboard",
                "icon_class": "fas fa-film",
                "icon_color": "#f39c12",
                "recommendation_weight": 55,
            },
            {
                "name": "健身中心",
                "description": "个性化健身计划和训练指导",
                "feature_type": "tool",
                "category": "health",
                "url_name": "fitness",
                "icon_class": "fas fa-dumbbell",
                "icon_color": "#27ae60",
                "recommendation_weight": 75,
            },
            {
                "name": "生活日记",
                "description": "记录生活点滴，追踪心情变化",
                "feature_type": "tool",
                "category": "life",
                "url_name": "life_diary",
                "icon_class": "fas fa-book",
                "icon_color": "#16a085",
                "recommendation_weight": 80,
            },
            {
                "name": "Emo日记",
                "description": "情感表达和心理疏导平台",
                "feature_type": "tool",
                "category": "entertainment",
                "url_name": "emo_diary",
                "icon_class": "fas fa-heart-broken",
                "icon_color": "#8e44ad",
                "recommendation_weight": 65,
            },
            {
                "name": "创意写作",
                "description": "AI辅助的创意写作和灵感激发",
                "feature_type": "tool",
                "category": "creative",
                "url_name": "creative_writer",
                "icon_class": "fas fa-feather-alt",
                "icon_color": "#e67e22",
                "recommendation_weight": 70,
            },
            {
                "name": "冥想指南",
                "description": "正念冥想和放松训练指导",
                "feature_type": "tool",
                "category": "health",
                "url_name": "meditation_guide",
                "icon_class": "fas fa-om",
                "icon_color": "#2ecc71",
                "recommendation_weight": 60,
            },
            {
                "name": "音乐疗愈",
                "description": "个性化音乐治疗和情绪调节",
                "feature_type": "tool",
                "category": "entertainment",
                "url_name": "music_healing",
                "icon_class": "fas fa-music",
                "icon_color": "#3498db",
                "recommendation_weight": 65,
            },
            {
                "name": "抖音分析器",
                "description": "社交媒体内容分析和数据洞察",
                "feature_type": "tool",
                "category": "analysis",
                "url_name": "douyin_analyzer",
                "icon_class": "fas fa-chart-line",
                "icon_color": "#e74c3c",
                "recommendation_weight": 70,
            },
            {
                "name": "三重觉醒",
                "description": "综合自我提升和成长计划",
                "feature_type": "tool",
                "category": "learning",
                "url_name": "triple_awakening_dashboard",
                "icon_class": "fas fa-rocket",
                "icon_color": "#9b59b6",
                "recommendation_weight": 65,
            },
            {
                "name": "欲望仪表盘",
                "description": "目标设定和进度追踪系统",
                "feature_type": "tool",
                "category": "life",
                "url_name": "desire_dashboard",
                "icon_class": "fas fa-bullseye",
                "icon_color": "#e67e22",
                "recommendation_weight": 70,
            },
            {
                "name": "心动链接",
                "description": "社交匹配和互动平台",
                "feature_type": "tool",
                "category": "social",
                "url_name": "heart_link",
                "icon_class": "fas fa-heart",
                "icon_color": "#e91e63",
                "recommendation_weight": 60,
            },
            {
                "name": "食物随机选择器",
                "description": "解决选择困难，随机推荐美食",
                "feature_type": "tool",
                "category": "life",
                "url_name": "food_randomizer",
                "icon_class": "fas fa-utensils",
                "icon_color": "#ff6347",
                "recommendation_weight": 75,
            },
            {
                "name": "塔罗占卜",
                "description": "神秘的塔罗牌占卜和解读",
                "feature_type": "tool",
                "category": "entertainment",
                "url_name": "tarot_reading",
                "icon_class": "fas fa-star",
                "icon_color": "#ffd700",
                "recommendation_weight": 55,
            },
            {
                "name": "人际档案系统",
                "description": "管理和追踪人际关系网络",
                "feature_type": "tool",
                "category": "social",
                "url_name": "meetsomeone_dashboard",
                "icon_class": "fas fa-users",
                "icon_color": "#3498db",
                "recommendation_weight": 65,
            },
            # 模式功能
            {
                "name": "极客模式",
                "description": "专注技术，追求卓越的工作环境",
                "feature_type": "mode",
                "category": "work",
                "url_name": "work_mode",
                "icon_class": "fas fa-code",
                "icon_color": "#2c3e50",
                "recommendation_weight": 80,
            },
            {
                "name": "生活模式",
                "description": "享受生活的美好时光",
                "feature_type": "mode",
                "category": "life",
                "url_name": "life_mode",
                "icon_class": "fas fa-home",
                "icon_color": "#27ae60",
                "recommendation_weight": 85,
            },
            {
                "name": "狂暴模式",
                "description": "突破极限，挑战自我的训练环境",
                "feature_type": "mode",
                "category": "health",
                "url_name": "training_mode",
                "icon_class": "fas fa-fire",
                "icon_color": "#e74c3c",
                "recommendation_weight": 70,
            },
            {
                "name": "Emo模式",
                "description": "感受内心的情感波动",
                "feature_type": "mode",
                "category": "entertainment",
                "url_name": "emo_mode",
                "icon_class": "fas fa-cloud-rain",
                "icon_color": "#8e44ad",
                "recommendation_weight": 60,
            },
            {
                "name": "赛博朋克模式",
                "description": "未来科技感的沉浸式体验",
                "feature_type": "mode",
                "category": "entertainment",
                "url_name": "cyberpunk_mode",
                "icon_class": "fas fa-robot",
                "icon_color": "#00ffff",
                "recommendation_weight": 50,
            },
        ]

        created_count = 0
        updated_count = 0

        for feature_data in features_data:
            feature, created = Feature.objects.update_or_create(url_name=feature_data["url_name"], defaults=feature_data)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ 创建功能: {feature.name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"○ 更新功能: {feature.name}"))

        # 输出统计信息
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"功能初始化完成！"))
        self.stdout.write(f"新创建: {created_count} 个功能")
        self.stdout.write(f"更新: {updated_count} 个功能")
        self.stdout.write(f"总计: {Feature.objects.count()} 个功能")

        # 提示管理员可以在后台管理功能
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.HTTP_INFO("您可以在Django管理后台进一步配置这些功能："))
        self.stdout.write("1. 调整推荐权重")
        self.stdout.write("2. 设置功能可见性")
        self.stdout.write("3. 配置会员要求")
        self.stdout.write("4. 管理用户权限")
