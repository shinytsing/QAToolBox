from django.apps import AppConfig


class ToolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tools"
    verbose_name = "工具管理"

    def ready(self):
        """应用启动时的初始化"""
        import os

        # 只在非管理命令环境下运行
        if not self._is_management_command():
            self._initialize_services()

    def _is_management_command(self):
        """检查是否在管理命令环境下运行"""
        import sys

        return len(sys.argv) > 1 and sys.argv[1] in [
            "runserver",
            "migrate",
            "collectstatic",
            "test",
            "shell",
            "health_check",
            "cache_test",
            "api_test",
        ]

    def _initialize_services(self):
        """初始化各种服务"""
        try:
            # 导入服务 (已移除测试模块)
            # from .services.auto_test_runner import initialize_auto_testing
            from .services.monitoring_service import periodic_health_check
            from .services.performance_optimizer import run_performance_optimization
            from .services.database_sharding import check_shards_health

            # 初始化服务 (跳过测试模块)
            # initialize_auto_testing()

            # 启动定时任务
            self._start_scheduled_tasks()

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"服务初始化失败: {e}")

    def _start_scheduled_tasks(self):
        """启动定时任务"""
        try:
            import threading
            import time
            from django.core.cache import cache

            def run_scheduled_tasks():
                """运行定时任务"""
                while True:
                    try:
                        # 每5分钟运行一次健康检查
                        from .services.monitoring_service import periodic_health_check

                        periodic_health_check()

                        # 每10分钟运行一次性能优化
                        from .services.performance_optimizer import run_performance_optimization

                        run_performance_optimization()

                        # 每15分钟运行一次分片健康检查
                        from .services.database_sharding import check_shards_health

                        check_shards_health()

                        # 每30分钟运行一次自动化测试 (已禁用)
                        # from .services.auto_test_runner import run_scheduled_tests
                        # run_scheduled_tests()

                        # 每60分钟运行一次垃圾回收
                        from .services.performance_optimizer import run_garbage_collection

                        run_garbage_collection()

                        # 等待5分钟
                        time.sleep(300)

                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(f"定时任务执行失败: {e}")
                        time.sleep(60)  # 出错后等待1分钟再重试

            # 启动定时任务线程
            task_thread = threading.Thread(target=run_scheduled_tasks)
            task_thread.daemon = True
            task_thread.start()

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"定时任务启动失败: {e}")
