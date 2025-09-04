"""
健康检查视图
用于监控服务状态和公网访问
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import psutil
import os
import time
from pathlib import Path


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    pass
    """
    健康检查接口
    返回服务状态信息
    """
    try:
        # 系统信息
        pass
        pass
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # 项目信息
        project_root = Path(__file__).resolve().parent.parent.parent
        db_file = project_root / "db.sqlite3"
        db_size = db_file.stat().st_size if db_file.exists() else 0

        # 服务状态
        status = {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "QAToolBox",
            "version": "1.0.0",
            "environment": os.environ.get("DJANGO_SETTINGS_MODULE", "unknown"),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
            },
            "application": {
                "database_size": db_size,
                "database_exists": db_file.exists(),
                "project_root": str(project_root),
            },
            "network": {
                "host": request.get_host(),
                "remote_addr": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        }

        return JsonResponse(status, status=200)

    except Exception as e:
        pass
        pass
        pass
        error_status = {"status": "unhealthy", "error": str(e), "timestamp": time.time(), "service": "QAToolBox"}
        return JsonResponse(error_status, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def ping(request):
    pass
    """
    简单的ping接口
    用于网络连通性测试
    """
    return JsonResponse({"message": "pong", "timestamp": time.time(), "service": "QAToolBox"})


@csrf_exempt
@require_http_methods(["GET"])
def status(request):
    pass
    """
    详细状态接口
    返回更详细的服务状态信息
    """
    try:
        # 进程信息
        pass
        pass
        current_process = psutil.Process()

        # 网络连接
        connections = len(current_process.connections())

        # 文件描述符
        try:
            pass
            pass
            open_files = len(current_process.open_files())
        except:
            open_files = "N/A"

        status = {
            "status": "running",
            "timestamp": time.time(),
            "service": "QAToolBox",
            "process": {
                "pid": current_process.pid,
                "connections": connections,
                "open_files": open_files,
                "create_time": current_process.create_time(),
                "cpu_percent": current_process.cpu_percent(),
                "memory_percent": current_process.memory_percent(),
            },
            "system": {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "memory": psutil.virtual_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict(),
            },
        }

        return JsonResponse(status, status=200)

    except Exception as e:
        pass
        pass
        pass
        error_status = {"status": "error", "error": str(e), "timestamp": time.time(), "service": "QAToolBox"}
        return JsonResponse(error_status, status=500)
