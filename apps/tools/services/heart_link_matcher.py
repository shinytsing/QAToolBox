#!/usr/bin/env python3
"""
心动链接智能匹配服务
提供更智能的匹配算法，考虑用户在线时间、匹配历史等因素
"""

import random
from datetime import timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.tools.models import ChatRoom, HeartLinkRequest, UserOnlineStatus
from apps.users.models import UserActivityLog


class HeartLinkMatcher:
    """心动链接智能匹配器"""

    def __init__(self):
        self.max_wait_time = 10  # 最大等待时间（分钟）- 统一设置为10分钟
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
        recent_activity = UserActivityLog.objects.filter(user=user, created_at__gte=timezone.now() - timedelta(days=7)).count()
        score += min(recent_activity * 5, 50)  # 最多加50分

        # 匹配成功率加分
        successful_matches = HeartLinkRequest.objects.filter(requester=user, status="matched").count()
        score += min(successful_matches * 10, 30)  # 最多加30分

        # 随机因子（避免总是匹配同一类用户）
        score += random.randint(-20, 20)

        return score

    def find_best_match(self, current_user, current_request):
        """找到最佳匹配对象"""
        try:
            # 查找可用的匹配对象，按等待时间排序
            available_requests = (
                HeartLinkRequest.objects.filter(
                    status="pending",
                    requester__is_staff=False,
                    requester__is_superuser=False,
                    requester__is_active=True,
                )
                .exclude(Q(requester=current_user))
                .order_by("created_at")
            )  # 优先匹配等待时间最长的

            if not available_requests.exists():
                return None

            # 尝试匹配等待时间最长的用户
            for available_request in available_requests:
                try:
                    # 使用乐观锁：尝试更新状态
                    updated = HeartLinkRequest.objects.filter(id=available_request.id, status="pending").update(
                        status="matching"
                    )

                    if updated > 0:
                        # 更新成功，重新获取对象
                        available_request.refresh_from_db()
                        print(f"成功匹配用户: {available_request.requester.username}")
                        return available_request

                except Exception as e:
                    print(f"匹配过程中出错: {str(e)}")
                    continue

            return None

        except Exception as e:
            print(f"查找匹配对象时出错: {str(e)}")
            return None

    def create_match(self, user1, user2):
        """创建匹配"""
        import uuid

        # 创建聊天室
        room_id = str(uuid.uuid4())
        chat_room = ChatRoom.objects.create(room_id=room_id, user1=user1, user2=user2, status="active")

        return chat_room

    def match_users(self, current_user, current_request):
        """执行用户匹配"""
        try:
            # 使用更短的超时时间避免长时间锁定
            with transaction.atomic():
                # 找到最佳匹配
                best_match_request = self.find_best_match(current_user, current_request)

                if not best_match_request:
                    print(f"用户 {current_user.username} 没有找到匹配对象")
                    return None, None

                # 双重检查：确保对方请求状态为matching
                best_match_request.refresh_from_db()
                if best_match_request.status != "matching":
                    print(f"用户 {best_match_request.requester.username} 的状态不是matching，可能是被其他用户匹配了")
                    return None, None

                # 优先使用对方的聊天室，如果没有则使用自己的，都没有则创建新的
                chat_room = None
                if best_match_request.chat_room:
                    # 使用对方的聊天室
                    chat_room = best_match_request.chat_room
                    chat_room.user2 = current_user
                    chat_room.status = "active"
                    chat_room.save()
                    print(f"使用对方聊天室: {chat_room.room_id}")
                elif current_request.chat_room:
                    # 使用自己的聊天室
                    chat_room = current_request.chat_room
                    chat_room.user2 = best_match_request.requester
                    chat_room.status = "active"
                    chat_room.save()
                    print(f"使用自己聊天室: {chat_room.room_id}")
                else:
                    # 创建新的聊天室
                    chat_room = self.create_match(current_user, best_match_request.requester)
                    print(f"创建新聊天室: {chat_room.room_id}")

                # 更新两个请求的状态
                current_request.status = "matched"
                current_request.matched_with = best_match_request.requester
                current_request.matched_at = timezone.now()
                current_request.chat_room = chat_room
                current_request.save()

                best_match_request.status = "matched"
                best_match_request.matched_with = current_user
                best_match_request.matched_at = timezone.now()
                # 如果best_match_request没有聊天室，也使用同一个聊天室
                if not best_match_request.chat_room:
                    best_match_request.chat_room = chat_room
                best_match_request.save()

                print(f"匹配成功: {current_user.username} <-> {best_match_request.requester.username}")
                return chat_room, best_match_request.requester

        except Exception as e:
            # 如果匹配失败，记录错误但不立即设为过期
            print(f"匹配失败: {str(e)}")
            # 保持pending状态，让用户有机会重试
            # 只有在明确知道是致命错误时才设为过期
            if "database is locked" in str(e).lower():
                # 数据库锁定错误，保持pending状态，让用户重试
                print("数据库锁定，保持pending状态")
                return None, None
            elif "duplicate key" in str(e).lower():
                # 重复键错误，可能已经被匹配，设为过期
                print("重复键错误，设为过期")
                current_request.status = "expired"
                current_request.save()
                return None, None
            else:
                # 其他错误，保持pending状态，让用户重试
                print("其他错误，保持pending状态")
                return None, None

    def cleanup_expired_requests(self):
        """清理过期的请求（10分钟）"""
        expired_time = timezone.now() - timedelta(minutes=10)  # 统一设置为10分钟
        expired_requests = HeartLinkRequest.objects.filter(status="pending", created_at__lt=expired_time)

        for request in expired_requests:
            request.status = "expired"
            request.save()

    def get_matching_stats(self):
        """获取匹配统计信息"""
        total_requests = HeartLinkRequest.objects.count()
        matched_requests = HeartLinkRequest.objects.filter(status="matched").count()
        pending_requests = HeartLinkRequest.objects.filter(status="pending").count()
        expired_requests = HeartLinkRequest.objects.filter(status="expired").count()

        return {
            "total": total_requests,
            "matched": matched_requests,
            "pending": pending_requests,
            "expired": expired_requests,
            "match_rate": (matched_requests / total_requests * 100) if total_requests > 0 else 0,
        }


# 全局匹配器实例
matcher = HeartLinkMatcher()
