"""
数据库清理服务
定期清理过期和无效数据
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from django.core.cache import cache
from django.db import connection

from apps.tools.models import SocialMediaSubscription, ToolUsageLog

logger = logging.getLogger(__name__)


class DatabaseCleanupService:
    """数据库清理服务"""

    def __init__(self):
        self.cleanup_config = {
            "tool_usage_logs": {"retention_days": 90, "batch_size": 1000, "enabled": True},  # 保留90天
            "social_media_subscriptions": {"retention_days": 180, "batch_size": 500, "enabled": True},  # 保留180天
            "user_sessions": {"retention_days": 30, "batch_size": 1000, "enabled": True},  # 保留30天
            "cache_cleanup": {"enabled": True},
            "orphaned_files": {"enabled": True},
        }

    def cleanup_old_data(self) -> Dict[str, Any]:
        """清理过期数据"""
        results = {}

        try:
            # 清理工具使用日志
            if self.cleanup_config["tool_usage_logs"]["enabled"]:
                results["tool_usage_logs"] = self._cleanup_tool_usage_logs()

            # 清理社交媒体订阅
            if self.cleanup_config["social_media_subscriptions"]["enabled"]:
                results["social_media_subscriptions"] = self._cleanup_social_media_subscriptions()

            # 清理用户会话
            if self.cleanup_config["user_sessions"]["enabled"]:
                results["user_sessions"] = self._cleanup_user_sessions()

            # 清理缓存
            if self.cleanup_config["cache_cleanup"]["enabled"]:
                results["cache_cleanup"] = self._cleanup_cache()

            # 清理孤立文件
            if self.cleanup_config["orphaned_files"]["enabled"]:
                results["orphaned_files"] = self._cleanup_orphaned_files()

            # 清理数据库连接
            self._cleanup_database_connections()

            logger.info("数据库清理完成")
            return {"status": "success", "results": results, "timestamp": datetime.now()}

        except Exception as e:
            logger.error(f"数据库清理失败: {e}")
            return {"status": "error", "message": str(e), "timestamp": datetime.now()}

    def _cleanup_tool_usage_logs(self) -> Dict[str, Any]:
        """清理工具使用日志"""
        try:
            retention_days = self.cleanup_config["tool_usage_logs"]["retention_days"]
            batch_size = self.cleanup_config["tool_usage_logs"]["batch_size"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # 获取要删除的记录数量
            total_count = ToolUsageLog.objects.filter(created_at__lt=cutoff_date).count()

            # 分批删除
            deleted_count = 0
            while True:
                batch = ToolUsageLog.objects.filter(created_at__lt=cutoff_date)[:batch_size]

                if not batch.exists():
                    break

                batch_ids = list(batch.values_list("id", flat=True))
                ToolUsageLog.objects.filter(id__in=batch_ids).delete()
                deleted_count += len(batch_ids)

                logger.info(f"已删除 {deleted_count}/{total_count} 条工具使用日志")

            return {"deleted_count": deleted_count, "total_count": total_count, "retention_days": retention_days}

        except Exception as e:
            logger.error(f"清理工具使用日志失败: {e}")
            return {"error": str(e)}

    def _cleanup_social_media_subscriptions(self) -> Dict[str, Any]:
        """清理社交媒体订阅"""
        try:
            retention_days = self.cleanup_config["social_media_subscriptions"]["retention_days"]
            batch_size = self.cleanup_config["social_media_subscriptions"]["batch_size"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # 获取要删除的记录数量
            total_count = SocialMediaSubscription.objects.filter(created_at__lt=cutoff_date, status="inactive").count()

            # 分批删除
            deleted_count = 0
            while True:
                batch = SocialMediaSubscription.objects.filter(created_at__lt=cutoff_date, status="inactive")[:batch_size]

                if not batch.exists():
                    break

                batch_ids = list(batch.values_list("id", flat=True))
                SocialMediaSubscription.objects.filter(id__in=batch_ids).delete()
                deleted_count += len(batch_ids)

                logger.info(f"已删除 {deleted_count}/{total_count} 条社交媒体订阅")

            return {"deleted_count": deleted_count, "total_count": total_count, "retention_days": retention_days}

        except Exception as e:
            logger.error(f"清理社交媒体订阅失败: {e}")
            return {"error": str(e)}

    def _cleanup_user_sessions(self) -> Dict[str, Any]:
        """清理用户会话"""
        try:
            retention_days = self.cleanup_config["user_sessions"]["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # 清理Django会话
            from django.contrib.sessions.models import Session
            from django.utils import timezone

            expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
            deleted_count = expired_sessions.count()
            expired_sessions.delete()

            return {"deleted_count": deleted_count, "retention_days": retention_days}

        except Exception as e:
            logger.error(f"清理用户会话失败: {e}")
            return {"error": str(e)}

    def _cleanup_cache(self) -> Dict[str, Any]:
        """清理缓存"""
        try:
            # 清理过期缓存
            cache.clear()

            return {"status": "cleared", "message": "缓存已清理"}

        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return {"error": str(e)}

    def _cleanup_orphaned_files(self) -> Dict[str, Any]:
        """清理孤立文件"""
        try:
            import os

            from django.conf import settings

            media_root = settings.MEDIA_ROOT
            deleted_files = 0

            # 遍历媒体文件目录
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    file_path = os.path.join(root, file)

                    # 检查文件是否被引用
                    if not self._is_file_referenced(file_path):
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                        except Exception as e:
                            logger.warning(f"删除文件失败 {file_path}: {e}")

            return {"deleted_files": deleted_files}

        except Exception as e:
            logger.error(f"清理孤立文件失败: {e}")
            return {"error": str(e)}

    def _is_file_referenced(self, file_path: str) -> bool:
        """检查文件是否被数据库引用"""
        try:
            # 这里可以添加检查逻辑，比如检查是否有模型字段引用了这个文件
            # 暂时返回True，避免误删
            return True
        except Exception:
            return True

    def _cleanup_database_connections(self) -> None:
        """清理数据库连接"""
        try:
            # 关闭数据库连接
            connection.close()
            logger.info("数据库连接已清理")
        except Exception as e:
            logger.error(f"清理数据库连接失败: {e}")

    def get_cleanup_stats(self) -> Dict[str, Any]:
        """获取清理统计信息"""
        try:
            stats = {}

            # 工具使用日志统计
            retention_days = self.cleanup_config["tool_usage_logs"]["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            stats["tool_usage_logs"] = {
                "total_count": ToolUsageLog.objects.count(),
                "old_count": ToolUsageLog.objects.filter(created_at__lt=cutoff_date).count(),
                "retention_days": retention_days,
            }

            # 社交媒体订阅统计
            retention_days = self.cleanup_config["social_media_subscriptions"]["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            stats["social_media_subscriptions"] = {
                "total_count": SocialMediaSubscription.objects.count(),
                "old_count": SocialMediaSubscription.objects.filter(created_at__lt=cutoff_date, status="inactive").count(),
                "retention_days": retention_days,
            }

            # 用户会话统计
            from django.contrib.sessions.models import Session
            from django.utils import timezone

            stats["user_sessions"] = {
                "total_count": Session.objects.count(),
                "expired_count": Session.objects.filter(expire_date__lt=timezone.now()).count(),
            }

            return stats

        except Exception as e:
            logger.error(f"获取清理统计信息失败: {e}")
            return {"error": str(e)}


# 全局实例
database_cleanup_service = DatabaseCleanupService()


# 清理函数
def cleanup_old_data() -> Dict[str, Any]:
    """清理过期数据"""
    return database_cleanup_service.cleanup_old_data()


# 获取统计信息
def get_cleanup_stats() -> Dict[str, Any]:
    """获取清理统计信息"""
    return database_cleanup_service.get_cleanup_stats()
