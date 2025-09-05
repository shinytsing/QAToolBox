#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化功能推荐系统数据
"""

from django.core.management.base import BaseCommand

from apps.tools.models import Feature


class Command(BaseCommand):
    help = "初始化功能推荐系统数据"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("开始初始化功能数据..."))

        # 创建功能数据
        features_data = [
            {
                "name": "Boss直聘自动投递",
                "description": "智能求职助手，自动筛选职位并投递简历，提高求职效率",
                "feature_type": "tool",
                "category": "work",
                "url_name": "job_search_machine",
                "icon_class": "fas fa-briefcase",
                "icon_color": "#2196F3",
                "recommendation_weight": 85,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "抖音数据分析器",
                "description": "深度分析抖音视频数据，洞察流量密码，优化内容策略",
                "feature_type": "tool",
                "category": "analysis",
                "url_name": "douyin_analyzer",
                "icon_class": "fas fa-chart-bar",
                "icon_color": "#FF5722",
                "recommendation_weight": 80,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "食物随机选择器",
                "description": "告别选择困难症，智能推荐美食，记录饮食偏好",
                "feature_type": "tool",
                "category": "life",
                "url_name": "food_randomizer",
                "icon_class": "fas fa-utensils",
                "icon_color": "#4CAF50",
                "recommendation_weight": 75,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "心动链接",
                "description": "匿名社交平台，遇见有趣的灵魂，开启美好对话",
                "feature_type": "tool",
                "category": "social",
                "url_name": "heart_link",
                "icon_class": "fas fa-heart",
                "icon_color": "#E91E63",
                "recommendation_weight": 78,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "冥想音乐治愈",
                "description": "专业冥想引导，舒缓身心，提升专注力和睡眠质量",
                "feature_type": "tool",
                "category": "health",
                "url_name": "meditation_guide",
                "icon_class": "fas fa-leaf",
                "icon_color": "#009688",
                "recommendation_weight": 82,
                "require_login": False,
                "require_membership": "",
            },
            {
                "name": "创意写作助手",
                "description": "AI驱动的写作灵感工具，激发创造力，提升文案质量",
                "feature_type": "tool",
                "category": "creative",
                "url_name": "creative_writer",
                "icon_class": "fas fa-pen-fancy",
                "icon_color": "#9C27B0",
                "recommendation_weight": 77,
                "require_login": True,
                "require_membership": "basic",
            },
            {
                "name": "生活日记",
                "description": "记录美好瞬间，追踪情绪变化，构建个人成长档案",
                "feature_type": "tool",
                "category": "life",
                "url_name": "life_diary",
                "icon_class": "fas fa-book",
                "icon_color": "#FF9800",
                "recommendation_weight": 70,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "健身训练中心",
                "description": "个性化健身计划，科学训练指导，打造完美体型",
                "feature_type": "tool",
                "category": "health",
                "url_name": "fitness_center",
                "icon_class": "fas fa-dumbbell",
                "icon_color": "#607D8B",
                "recommendation_weight": 84,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "旅游攻略生成器",
                "description": "智能规划旅行路线，发现小众景点，创建专属旅游攻略",
                "feature_type": "tool",
                "category": "life",
                "url_name": "travel_guide",
                "icon_class": "fas fa-map-marked-alt",
                "icon_color": "#3F51B5",
                "recommendation_weight": 76,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "PDF转换工具",
                "description": "高质量文档格式转换，支持多种格式互转，保持原始排版",
                "feature_type": "tool",
                "category": "work",
                "url_name": "pdf_converter",
                "icon_class": "fas fa-file-pdf",
                "icon_color": "#F44336",
                "recommendation_weight": 73,
                "require_login": False,
                "require_membership": "",
            },
            {
                "name": "测试用例生成器",
                "description": "自动生成软件测试用例，提升测试覆盖率和质量",
                "feature_type": "tool",
                "category": "work",
                "url_name": "test_case_generator",
                "icon_class": "fas fa-vial",
                "icon_color": "#795548",
                "recommendation_weight": 74,
                "require_login": True,
                "require_membership": "basic",
            },
            {
                "name": "小红书文案生成",
                "description": "一键生成爆款小红书文案，提升内容传播力和互动率",
                "feature_type": "tool",
                "category": "creative",
                "url_name": "redbook_generator",
                "icon_class": "fas fa-hashtag",
                "icon_color": "#E91E63",
                "recommendation_weight": 79,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "塔罗牌占卜",
                "description": "神秘塔罗牌在线占卜，探索内心世界，寻找人生方向",
                "feature_type": "tool",
                "category": "entertainment",
                "url_name": "tarot_reading",
                "icon_class": "fas fa-magic",
                "icon_color": "#673AB7",
                "recommendation_weight": 68,
                "require_login": False,
                "require_membership": "",
            },
            {
                "name": "人际关系档案",
                "description": "智能管理人际关系，记录重要时刻，维护社交网络",
                "feature_type": "tool",
                "category": "social",
                "url_name": "meetsomeone_dashboard",
                "icon_class": "fas fa-users",
                "icon_color": "#2196F3",
                "recommendation_weight": 81,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "三重觉醒系统",
                "description": "健身+编程+AI协作的混合训练系统，全方位提升个人能力",
                "feature_type": "mode",
                "category": "health",
                "url_name": "triple_awakening_dashboard",
                "icon_class": "fas fa-bolt",
                "icon_color": "#FF6B35",
                "recommendation_weight": 88,
                "require_login": True,
                "require_membership": "premium",
            },
            {
                "name": "欲望仪表盘",
                "description": "可视化欲望管理，追踪目标实现进度，激发内在动力",
                "feature_type": "mode",
                "category": "life",
                "url_name": "desire_dashboard",
                "icon_class": "fas fa-fire",
                "icon_color": "#FF5722",
                "recommendation_weight": 83,
                "require_login": True,
                "require_membership": "",
            },
            {
                "name": "VanityOS虚荣系统",
                "description": "游戏化人生管理系统，通过虚荣心驱动个人成长",
                "feature_type": "mode",
                "category": "entertainment",
                "url_name": "vanity_os_dashboard",
                "icon_class": "fas fa-crown",
                "icon_color": "#FFD700",
                "recommendation_weight": 79,
                "require_login": True,
                "require_membership": "vip",
            },
            {
                "name": "功能发现",
                "description": "探索QAToolBox的丰富功能，发现最适合您的工具",
                "feature_type": "page",
                "category": "other",
                "url_name": "feature_discovery_page",
                "icon_class": "fas fa-compass",
                "icon_color": "#607D8B",
                "recommendation_weight": 90,
                "require_login": True,
                "require_membership": "",
            },
        ]

        created_count = 0
        updated_count = 0

        for feature_data in features_data:
            feature, created = Feature.objects.get_or_create(name=feature_data["name"], defaults=feature_data)

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ 创建功能: {feature.name}"))
            else:
                # 更新现有功能的部分字段
                updated = False
                for field, value in feature_data.items():
                    if field != "name" and getattr(feature, field, None) != value:
                        setattr(feature, field, value)
                        updated = True

                if updated:
                    feature.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"⟳ 更新功能: {feature.name}"))

        # 更新功能的受欢迎程度分数（基于推荐权重）
        for feature in Feature.objects.all():
            feature.popularity_score = min(100, feature.recommendation_weight - 50 + (feature.total_usage_count // 100))
            feature.save(update_fields=["popularity_score"])

        self.stdout.write(
            self.style.SUCCESS(
                f"\n功能数据初始化完成！\n"
                f"- 新创建: {created_count} 个功能\n"
                f"- 更新: {updated_count} 个功能\n"
                f"- 总计: {Feature.objects.count()} 个功能"
            )
        )

        # 显示一些统计信息
        self.stdout.write("\n=== 功能统计 ===")
        for category_code, category_name in Feature.CATEGORY_CHOICES:
            count = Feature.objects.filter(category=category_code).count()
            self.stdout.write(f"{category_name}: {count} 个")

        active_count = Feature.objects.filter(is_active=True).count()
        self.stdout.write(f"\n启用功能: {active_count} 个")
        self.stdout.write(f"禁用功能: {Feature.objects.count() - active_count} 个")
