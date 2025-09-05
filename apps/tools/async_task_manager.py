import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .utils import DeepSeekClient

logger = logging.getLogger(__name__)


class AsyncTaskManager:
    """异步任务管理器 - 支持真正的后台任务"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.task_lock = threading.Lock()
        # 使用项目根目录下的task_storage目录
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.storage_dir = os.path.join(project_root, "task_storage")
        # 任务超时配置（小时）
        self.task_timeout_hours = 1
        self._ensure_storage_dir()
        self._load_tasks_from_storage()
        self._start_cleanup_thread()

    def _ensure_storage_dir(self):
        """确保存储目录存在"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def _load_tasks_from_storage(self):
        """从存储中加载任务"""
        try:
            tasks_file = os.path.join(self.storage_dir, "tasks.json")
            if os.path.exists(tasks_file):
                with open(tasks_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    # 只加载未完成的任务
                    for task_id, task_data in tasks_data.items():
                        if task_data.get("status") in ["pending", "running"]:
                            self.tasks[task_id] = task_data
                            logger.info(f"从存储中恢复任务: {task_id}")
        except Exception as e:
            logger.error(f"加载任务存储失败: {e}")

    def _save_tasks_to_storage(self):
        """保存任务到存储"""
        try:
            tasks_file = os.path.join(self.storage_dir, "tasks.json")
            with open(tasks_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存任务存储失败: {e}")

    def _start_cleanup_thread(self):
        """启动清理线程，定期清理过期任务和超时任务"""

        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # 每5分钟检查一次
                    self._cleanup_expired_tasks()
                    self._cleanup_timeout_tasks()
                except Exception as e:
                    logger.error(f"清理任务失败: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_expired_tasks(self):
        """清理过期任务（超过7天的已完成任务）"""
        with self.task_lock:
            expired_tasks = []
            cutoff_time = datetime.now() - timedelta(days=7)

            for task_id, task in self.tasks.items():
                if task.get("status") in ["completed", "failed"]:
                    completed_at = task.get("completed_at")
                    if completed_at:
                        try:
                            completed_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                            if completed_time < cutoff_time:
                                expired_tasks.append(task_id)
                        except Exception:
                            pass

            for task_id in expired_tasks:
                del self.tasks[task_id]
                logger.info(f"清理过期任务: {task_id}")

            if expired_tasks:
                self._save_tasks_to_storage()

    def _cleanup_timeout_tasks(self):
        """清理超时任务（超过配置时间未完成的任务）"""
        with self.task_lock:
            timeout_tasks = []
            timeout_threshold = datetime.now() - timedelta(hours=self.task_timeout_hours)

            for task_id, task in self.tasks.items():
                # 只检查未完成的任务
                if task.get("status") in ["pending", "running"]:
                    created_at = task.get("created_at")
                    if created_at:
                        try:
                            created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                            if created_time < timeout_threshold:
                                timeout_tasks.append(task_id)
                        except Exception:
                            # 如果时间格式有问题，也标记为超时
                            timeout_tasks.append(task_id)

            # 删除超时任务
            for task_id in timeout_tasks:
                task = self.tasks[task_id]
                logger.info(f"任务 {task_id} 超时自动删除 (创建时间: {task.get('created_at')}, 状态: {task.get('status')})")
                del self.tasks[task_id]

            if timeout_tasks:
                self._save_tasks_to_storage()
                logger.info(f"自动清理了 {len(timeout_tasks)} 个超时任务")

    def manual_cleanup_timeout_tasks(self):
        """手动触发超时任务清理"""
        self._cleanup_timeout_tasks()
        return len([t for t in self.tasks.values() if t.get("status") in ["pending", "running"]])

    def _is_task_timeout(self, task_id: str) -> bool:
        """检查任务是否超时"""
        with self.task_lock:
            if task_id not in self.tasks:
                return True

            task = self.tasks[task_id]
            created_at = task.get("created_at")
            if not created_at:
                return True

            try:
                created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                timeout_threshold = datetime.now() - timedelta(hours=self.task_timeout_hours)
                return created_time < timeout_threshold
            except Exception:
                return True

    def create_task(
        self,
        requirement: str,
        user_prompt: str,
        is_batch: bool = False,
        batch_id: int = 0,
        total_batches: int = 1,
        user_id: str = None,
    ) -> str:
        """创建新的后台任务"""
        task_id = str(uuid.uuid4())

        with self.task_lock:
            self.tasks[task_id] = {
                "id": task_id,
                "requirement": requirement,
                "user_prompt": user_prompt,
                "is_batch": is_batch,
                "batch_id": batch_id,
                "total_batches": total_batches,
                "user_id": user_id,
                "status": "pending",  # pending, running, completed, failed
                "progress": 0,
                "current_step": "等待处理",
                "result": None,
                "error": None,
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
            }

            # 保存到存储
            self._save_tasks_to_storage()

        # 启动后台任务
        thread = threading.Thread(target=self._execute_task, args=(task_id,))
        thread.daemon = True
        thread.start()

        logger.info(f"创建后台任务: {task_id}, 需求: {requirement[:50]}...")
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        with self.task_lock:
            return self.tasks.get(task_id)

    def get_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务列表"""
        with self.task_lock:
            return list(self.tasks.values())

    def delete_task(self, task_id: str) -> bool:
        """删除任务（停止运行中的任务并删除）"""
        with self.task_lock:
            if task_id not in self.tasks:
                return False

            task = self.tasks[task_id]

            # 如果任务正在运行，标记为取消状态
            if task["status"] == "running":
                task["status"] = "cancelled"
                task["completed_at"] = datetime.now().isoformat()
                task["error"] = "任务已被用户取消"
                logger.info(f"任务 {task_id} 已被取消")

            # 删除任务
            del self.tasks[task_id]
            self._save_tasks_to_storage()
            logger.info(f"任务 {task_id} 已删除")
            return True

    def _execute_task(self, task_id: str):
        """执行后台任务"""
        try:
            with self.task_lock:
                if task_id not in self.tasks:
                    return
                self.tasks[task_id]["status"] = "running"
                self.tasks[task_id]["started_at"] = datetime.now().isoformat()
                self.tasks[task_id]["progress"] = 5
                self.tasks[task_id]["current_step"] = "分析需求"

            # 检查任务是否超时
            if self._is_task_timeout(task_id):
                logger.info(f"任务 {task_id} 在开始执行时已超时，跳过执行")
                return

            # 获取任务参数
            task = self.tasks[task_id]
            requirement = task["requirement"]
            user_prompt = task["user_prompt"]
            is_batch = task["is_batch"]
            batch_id = task["batch_id"]
            total_batches = task["total_batches"]

            # 步骤1: 分析需求 (5-15%)
            time.sleep(1)  # 模拟分析时间

            # 检查任务是否超时
            if self._is_task_timeout(task_id):
                logger.info(f"任务 {task_id} 在步骤1后超时，停止执行")
                return

            with self.task_lock:
                if task_id not in self.tasks:  # 任务可能已被删除
                    return
                self.tasks[task_id]["progress"] = 15
                self.tasks[task_id]["current_step"] = "生成功能测试用例"
                self._save_tasks_to_storage()

            # 步骤2: 生成功能测试用例 (15-30%)
            time.sleep(2)

            # 检查任务是否超时
            if self._is_task_timeout(task_id):
                logger.info(f"任务 {task_id} 在步骤2后超时，停止执行")
                return

            with self.task_lock:
                if task_id not in self.tasks:
                    return
                self.tasks[task_id]["progress"] = 30
                self.tasks[task_id]["current_step"] = "生成界面测试用例"
                self._save_tasks_to_storage()

            # 步骤3: 生成界面测试用例 (30-45%)
            time.sleep(2)

            # 检查任务是否超时
            if self._is_task_timeout(task_id):
                logger.info(f"任务 {task_id} 在步骤3后超时，停止执行")
                return

            with self.task_lock:
                if task_id not in self.tasks:
                    return
                self.tasks[task_id]["progress"] = 45
                self.tasks[task_id]["current_step"] = "生成性能测试用例"
                self._save_tasks_to_storage()

            # 步骤4: 生成性能测试用例 (45-60%)
            time.sleep(2)
            with self.task_lock:
                self.tasks[task_id]["progress"] = 60
                self.tasks[task_id]["current_step"] = "生成安全测试用例"
                self._save_tasks_to_storage()

            # 步骤5: 生成安全测试用例 (60-75%)
            time.sleep(2)
            with self.task_lock:
                self.tasks[task_id]["progress"] = 75
                self.tasks[task_id]["current_step"] = "生成兼容性测试用例"
                self._save_tasks_to_storage()

            # 步骤6: 生成兼容性测试用例 (75-90%)
            time.sleep(2)
            with self.task_lock:
                self.tasks[task_id]["progress"] = 90
                self.tasks[task_id]["current_step"] = "整理和优化"
                self._save_tasks_to_storage()

            # 调用 DeepSeek API
            client = DeepSeekClient()

            # 生成测试用例
            result = client.generate_test_cases(
                requirement=requirement,
                user_prompt=user_prompt,
                is_batch=is_batch,
                batch_id=batch_id,
                total_batches=total_batches,
            )

            # 步骤7: 完成 (90-100%)
            time.sleep(1)
            with self.task_lock:
                self.tasks[task_id]["status"] = "completed"
                self.tasks[task_id]["progress"] = 100
                self.tasks[task_id]["current_step"] = "生成完成"
                self.tasks[task_id]["result"] = result
                self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                self._save_tasks_to_storage()

            # 创建完成通知
            self._create_completion_notification(task_id, task)

            logger.info(f"后台任务完成: {task_id}")

        except Exception as e:
            # 任务失败
            with self.task_lock:
                if task_id in self.tasks:
                    self.tasks[task_id]["status"] = "failed"
                    self.tasks[task_id]["error"] = str(e)
                    self.tasks[task_id]["current_step"] = "生成失败"
                    self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
                    self._save_tasks_to_storage()

            logger.error(f"后台任务失败: {task_id}, 错误: {e}")

    def _create_completion_notification(self, task_id: str, task: Dict[str, Any]):
        """创建任务完成通知"""
        try:
            from django.contrib.auth.models import User

            from .models import ChatMessage, ChatNotification, ChatRoom

            # 获取admin用户
            admin_user = User.objects.filter(username="admin").first()
            if not admin_user:
                logger.warning("未找到admin用户，跳过通知创建")
                return

            # 创建一个系统通知消息
            requirement_preview = task.get("requirement", "")[:50] + ("..." if len(task.get("requirement", "")) > 50 else "")
            system_message = f"🎉 后台任务已完成！\n\n📋 任务类型: 测试用例生成\n🆔 任务ID: {task_id[:8]}...\n📝 需求: {requirement_preview}\n⏰ 完成时间: {task.get('completed_at', '')}\n\n💡 您可以关闭页面，任务已在后台完成！"

            # 创建系统聊天室（如果不存在）
            system_room, created = ChatRoom.objects.get_or_create(
                name="系统通知", defaults={"description": "系统任务完成通知", "is_public": False, "created_by": admin_user}
            )

            # 创建系统消息
            system_chat_message = ChatMessage.objects.create(
                room=system_room, sender=admin_user, content=system_message, message_type="system"
            )

            # 为任务创建者创建通知
            user_id = task.get("user_id")
            if user_id and user_id != "anonymous":
                try:
                    user = User.objects.get(username=user_id)
                    ChatNotification.objects.create(user=user, room=system_room, message=system_chat_message, is_read=False)
                    logger.info(f"为用户 {user_id} 创建任务完成通知")
                except User.DoesNotExist:
                    logger.warning(f"用户 {user_id} 不存在，跳过通知创建")
            else:
                logger.info("匿名用户任务，跳过通知创建")

            logger.info(f"🎉 任务完成通知已创建: 任务 {task_id[:8]}... 已完成")

        except Exception as e:
            logger.error(f"创建任务完成通知失败: {e}")

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self.task_lock:
            tasks_to_remove = []
            for task_id, task in self.tasks.items():
                try:
                    created_at = datetime.fromisoformat(task["created_at"]).timestamp()
                    if created_at < cutoff_time:
                        tasks_to_remove.append(task_id)
                except Exception:
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.tasks[task_id]
                logger.info(f"清理旧任务: {task_id}")


# 全局任务管理器实例
task_manager = AsyncTaskManager()
