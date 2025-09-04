from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .async_task_manager import task_manager
import logging

logger = logging.getLogger(__name__)


class AsyncGenerateTestCasesAPI(APIView):
    """异步测试用例生成 API"""

    permission_classes = []  # 允许匿名访问

    def post(self, request):
        """创建异步任务"""
        try:
            # 获取请求参数
            requirement = request.data.get("requirement", "").strip()
            user_prompt = request.data.get("prompt", "").strip()
            is_batch = request.data.get("is_batch", False)
            batch_id = int(request.data.get("batch_id", 0))
            total_batches = int(request.data.get("total_batches", 1))

            # 参数验证
            if not requirement:
                return Response({"success": False, "error": "需求内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)

            if not user_prompt:
                return Response({"success": False, "error": "提示词不能为空"}, status=status.HTTP_400_BAD_REQUEST)

            # 创建异步任务
            user_id = request.user.username if request.user.is_authenticated else "anonymous"
            task_id = task_manager.create_task(
                requirement=requirement,
                user_prompt=user_prompt,
                is_batch=is_batch,
                batch_id=batch_id,
                total_batches=total_batches,
                user_id=user_id,
            )

            logger.info(f"创建异步任务: {task_id}, 用户: {request.user.username if request.user.is_authenticated else '匿名'}")

            return Response({"success": True, "task_id": task_id, "message": "任务已创建，正在后台处理中..."})

        except Exception as e:
            logger.error(f"创建异步任务失败: {e}")
            return Response(
                {"success": False, "error": f"创建任务失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskStatusAPI(APIView):
    """任务状态查询 API"""

    permission_classes = []  # 允许匿名访问

    def get(self, request, task_id):
        """获取任务状态"""
        try:
            task = task_manager.get_task_status(task_id)

            if not task:
                return Response({"success": False, "error": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)

            # 构建响应数据
            response_data = {
                "success": True,
                "task_id": task["id"],
                "status": task["status"],
                "progress": task["progress"],
                "created_at": task["created_at"],
                "started_at": task["started_at"],
                "completed_at": task["completed_at"],
            }

            # 如果任务完成，返回结果
            if task["status"] == "completed":
                response_data["result"] = task["result"]
            elif task["status"] == "failed":
                response_data["error"] = task["error"]

            # 添加当前步骤信息
            if "current_step" in task:
                response_data["current_step"] = task["current_step"]

            return Response(response_data)

        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return Response(
                {"success": False, "error": f"获取任务状态失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskListAPI(APIView):
    """任务列表 API"""

    permission_classes = []  # 允许匿名访问

    def get(self, request):
        """获取任务列表"""
        try:
            with task_manager.task_lock:
                tasks = list(task_manager.tasks.values())

            # 按创建时间倒序排列
            tasks.sort(key=lambda x: x["created_at"], reverse=True)

            # 只返回基本信息，不包含结果内容
            task_list = []
            for task in tasks:
                task_list.append(
                    {
                        "id": task["id"],
                        "requirement": task["requirement"],
                        "status": task["status"],
                        "progress": task["progress"],
                        "created_at": task["created_at"],
                        "started_at": task["started_at"],
                        "completed_at": task["completed_at"],
                    }
                )

            return Response({"success": True, "tasks": task_list, "total": len(task_list)})

        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return Response(
                {"success": False, "error": f"获取任务列表失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteTaskAPI(APIView):
    """删除任务 API"""

    permission_classes = []  # 允许匿名访问
    authentication_classes = []  # 禁用认证

    def dispatch(self, request, *args, **kwargs):
        # 手动设置CSRF豁免
        setattr(request, "_dont_enforce_csrf_checks", True)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """删除任务"""
        try:
            task_id = request.data.get("task_id")

            if not task_id:
                return Response({"success": False, "error": "任务ID不能为空"}, status=status.HTTP_400_BAD_REQUEST)

            # 删除任务
            success = task_manager.delete_task(task_id)

            if success:
                logger.info(f"任务 {task_id} 删除成功")
                return Response({"success": True, "message": "任务删除成功"})
            else:
                return Response({"success": False, "error": "任务不存在"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            return Response(
                {"success": False, "error": f"删除任务失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
