import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, Sum
from collections import defaultdict, Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

User = get_user_model()

class UserBehaviorAnalyzer:
    """用户行为分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger('user_behavior_analyzer')
        self.cache_timeout = 3600  # 缓存1小时
    
    def track_user_action(self, user, action, details=None, metadata=None):
        """跟踪用户行为"""
        try:
            action_data = {
                'user_id': user.id,
                'username': user.username,
                'action': action,
                'details': details or {},
                'metadata': metadata or {},
                'timestamp': timezone.now().isoformat(),
                'ip_address': getattr(metadata, 'ip_address', None),
                'user_agent': getattr(metadata, 'user_agent', None),
                'session_id': getattr(metadata, 'session_id', None),
            }
            
            # 记录到日志
            self.logger.info(
                f"User action tracked: {action}",
                extra=action_data
            )
            
            # 存储到缓存
            cache_key = f"user_action_{user.id}_{int(timezone.now().timestamp())}"
            cache.set(cache_key, action_data, self.cache_timeout)
            
            # 更新用户活跃度
            self._update_user_activity(user)
            
        except Exception as e:
            self.logger.error(f"Failed to track user action: {e}")
    
    def _update_user_activity(self, user):
        """更新用户活跃度"""
        try:
            activity_key = f"user_activity_{user.id}"
            current_activity = cache.get(activity_key, {
                'last_activity': None,
                'session_count': 0,
                'total_actions': 0,
                'active_days': set()
            })
            
            current_time = timezone.now()
            current_activity['last_activity'] = current_time.isoformat()
            current_activity['total_actions'] += 1
            current_activity['active_days'].add(current_time.date().isoformat())
            
            cache.set(activity_key, current_activity, self.cache_timeout)
            
        except Exception as e:
            self.logger.error(f"Failed to update user activity: {e}")
    
    def get_user_behavior_profile(self, user_id, days=30):
        """获取用户行为画像"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 从缓存获取
            cache_key = f"user_profile_{user_id}_{days}"
            cached_profile = cache.get(cache_key)
            if cached_profile:
                return cached_profile
            
            # 获取用户基本信息
            user = User.objects.get(id=user_id)
            
            # 获取行为数据
            behavior_data = self._get_user_behavior_data(user_id, start_date, end_date)
            
            # 分析行为模式
            profile = {
                'user_id': user_id,
                'username': user.username,
                'email': user.email,
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'activity_summary': self._analyze_activity_summary(behavior_data),
                'feature_usage': self._analyze_feature_usage(behavior_data),
                'usage_patterns': self._analyze_usage_patterns(behavior_data),
                'engagement_level': self._calculate_engagement_level(behavior_data),
                'user_segment': self._classify_user_segment(behavior_data),
                'recommendations': self._generate_recommendations(behavior_data),
                'generated_at': timezone.now().isoformat()
            }
            
            # 缓存结果
            cache.set(cache_key, profile, self.cache_timeout)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Failed to get user behavior profile: {e}")
            return {}
    
    def _get_user_behavior_data(self, user_id, start_date, end_date):
        """获取用户行为数据"""
        try:
            # 这里需要从实际的日志或数据库中获取用户行为数据
            # 示例实现
            behavior_data = {
                'total_actions': 0,
                'unique_days': 0,
                'feature_usage': {},
                'session_data': [],
                'time_patterns': {},
                'device_info': {},
                'location_data': {}
            }
            
            return behavior_data
            
        except Exception as e:
            self.logger.error(f"Failed to get user behavior data: {e}")
            return {}
    
    def _analyze_activity_summary(self, behavior_data):
        """分析活动摘要"""
        try:
            return {
                'total_actions': behavior_data.get('total_actions', 0),
                'active_days': behavior_data.get('unique_days', 0),
                'avg_actions_per_day': behavior_data.get('total_actions', 0) / max(behavior_data.get('unique_days', 1), 1),
                'last_activity': behavior_data.get('last_activity'),
                'activity_trend': 'increasing'  # 示例值
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze activity summary: {e}")
            return {}
    
    def _analyze_feature_usage(self, behavior_data):
        """分析功能使用情况"""
        try:
            feature_usage = behavior_data.get('feature_usage', {})
            
            # 计算使用频率
            total_usage = sum(feature_usage.values())
            usage_percentages = {
                feature: (count / total_usage * 100) if total_usage > 0 else 0
                for feature, count in feature_usage.items()
            }
            
            # 排序功能使用情况
            sorted_features = sorted(
                usage_percentages.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                'most_used_features': sorted_features[:5],
                'least_used_features': sorted_features[-5:],
                'feature_diversity': len(feature_usage),
                'usage_distribution': usage_percentages
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze feature usage: {e}")
            return {}
    
    def _analyze_usage_patterns(self, behavior_data):
        """分析使用模式"""
        try:
            time_patterns = behavior_data.get('time_patterns', {})
            
            # 分析时间模式
            patterns = {
                'peak_hours': self._find_peak_hours(time_patterns),
                'usage_days': self._analyze_usage_days(time_patterns),
                'session_length': self._analyze_session_length(behavior_data.get('session_data', [])),
                'frequency_pattern': self._analyze_frequency_pattern(time_patterns)
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze usage patterns: {e}")
            return {}
    
    def _find_peak_hours(self, time_patterns):
        """找出使用高峰时段"""
        try:
            hour_usage = time_patterns.get('hourly_usage', {})
            if not hour_usage:
                return []
            
            # 找出使用量最高的3个小时
            sorted_hours = sorted(hour_usage.items(), key=lambda x: x[1], reverse=True)
            return sorted_hours[:3]
            
        except Exception as e:
            self.logger.error(f"Failed to find peak hours: {e}")
            return []
    
    def _analyze_usage_days(self, time_patterns):
        """分析使用天数模式"""
        try:
            day_usage = time_patterns.get('daily_usage', {})
            if not day_usage:
                return {}
            
            # 分析工作日vs周末使用情况
            weekday_usage = sum(day_usage.get(f'weekday_{i}', 0) for i in range(5))
            weekend_usage = sum(day_usage.get(f'weekend_{i}', 0) for i in range(2))
            
            return {
                'weekday_usage': weekday_usage,
                'weekend_usage': weekend_usage,
                'preferred_day_type': 'weekday' if weekday_usage > weekend_usage else 'weekend',
                'usage_consistency': self._calculate_usage_consistency(day_usage)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze usage days: {e}")
            return {}
    
    def _analyze_session_length(self, session_data):
        """分析会话长度"""
        try:
            if not session_data:
                return {}
            
            session_lengths = [session.get('duration', 0) for session in session_data]
            
            return {
                'avg_session_length': np.mean(session_lengths) if session_lengths else 0,
                'max_session_length': max(session_lengths) if session_lengths else 0,
                'min_session_length': min(session_lengths) if session_lengths else 0,
                'total_sessions': len(session_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze session length: {e}")
            return {}
    
    def _analyze_frequency_pattern(self, time_patterns):
        """分析使用频率模式"""
        try:
            # 分析使用频率的规律性
            daily_usage = time_patterns.get('daily_usage', {})
            if not daily_usage:
                return 'unknown'
            
            usage_values = list(daily_usage.values())
            if len(usage_values) < 7:
                return 'insufficient_data'
            
            # 计算变异系数
            mean_usage = np.mean(usage_values)
            std_usage = np.std(usage_values)
            cv = std_usage / mean_usage if mean_usage > 0 else 0
            
            if cv < 0.3:
                return 'very_consistent'
            elif cv < 0.6:
                return 'consistent'
            elif cv < 1.0:
                return 'variable'
            else:
                return 'irregular'
                
        except Exception as e:
            self.logger.error(f"Failed to analyze frequency pattern: {e}")
            return 'unknown'
    
    def _calculate_usage_consistency(self, day_usage):
        """计算使用一致性"""
        try:
            if not day_usage:
                return 0
            
            usage_values = list(day_usage.values())
            if len(usage_values) < 2:
                return 0
            
            # 计算变异系数的倒数作为一致性指标
            mean_usage = np.mean(usage_values)
            std_usage = np.std(usage_values)
            cv = std_usage / mean_usage if mean_usage > 0 else 1
            
            consistency = max(0, 1 - cv)
            return round(consistency, 2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate usage consistency: {e}")
            return 0
    
    def _calculate_engagement_level(self, behavior_data):
        """计算参与度等级"""
        try:
            total_actions = behavior_data.get('total_actions', 0)
            active_days = behavior_data.get('unique_days', 0)
            feature_diversity = len(behavior_data.get('feature_usage', {}))
            
            # 计算参与度分数
            engagement_score = 0
            
            # 基于总行动数
            if total_actions > 1000:
                engagement_score += 40
            elif total_actions > 500:
                engagement_score += 30
            elif total_actions > 100:
                engagement_score += 20
            elif total_actions > 50:
                engagement_score += 10
            
            # 基于活跃天数
            if active_days > 20:
                engagement_score += 30
            elif active_days > 10:
                engagement_score += 20
            elif active_days > 5:
                engagement_score += 10
            
            # 基于功能多样性
            if feature_diversity > 10:
                engagement_score += 30
            elif feature_diversity > 5:
                engagement_score += 20
            elif feature_diversity > 2:
                engagement_score += 10
            
            # 确定参与度等级
            if engagement_score >= 80:
                level = 'high'
            elif engagement_score >= 60:
                level = 'medium'
            elif engagement_score >= 30:
                level = 'low'
            else:
                level = 'very_low'
            
            return {
                'level': level,
                'score': engagement_score,
                'factors': {
                    'total_actions': total_actions,
                    'active_days': active_days,
                    'feature_diversity': feature_diversity
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate engagement level: {e}")
            return {'level': 'unknown', 'score': 0}
    
    def _classify_user_segment(self, behavior_data):
        """用户分群"""
        try:
            # 基于行为特征进行用户分群
            total_actions = behavior_data.get('total_actions', 0)
            active_days = behavior_data.get('unique_days', 0)
            feature_diversity = len(behavior_data.get('feature_usage', {}))
            
            # 简单的规则分群
            if total_actions > 500 and active_days > 15 and feature_diversity > 5:
                segment = 'power_user'
            elif total_actions > 100 and active_days > 7:
                segment = 'regular_user'
            elif total_actions > 20:
                segment = 'casual_user'
            else:
                segment = 'new_user'
            
            return {
                'segment': segment,
                'characteristics': self._get_segment_characteristics(segment),
                'recommendations': self._get_segment_recommendations(segment)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to classify user segment: {e}")
            return {'segment': 'unknown'}
    
    def _get_segment_characteristics(self, segment):
        """获取分群特征"""
        characteristics = {
            'power_user': {
                'description': '重度用户，使用频率高，功能使用全面',
                'behavior_pattern': '高频使用，功能探索深入',
                'value_to_platform': '高价值用户，贡献大量数据'
            },
            'regular_user': {
                'description': '常规用户，使用频率中等，功能使用稳定',
                'behavior_pattern': '规律使用，偏好特定功能',
                'value_to_platform': '稳定用户，有增长潜力'
            },
            'casual_user': {
                'description': '轻度用户，使用频率较低，功能使用有限',
                'behavior_pattern': '偶尔使用，功能使用简单',
                'value_to_platform': '潜在用户，需要引导'
            },
            'new_user': {
                'description': '新用户，刚开始使用，功能探索阶段',
                'behavior_pattern': '学习使用，功能尝试',
                'value_to_platform': '新用户，需要培养'
            }
        }
        
        return characteristics.get(segment, {})
    
    def _get_segment_recommendations(self, segment):
        """获取分群建议"""
        recommendations = {
            'power_user': [
                '提供高级功能和个性化定制',
                '邀请参与产品反馈和测试',
                '提供专属客服支持',
                '推荐相关高级功能'
            ],
            'regular_user': [
                '推荐未使用的功能',
                '提供使用技巧和最佳实践',
                '发送个性化内容推荐',
                '邀请参与社区活动'
            ],
            'casual_user': [
                '发送功能使用教程',
                '提供简化操作流程',
                '发送使用提醒和激励',
                '推荐核心功能'
            ],
            'new_user': [
                '提供完整的新手引导',
                '发送欢迎邮件和功能介绍',
                '提供在线帮助和文档',
                '推荐基础功能使用'
            ]
        }
        
        return recommendations.get(segment, [])
    
    def _generate_recommendations(self, behavior_data):
        """生成个性化推荐"""
        try:
            recommendations = []
            
            # 基于功能使用情况推荐
            feature_usage = behavior_data.get('feature_usage', {})
            if not feature_usage:
                recommendations.append({
                    'type': 'feature_discovery',
                    'title': '探索新功能',
                    'description': '尝试使用不同的功能来发现更多价值',
                    'priority': 'high'
                })
            
            # 基于使用频率推荐
            total_actions = behavior_data.get('total_actions', 0)
            if total_actions < 50:
                recommendations.append({
                    'type': 'usage_encouragement',
                    'title': '增加使用频率',
                    'description': '定期使用应用可以获得更好的体验',
                    'priority': 'medium'
                })
            
            # 基于功能多样性推荐
            feature_diversity = len(feature_usage)
            if feature_diversity < 3:
                recommendations.append({
                    'type': 'feature_diversification',
                    'title': '尝试更多功能',
                    'description': '探索更多功能可以提升使用体验',
                    'priority': 'medium'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    def get_platform_analytics(self, days=30):
        """获取平台分析数据"""
        try:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # 从缓存获取
            cache_key = f"platform_analytics_{days}"
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # 获取平台级数据
            analytics = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'user_metrics': self._get_user_metrics(start_date, end_date),
                'feature_usage': self._get_platform_feature_usage(start_date, end_date),
                'user_segments': self._get_platform_user_segments(start_date, end_date),
                'retention_analysis': self._analyze_retention(start_date, end_date),
                'growth_metrics': self._analyze_growth_metrics(start_date, end_date),
                'generated_at': timezone.now().isoformat()
            }
            
            # 缓存结果
            cache.set(cache_key, analytics, self.cache_timeout)
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get platform analytics: {e}")
            return {}
    
    def _get_user_metrics(self, start_date, end_date):
        """获取用户指标"""
        try:
            # 总用户数
            total_users = User.objects.count()
            
            # 活跃用户数
            active_users = User.objects.filter(
                last_login__gte=start_date
            ).count()
            
            # 新用户数
            new_users = User.objects.filter(
                date_joined__gte=start_date
            ).count()
            
            # 用户增长率
            previous_period_start = start_date - timedelta(days=30)
            previous_period_users = User.objects.filter(
                date_joined__gte=previous_period_start,
                date_joined__lt=start_date
            ).count()
            
            growth_rate = ((new_users - previous_period_users) / max(previous_period_users, 1)) * 100
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'new_users': new_users,
                'growth_rate': round(growth_rate, 2),
                'activity_rate': round((active_users / max(total_users, 1)) * 100, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user metrics: {e}")
            return {}
    
    def _get_platform_feature_usage(self, start_date, end_date):
        """获取平台功能使用情况"""
        try:
            # 这里需要从实际的日志或数据库中获取功能使用数据
            # 示例实现
            feature_usage = {
                'fitness': 0,
                'life_tools': 0,
                'geek_tools': 0,
                'social': 0,
                'share': 0
            }
            
            return feature_usage
            
        except Exception as e:
            self.logger.error(f"Failed to get platform feature usage: {e}")
            return {}
    
    def _get_platform_user_segments(self, start_date, end_date):
        """获取平台用户分群"""
        try:
            # 这里需要分析所有用户的行为数据
            # 示例实现
            segments = {
                'power_user': 0,
                'regular_user': 0,
                'casual_user': 0,
                'new_user': 0
            }
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Failed to get platform user segments: {e}")
            return {}
    
    def _analyze_retention(self, start_date, end_date):
        """分析用户留存"""
        try:
            # 计算不同时间段的留存率
            retention_data = {
                'day_1': 0,
                'day_7': 0,
                'day_30': 0,
                'day_90': 0
            }
            
            return retention_data
            
        except Exception as e:
            self.logger.error(f"Failed to analyze retention: {e}")
            return {}
    
    def _analyze_growth_metrics(self, start_date, end_date):
        """分析增长指标"""
        try:
            # 计算各种增长指标
            growth_metrics = {
                'user_growth': 0,
                'feature_adoption': 0,
                'engagement_growth': 0,
                'revenue_growth': 0
            }
            
            return growth_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to analyze growth metrics: {e}")
            return {}

# 全局分析器实例
user_behavior_analyzer = UserBehaviorAnalyzer()
