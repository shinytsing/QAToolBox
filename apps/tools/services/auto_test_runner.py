"""
自动化测试运行器
在服务启动时自动运行测试，确保系统健康
"""
import os
import sys
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from django.conf import settings
from django.core.management import execute_from_command_line
from django.test import TestCase
from django.db import connection
from django.core.cache import cache
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class AutoTestRunner:
    """自动化测试运行器"""
    
    def __init__(self):
        self.test_results = {}
        self.is_running = False
        self.test_suites = {
            'unit_tests': {
                'command': ['python', 'manage.py', 'test', '--settings=config.settings.testing'],
                'timeout': 300,  # 5分钟
                'critical': True,
                'description': '单元测试'
            },
            'health_check': {
                'command': ['python', 'manage.py', 'health_check'],
                'timeout': 60,
                'critical': True,
                'description': '健康检查'
            },
            'database_migration': {
                'command': ['python', 'manage.py', 'migrate', '--check'],
                'timeout': 30,
                'critical': True,
                'description': '数据库迁移检查'
            },
            'cache_test': {
                'command': ['python', 'manage.py', 'cache_test'],
                'timeout': 30,
                'critical': False,
                'description': '缓存测试'
            },
            'api_test': {
                'command': ['python', 'manage.py', 'api_test'],
                'timeout': 120,
                'critical': False,
                'description': 'API测试'
            }
        }
    
    def start_auto_testing(self):
        """启动自动化测试"""
        if self.is_running:
            logger.warning("自动化测试已在运行中")
            return
        
        self.is_running = True
        logger.info("启动自动化测试...")
        
        # 在后台线程中运行测试
        test_thread = threading.Thread(target=self._run_all_tests)
        test_thread.daemon = True
        test_thread.start()
    
    def _run_all_tests(self):
        """运行所有测试"""
        try:
            start_time = time.time()
            
            for suite_name, suite_config in self.test_suites.items():
                if not self.is_running:
                    break
                
                logger.info(f"运行{suite_config['description']}...")
                result = self._run_test_suite(suite_name, suite_config)
                
                if result['success']:
                    logger.info(f"{suite_config['description']}通过")
                else:
                    logger.error(f"{suite_config['description']}失败: {result['error']}")
                    
                    if suite_config['critical']:
                        logger.critical(f"关键测试失败，系统可能不稳定")
                        # 可以在这里添加告警通知
                
                self.test_results[suite_name] = result
            
            total_time = time.time() - start_time
            logger.info(f"自动化测试完成，耗时: {total_time:.2f}秒")
            
            # 缓存测试结果
            cache.set('auto_test_results', self.test_results, timeout=3600)
            
        except Exception as e:
            logger.error(f"自动化测试运行失败: {e}")
        finally:
            self.is_running = False
    
    def _run_test_suite(self, suite_name: str, suite_config: Dict) -> Dict[str, Any]:
        """运行单个测试套件"""
        try:
            start_time = time.time()
            
            # 运行测试命令
            process = subprocess.Popen(
                suite_config['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=suite_config['timeout'])
                success = process.returncode == 0
                
                result = {
                    'success': success,
                    'return_code': process.returncode,
                    'stdout': stdout,
                    'stderr': stderr,
                    'execution_time': time.time() - start_time,
                    'timestamp': datetime.now()
                }
                
                if not success:
                    result['error'] = stderr or stdout
                
                return result
                
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    'success': False,
                    'error': f"测试超时 ({suite_config['timeout']}秒)",
                    'execution_time': suite_config['timeout'],
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': 0,
                'timestamp': datetime.now()
            }
    
    def get_test_results(self) -> Dict[str, Any]:
        """获取测试结果"""
        cached_results = cache.get('auto_test_results')
        if cached_results:
            return cached_results
        
        return self.test_results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        results = self.get_test_results()
        
        if not results:
            return {'status': 'no_results', 'message': '暂无测试结果'}
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results.values() if r.get('success', False))
        failed_tests = total_tests - passed_tests
        
        critical_failures = sum(
            1 for name, result in results.items()
            if not result.get('success', False) and self.test_suites[name]['critical']
        )
        
        return {
            'status': 'healthy' if critical_failures == 0 else 'unhealthy',
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'critical_failures': critical_failures,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'last_run': max(r.get('timestamp', datetime.min) for r in results.values()),
            'results': results
        }
    
    def stop_auto_testing(self):
        """停止自动化测试"""
        self.is_running = False
        logger.info("停止自动化测试")


class HealthCheckCommand:
    """健康检查命令"""
    
    def __init__(self):
        self.checks = [
            self._check_database,
            self._check_cache,
            self._check_static_files,
            self._check_media_files,
            self._check_celery,
            self._check_redis
        ]
    
    def run_health_check(self):
        """运行健康检查"""
        results = {}
        
        for check in self.checks:
            try:
                check_name = check.__name__.replace('_check_', '')
                result = check()
                results[check_name] = result
                
                if not result['healthy']:
                    logger.warning(f"健康检查失败 {check_name}: {result['message']}")
                else:
                    logger.info(f"健康检查通过 {check_name}")
                    
            except Exception as e:
                logger.error(f"健康检查异常 {check.__name__}: {e}")
                results[check_name] = {
                    'healthy': False,
                    'message': str(e),
                    'timestamp': datetime.now()
                }
        
        return results
    
    def _check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return {
                'healthy': True,
                'message': '数据库连接正常',
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'数据库连接失败: {e}',
                'timestamp': datetime.now()
            }
    
    def _check_cache(self) -> Dict[str, Any]:
        """检查缓存连接"""
        try:
            cache.set('health_check', 'ok', timeout=10)
            value = cache.get('health_check')
            
            if value == 'ok':
                return {
                    'healthy': True,
                    'message': '缓存连接正常',
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'healthy': False,
                    'message': '缓存读写失败',
                    'timestamp': datetime.now()
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'缓存连接失败: {e}',
                'timestamp': datetime.now()
            }
    
    def _check_static_files(self) -> Dict[str, Any]:
        """检查静态文件"""
        try:
            static_root = settings.STATIC_ROOT
            if os.path.exists(static_root):
                return {
                    'healthy': True,
                    'message': '静态文件目录正常',
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'healthy': False,
                    'message': '静态文件目录不存在',
                    'timestamp': datetime.now()
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'静态文件检查失败: {e}',
                'timestamp': datetime.now()
            }
    
    def _check_media_files(self) -> Dict[str, Any]:
        """检查媒体文件"""
        try:
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                return {
                    'healthy': True,
                    'message': '媒体文件目录正常',
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'healthy': False,
                    'message': '媒体文件目录不存在',
                    'timestamp': datetime.now()
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'媒体文件检查失败: {e}',
                'timestamp': datetime.now()
            }
    
    def _check_celery(self) -> Dict[str, Any]:
        """检查Celery状态"""
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            stats = inspect.stats()
            
            if stats:
                return {
                    'healthy': True,
                    'message': 'Celery工作进程正常',
                    'timestamp': datetime.now()
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Celery工作进程未运行',
                    'timestamp': datetime.now()
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Celery检查失败: {e}',
                'timestamp': datetime.now()
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            import redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            
            return {
                'healthy': True,
                'message': 'Redis连接正常',
                'timestamp': datetime.now()
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Redis连接失败: {e}',
                'timestamp': datetime.now()
            }


# 全局实例
auto_test_runner = AutoTestRunner()
health_checker = HealthCheckCommand()


# Django管理命令
def health_check_command():
    """健康检查管理命令"""
    results = health_checker.run_health_check()
    
    # 输出结果
    for check_name, result in results.items():
        status = "✅" if result['healthy'] else "❌"
        print(f"{status} {check_name}: {result['message']}")
    
    # 如果有失败的健康检查，退出码为1
    failed_checks = [r for r in results.values() if not r['healthy']]
    if failed_checks:
        sys.exit(1)


def cache_test_command():
    """缓存测试管理命令"""
    try:
        # 测试缓存读写
        test_key = 'cache_test_key'
        test_value = 'cache_test_value'
        
        cache.set(test_key, test_value, timeout=60)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            print("✅ 缓存测试通过")
            sys.exit(0)
        else:
            print("❌ 缓存测试失败：数据不一致")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 缓存测试失败：{e}")
        sys.exit(1)


def api_test_command():
    """API测试管理命令"""
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # 测试健康检查API
        health_url = reverse('health_check')
        response = client.get(health_url)
        
        if response.status_code == 200:
            print("✅ API测试通过")
            sys.exit(0)
        else:
            print(f"❌ API测试失败：状态码 {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ API测试失败：{e}")
        sys.exit(1)


# 定时任务：定期运行自动化测试
def run_scheduled_tests():
    """运行定时测试"""
    try:
        auto_test_runner.start_auto_testing()
        logger.info("定时测试已启动")
    except Exception as e:
        logger.error(f"定时测试启动失败: {e}")


# 服务启动时的初始化
def initialize_auto_testing():
    """初始化自动化测试"""
    try:
        # 延迟启动，等待服务完全启动
        def delayed_start():
            time.sleep(30)  # 等待30秒
            auto_test_runner.start_auto_testing()
        
        thread = threading.Thread(target=delayed_start)
        thread.daemon = True
        thread.start()
        
        logger.info("自动化测试初始化完成")
        
    except Exception as e:
        logger.error(f"自动化测试初始化失败: {e}")
