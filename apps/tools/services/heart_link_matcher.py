#!/usr/bin/env python3
"""
心动链接智能匹配服务
提供更智能的匹配算法，考虑用户在线时间、匹配历史等因素
"""

from django.db import transaction
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
import random
from apps.tools.models import HeartLinkRequest, ChatRoom, UserOnlineStatus
from apps.users.models import UserActivityLog


class HeartLinkMatcher:
    """心动链接智能匹配器"""
    
    def __init__(self):
        self.max_wait_time = 10  # 最大等待时间（分钟）
        self.min_online_time = 5  # 最小在线时间（分钟）
    
    def get_user_score(self, user):
        """计算用户匹配分数"""
        score = 0
        
        # 基础分数
        score += 100
        
        # 在线时间加分
        online_status = UserOnlineStatus.objects.filter(user=user).first()
        if online_status and online_status.last_seen:
            time_diff = timezone.now() - online_status.last_seen
            if time_diff.total_seconds() < 300:  # 5分钟内在线
                score += 50
            elif time_diff.total_seconds() < 600:  # 10分钟内在线
                score += 25
        
        # 活跃度加分
        recent_activity = UserActivityLog.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        score += min(recent_activity * 5, 50)  # 最多加50分
        
        # 匹配成功率加分
        successful_matches = HeartLinkRequest.objects.filter(
            requester=user,
            status='matched'
        ).count()
        score += min(successful_matches * 10, 30)  # 最多加30分
        
        # 随机因子（避免总是匹配同一类用户）
        score += random.randint(-20, 20)
        
        return score
    
    def find_best_match(self, current_user, current_request):
        """找到最佳匹配对象"""
        # 使用更简单的匹配逻辑，避免复杂的锁操作
        # 首先尝试找到一个可用的匹配对象
        available_request = HeartLinkRequest.objects.filter(
            status='pending',
            requester__is_staff=False,
            requester__is_superuser=False,
            requester__is_active=True,
        ).exclude(
            Q(requester=current_user)
        ).first()
        
        if not available_request:
            return None
        
        # 使用乐观锁：尝试更新状态
        try:
            # 尝试将对方请求标记为匹配中，避免被其他线程抢走
            updated = HeartLinkRequest.objects.filter(
                id=available_request.id,
                status='pending'
            ).update(status='matching')
            
            if updated == 0:
                # 如果更新失败，说明已经被其他线程抢走了
                return None
            
            # 重新获取更新后的对象
            available_request.refresh_from_db()
            return available_request
            
        except Exception as e:
            print(f"匹配过程中出错: {str(e)}")
            return None
    
    def create_match(self, user1, user2):
        """创建匹配"""
        import uuid
        
        # 创建聊天室
        room_id = str(uuid.uuid4())
        chat_room = ChatRoom.objects.create(
            room_id=room_id,
            user1=user1,
            user2=user2,
            status='active'
        )
        
        return chat_room
    
    def match_users(self, current_user, current_request):
        """执行用户匹配"""
        try:
            # 使用更短的超时时间避免长时间锁定
            with transaction.atomic():
                # 找到最佳匹配
                best_match_request = self.find_best_match(current_user, current_request)
                
                if not best_match_request:
                    return None, None
                
                # 双重检查：确保对方请求状态为matching
                best_match_request.refresh_from_db()
                if best_match_request.status != 'matching':
                    return None, None
                
                # 创建匹配
                chat_room = self.create_match(current_user, best_match_request.requester)
                
                # 更新两个请求的状态
                current_request.status = 'matched'
                current_request.matched_with = best_match_request.requester
                current_request.matched_at = timezone.now()
                current_request.chat_room = chat_room
                current_request.save()
                
                best_match_request.status = 'matched'
                best_match_request.matched_with = current_user
                best_match_request.matched_at = timezone.now()
                best_match_request.chat_room = chat_room
                best_match_request.save()
                
                return chat_room, best_match_request.requester
                
        except Exception as e:
            # 如果匹配失败，记录错误但不立即设为过期
            print(f"匹配失败: {str(e)}")
            # 只有在特定错误情况下才设为过期
            if "database is locked" in str(e).lower():
                # 数据库锁定错误，保持pending状态，让用户重试
                return None, None
            else:
                # 其他错误，设为过期
                current_request.status = 'expired'
                current_request.save()
                return None, None
    
    def cleanup_expired_requests(self):
        """清理过期的请求"""
        expired_time = timezone.now() - timedelta(minutes=self.max_wait_time)
        expired_requests = HeartLinkRequest.objects.filter(
            status='pending',
            created_at__lt=expired_time
        )
        
        for request in expired_requests:
            request.status = 'expired'
            request.save()
    
    def get_matching_stats(self):
        """获取匹配统计信息"""
        total_requests = HeartLinkRequest.objects.count()
        matched_requests = HeartLinkRequest.objects.filter(status='matched').count()
        pending_requests = HeartLinkRequest.objects.filter(status='pending').count()
        expired_requests = HeartLinkRequest.objects.filter(status='expired').count()
        
        return {
            'total': total_requests,
            'matched': matched_requests,
            'pending': pending_requests,
            'expired': expired_requests,
            'match_rate': (matched_requests / total_requests * 100) if total_requests > 0 else 0
        }


# 全局匹配器实例
matcher = HeartLinkMatcher() 