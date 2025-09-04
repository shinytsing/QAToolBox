#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
功能推荐引擎
提供智能推荐算法和推荐业务逻辑
"""

import random
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, F
from django.core.cache import cache

from ..models import Feature, FeatureRecommendation, UserFeaturePermission, UserFirstVisit
from apps.users.models import UserModePreference


class FeatureRecommendationEngine:
    """功能推荐引擎"""

    def __init__(self):
        self.cache_timeout = 300  # 5分钟缓存
        self.default_limit = 6
        self.min_recommendation_interval = 24  # 24小时内不重复推荐同一功能

    def get_recommendations_for_user(self, user, limit=None, context=None):
        """
        为用户获取个性化推荐

        Args:
            user: 用户对象
            limit: 推荐数量限制
            context: 上下文信息（IP、用户代理等）

        Returns:
            list: 推荐结果列表
        """
        if limit is None:
            limit = self.default_limit

        if context is None:
            context = {}

        # 获取用户可用功能
        available_features = self._get_available_features(user)
        if not available_features:
            return []

        # 排除最近推荐过的功能
        available_features = self._filter_recent_recommendations(user, available_features)
        if not available_features:
            return []

        # 应用多种推荐算法
        recommendations = []

        # 1. 基于用户偏好的推荐
        personalized_recs = self._get_personalized_recommendations(user, available_features, limit // 2)
        recommendations.extend(personalized_recs)

        # 2. 基于热门度的推荐
        remaining_limit = limit - len(recommendations)
        if remaining_limit > 0:
            # 排除已推荐的功能
            remaining_features = [f for f in available_features if f not in [r["feature"] for r in recommendations]]
            popular_recs = self._get_popular_recommendations(remaining_features, remaining_limit // 2)
            recommendations.extend(popular_recs)

        # 3. 随机推荐（保证多样性）
        remaining_limit = limit - len(recommendations)
        if remaining_limit > 0:
            remaining_features = [f for f in available_features if f not in [r["feature"] for r in recommendations]]
            random_recs = self._get_random_recommendations(remaining_features, remaining_limit)
            recommendations.extend(random_recs)

        # 记录推荐会话
        session_id = str(uuid.uuid4())
        for rec in recommendations:
            rec["session_id"] = session_id
            rec["context"] = context

        # 限制返回数量
        return recommendations[:limit]

    def _get_available_features(self, user):
        """获取用户可用的功能列表"""
        cache_key = f"available_features_v2_{user.id}"
        cached_features = cache.get(cache_key)

        if cached_features is not None:
            return cached_features

        # 基础查询：激活且公开的功能
        features = Feature.objects.filter(is_active=True, is_public=True)

        # 检查用户特定权限
        user_permissions = UserFeaturePermission.objects.filter(user=user, is_visible=True, is_allowed=True).values_list(
            "feature_id", flat=True
        )

        if user_permissions.exists():
            # 使用用户特定权限
            features = features.filter(id__in=user_permissions)
        else:
            # 使用默认权限逻辑
            available_feature_ids = []
            for feature in features:
                if feature.can_recommend_to_user(user):
                    available_feature_ids.append(feature.id)
            features = features.filter(id__in=available_feature_ids)

        features_list = list(features)
        cache.set(cache_key, features_list, self.cache_timeout)

        return features_list

    def _filter_recent_recommendations(self, user, features):
        """过滤最近推荐过的功能"""
        since = timezone.now() - timedelta(hours=self.min_recommendation_interval)
        recent_feature_ids = FeatureRecommendation.objects.filter(
            user=user, created_at__gte=since, action="shown"
        ).values_list("feature_id", flat=True)

        return [f for f in features if f.id not in recent_feature_ids]

    def _get_personalized_recommendations(self, user, features, limit):
        """基于用户偏好的个性化推荐"""
        if not features or limit <= 0:
            return []

        # 获取用户模式偏好
        user_mode = self._get_user_preferred_mode(user)

        # 模式与功能类别的映射
        mode_category_mapping = {
            "work": ["work", "analysis", "creative"],
            "life": ["life", "entertainment", "health", "social"],
            "training": ["health", "learning", "work"],
            "emo": ["entertainment", "creative", "social"],
        }

        preferred_categories = mode_category_mapping.get(user_mode, ["work", "life"])

        # 为每个功能计算个性化得分
        scored_features = []
        for feature in features:
            # 排除Boss直聘自动投递功能（被注释的功能）
            if feature.name == "Boss直聘自动投递":
                continue

            score = self._calculate_personalized_score(user, feature, user_mode, preferred_categories)
            if score > 0:
                scored_features.append((feature, score))

        # 排序并选择
        scored_features.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for feature, score in scored_features[:limit]:
            # 设置默认的推荐理由
            default_reason = self._get_default_recommendation_reason(feature, user_mode)

            recommendations.append(
                {
                    "feature": feature,
                    "algorithm": "personalized",
                    "score": score,
                    "reason": default_reason,
                    "metadata": {"user_mode": user_mode, "category_match": feature.category in preferred_categories},
                }
            )

        return recommendations

    def _calculate_personalized_score(self, user, feature, user_mode, preferred_categories):
        """计算个性化推荐得分"""
        score = feature.recommendation_weight  # 基础权重

        # 类别匹配加分
        if feature.category in preferred_categories:
            score += 30

        # 用户自定义权重
        try:
            permission = UserFeaturePermission.objects.get(user=user, feature=feature)
            if permission.custom_weight:
                score += permission.custom_weight * 0.5
        except UserFeaturePermission.DoesNotExist:
            pass

        # 新功能加分
        if feature.created_at > timezone.now() - timedelta(days=30):
            score += 15

        # 受欢迎程度加分
        score += feature.popularity_score * 0.3

        # 用户历史行为分析
        user_history = FeatureRecommendation.objects.filter(
            user=user, feature__category=feature.category, action="clicked"
        ).count()

        if user_history > 0:
            score += min(20, user_history * 5)  # 历史点击同类功能加分

        return max(0, score)

    def _get_popular_recommendations(self, features, limit):
        """基于热门度的推荐"""
        if not features or limit <= 0:
            return []

        # 过滤掉Boss直聘自动投递功能
        filtered_features = [f for f in features if f.name != "Boss直聘自动投递"]

        # 按受欢迎程度和使用量排序
        features_sorted = sorted(
            filtered_features, key=lambda f: (f.popularity_score, f.total_usage_count, f.recommendation_weight), reverse=True
        )

        recommendations = []
        for feature in features_sorted[:limit]:
            # 设置默认的推荐理由
            default_reason = self._get_default_recommendation_reason(feature, "popular")

            recommendations.append(
                {
                    "feature": feature,
                    "algorithm": "popular",
                    "score": feature.popularity_score,
                    "reason": default_reason,
                    "metadata": {"popularity_score": feature.popularity_score, "usage_count": feature.total_usage_count},
                }
            )

        return recommendations

    def _get_random_recommendations(self, features, limit):
        """随机推荐（保证多样性）"""
        if not features or limit <= 0:
            return []

        # 过滤掉Boss直聘自动投递功能
        filtered_features = [f for f in features if f.name != "Boss直聘自动投递"]

        if not filtered_features:
            return []

        # 随机选择功能
        selected_features = random.sample(filtered_features, min(limit, len(filtered_features)))

        recommendations = []
        for feature in selected_features:
            # 设置默认的推荐理由
            default_reason = self._get_default_recommendation_reason(feature, "random")

            recommendations.append(
                {
                    "feature": feature,
                    "algorithm": "random",
                    "score": feature.recommendation_weight,
                    "reason": default_reason,
                    "metadata": {"random_selection": True},
                }
            )

        return recommendations

    def _get_user_preferred_mode(self, user):
        """获取用户偏好模式"""
        try:
            return UserModePreference.get_user_preferred_mode(user)
        except:
            return "work"  # 默认模式

    def record_user_action(self, user, feature, action, session_id=None, context=None):
        """记录用户行为"""
        if context is None:
            context = {}

        if session_id is None:
            session_id = str(uuid.uuid4())

        # 创建推荐记录
        recommendation = FeatureRecommendation.objects.create(
            user=user,
            feature=feature,
            session_id=session_id,
            action=action,
            ip_address=context.get("ip_address"),
            user_agent=context.get("user_agent", ""),
            action_time=timezone.now() if action != "shown" else None,
        )

        # 更新功能统计
        if action == "clicked":
            feature.increment_usage()

            # 更新用户首次访问记录
            try:
                first_visit = UserFirstVisit.objects.get(user=user)
                first_visit.total_feature_usage += 1
                first_visit.save(update_fields=["total_feature_usage"])
            except UserFirstVisit.DoesNotExist:
                UserFirstVisit.objects.create(user=user, total_feature_usage=1)

        return recommendation

    def should_show_recommendation_popup(self, user):
        """判断是否应该显示推荐弹窗"""
        try:
            first_visit = UserFirstVisit.objects.get(user=user)
            return first_visit.should_show_recommendation()
        except UserFirstVisit.DoesNotExist:
            # 新用户，应该显示推荐
            return True

    def mark_recommendation_shown(self, user):
        """标记推荐已显示"""
        first_visit, created = UserFirstVisit.objects.get_or_create(
            user=user,
            defaults={
                "has_seen_recommendation": True,
                "recommendation_shown_count": 1,
                "last_recommendation_time": timezone.now(),
            },
        )

        if not created:
            first_visit.mark_recommendation_shown()

    def get_recommendation_stats(self, user=None, days=30):
        """获取推荐统计信息"""
        since = timezone.now() - timedelta(days=days)

        base_query = FeatureRecommendation.objects.filter(created_at__gte=since)
        if user:
            base_query = base_query.filter(user=user)

        stats = {
            "period_days": days,
            "total_recommendations": base_query.count(),
            "shown_recommendations": base_query.filter(action="shown").count(),
            "clicked_recommendations": base_query.filter(action="clicked").count(),
            "dismissed_recommendations": base_query.filter(action="dismissed").count(),
            "not_interested_recommendations": base_query.filter(action="not_interested").count(),
        }

        # 计算点击率
        if stats["shown_recommendations"] > 0:
            stats["click_rate"] = (stats["clicked_recommendations"] / stats["shown_recommendations"]) * 100
        else:
            stats["click_rate"] = 0

        # 热门功能统计
        popular_features = Feature.objects.filter(
            featurerecommendation__created_at__gte=since, featurerecommendation__action="clicked"
        )

        if user:
            popular_features = popular_features.filter(featurerecommendation__user=user)

        popular_features = popular_features.annotate(click_count=Count("featurerecommendation")).order_by("-click_count")[:5]

        stats["popular_features"] = [
            {"id": f.id, "name": f.name, "category": f.get_category_display(), "click_count": f.click_count}
            for f in popular_features
        ]

        # 算法效果统计
        algorithm_stats = (
            base_query.filter(action="clicked")
            .values("recommendation_algorithm")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        stats["algorithm_performance"] = list(algorithm_stats)

        return stats

    def _get_default_recommendation_reason(self, feature, algorithm_type="smart"):
        """获取默认的推荐理由"""
        # 基础推荐理由
        base_reasons = {
            "personalized": f"根据您的使用偏好为您推荐",
            "popular": f"热门功能，已有{feature.total_usage_count}人使用",
            "random": "为您随机推荐一个有趣的功能",
            "smart": f"智能推荐，这个功能很适合您",
        }

        base_reason = base_reasons.get(algorithm_type, "为您推荐一个实用功能")

        # 根据功能类别添加具体描述
        category_descriptions = {
            "work": "，提升工作效率",
            "life": "，丰富生活体验",
            "health": "，关注健康管理",
            "social": "，拓展社交圈子",
            "creative": "，激发创作灵感",
            "analysis": "，深度数据分析",
            "entertainment": "，享受娱乐时光",
            "learning": "，促进学习成长",
        }

        category_desc = category_descriptions.get(feature.category, "")

        # 根据功能特点添加特殊描述
        feature_specific_reasons = {
            "抖音数据分析器": "，洞察流量密码，优化内容策略",
            "食物随机选择器": "，告别选择困难症，智能推荐美食",
            "心动链接": "，遇见有趣的灵魂，开启美好对话",
            "冥想音乐治愈": "，舒缓身心，提升专注力",
            "创意写作助手": "，激发创造力，提升文案质量",
            "生活日记": "，记录美好瞬间，追踪情绪变化",
            "健身训练中心": "，个性化健身计划，科学训练指导",
        }

        specific_reason = feature_specific_reasons.get(feature.name, "")

        # 组合最终推荐理由
        final_reason = base_reason + category_desc + specific_reason

        return final_reason


# 创建全局推荐引擎实例
recommendation_engine = FeatureRecommendationEngine()
