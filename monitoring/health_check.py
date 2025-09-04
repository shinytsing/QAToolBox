#!/usr/bin/env python3
"""
系统健康检查脚本
监控应用各个组件的健康状态
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import psutil
import requests

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

# Django设置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
import django

django.setup()

from django.conf import settings
from django.core.cache import cache
from django.db import connections


@dataclass
class HealthCheckResult:
    """健康检查结果"""

    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    details: Dict = None
    timestamp: str = None
    response_time: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.results = []
        self.base_url = getattr(settings, "HEALTH_CHECK_BASE_URL", "http://localhost:8000")
        self.timeout = 10

    def check_all(self) -> List[HealthCheckResult]:
        """执行所有健康检查"""
        checks = [
            self.check_web_server,
            self.check_database,
            self.check_redis,
            self.check_celery,
            self.check_disk_space,
            self.check_memory,
            self.check_cpu,
            self.check_network,
            self.check_ssl_certificate,
            self.check_external_apis,
        ]

        self.results = []
        for check in checks:
            try:
                result = check()
                if isinstance(result, list):
                    self.results.extend(result)
                else:
                    self.results.append(result)
            except Exception as e:
                self.results.append(
                    HealthCheckResult(
                        component=check.__name__.replace("check_", ""), status="critical", message=f"检查失败: {str(e)}"
                    )
                )

        return self.results

    def check_web_server(self) -> HealthCheckResult:
        """检查Web服务器"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/health/", timeout=self.timeout)

            response_time = time.time() - start_time

            if response.status_code == 200:
                return HealthCheckResult(
                    component="web_server",
                    status="healthy",
                    message="Web服务器运行正常",
                    response_time=response_time,
                    details={"status_code": response.status_code, "response_time": f"{response_time:.3f}s"},
                )
            else:
                return HealthCheckResult(
                    component="web_server",
                    status="warning",
                    message=f"Web服务器响应异常: {response.status_code}",
                    response_time=response_time,
                )

        except requests.exceptions.RequestException as e:
            return HealthCheckResult(component="web_server", status="critical", message=f"Web服务器无法访问: {str(e)}")

    def check_database(self) -> HealthCheckResult:
        """检查数据库连接"""
        start_time = time.time()

        try:
            from django.db import connection

            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            response_time = time.time() - start_time

            # 获取数据库统计信息
            stats = self.get_database_stats()

            return HealthCheckResult(
                component="database", status="healthy", message="数据库连接正常", response_time=response_time, details=stats
            )

        except Exception as e:
            return HealthCheckResult(component="database", status="critical", message=f"数据库连接失败: {str(e)}")

    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        try:
            from django.db import connection

            with connection.cursor() as cursor:
                # PostgreSQL统计查询
                cursor.execute(
                    """
                    SELECT 
                        count(*) as total_connections,
                        sum(case when state = 'active' then 1 else 0 end) as active_connections
                    FROM pg_stat_activity
                """
                )

                row = cursor.fetchone()
                return {
                    "total_connections": row[0],
                    "active_connections": row[1],
                    "database_name": connection.settings_dict["NAME"],
                }
        except Exception:
            return {}

    def check_redis(self) -> HealthCheckResult:
        """检查Redis连接"""
        start_time = time.time()

        try:
            # 测试缓存连接
            test_key = "health_check_test"
            test_value = str(int(time.time()))

            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)

            response_time = time.time() - start_time

            if retrieved_value == test_value:
                # 获取Redis统计信息
                stats = self.get_redis_stats()

                return HealthCheckResult(
                    component="redis", status="healthy", message="Redis连接正常", response_time=response_time, details=stats
                )
            else:
                return HealthCheckResult(component="redis", status="warning", message="Redis数据读写异常")

        except Exception as e:
            return HealthCheckResult(component="redis", status="critical", message=f"Redis连接失败: {str(e)}")

    def get_redis_stats(self) -> Dict:
        """获取Redis统计信息"""
        try:
            from django_redis import get_redis_connection

            r = get_redis_connection("default")
            info = r.info()

            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception:
            return {}

    def check_celery(self) -> HealthCheckResult:
        """检查Celery工作进程"""
        try:
            from celery import current_app

            # 检查Celery工作进程
            inspect = current_app.control.inspect()
            active = inspect.active()
            stats = inspect.stats()

            if active is None or stats is None:
                return HealthCheckResult(component="celery", status="critical", message="Celery工作进程无响应")

            worker_count = len(active.keys()) if active else 0

            if worker_count > 0:
                return HealthCheckResult(
                    component="celery",
                    status="healthy",
                    message=f"Celery运行正常，{worker_count}个工作进程",
                    details={"worker_count": worker_count, "workers": list(active.keys()) if active else []},
                )
            else:
                return HealthCheckResult(component="celery", status="warning", message="没有可用的Celery工作进程")

        except Exception as e:
            return HealthCheckResult(component="celery", status="critical", message=f"Celery检查失败: {str(e)}")

    def check_disk_space(self) -> HealthCheckResult:
        """检查磁盘空间"""
        try:
            disk_usage = psutil.disk_usage("/")
            used_percent = (disk_usage.used / disk_usage.total) * 100

            if used_percent < 80:
                status = "healthy"
                message = f"磁盘空间充足 ({used_percent:.1f}% 已使用)"
            elif used_percent < 90:
                status = "warning"
                message = f"磁盘空间不足 ({used_percent:.1f}% 已使用)"
            else:
                status = "critical"
                message = f"磁盘空间严重不足 ({used_percent:.1f}% 已使用)"

            return HealthCheckResult(
                component="disk_space",
                status=status,
                message=message,
                details={
                    "total": self.bytes_to_human(disk_usage.total),
                    "used": self.bytes_to_human(disk_usage.used),
                    "free": self.bytes_to_human(disk_usage.free),
                    "used_percent": f"{used_percent:.1f}%",
                },
            )

        except Exception as e:
            return HealthCheckResult(component="disk_space", status="critical", message=f"磁盘空间检查失败: {str(e)}")

    def check_memory(self) -> HealthCheckResult:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent

            if used_percent < 80:
                status = "healthy"
                message = f"内存使用正常 ({used_percent:.1f}% 已使用)"
            elif used_percent < 90:
                status = "warning"
                message = f"内存使用较高 ({used_percent:.1f}% 已使用)"
            else:
                status = "critical"
                message = f"内存使用过高 ({used_percent:.1f}% 已使用)"

            return HealthCheckResult(
                component="memory",
                status=status,
                message=message,
                details={
                    "total": self.bytes_to_human(memory.total),
                    "available": self.bytes_to_human(memory.available),
                    "used": self.bytes_to_human(memory.used),
                    "used_percent": f"{used_percent:.1f}%",
                },
            )

        except Exception as e:
            return HealthCheckResult(component="memory", status="critical", message=f"内存检查失败: {str(e)}")

    def check_cpu(self) -> HealthCheckResult:
        """检查CPU使用率"""
        try:
            # 获取1秒内的CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

            if cpu_percent < 70:
                status = "healthy"
                message = f"CPU使用正常 ({cpu_percent:.1f}%)"
            elif cpu_percent < 85:
                status = "warning"
                message = f"CPU使用较高 ({cpu_percent:.1f}%)"
            else:
                status = "critical"
                message = f"CPU使用过高 ({cpu_percent:.1f}%)"

            return HealthCheckResult(
                component="cpu",
                status=status,
                message=message,
                details={
                    "cpu_percent": f"{cpu_percent:.1f}%",
                    "cpu_count": cpu_count,
                    "load_avg_1min": f"{load_avg[0]:.2f}",
                    "load_avg_5min": f"{load_avg[1]:.2f}",
                    "load_avg_15min": f"{load_avg[2]:.2f}",
                },
            )

        except Exception as e:
            return HealthCheckResult(component="cpu", status="critical", message=f"CPU检查失败: {str(e)}")

    def check_network(self) -> HealthCheckResult:
        """检查网络连接"""
        try:
            # 检查网络连接
            response = requests.get("https://www.baidu.com", timeout=5)

            if response.status_code == 200:
                return HealthCheckResult(component="network", status="healthy", message="网络连接正常")
            else:
                return HealthCheckResult(
                    component="network", status="warning", message=f"网络连接异常: {response.status_code}"
                )

        except Exception as e:
            return HealthCheckResult(component="network", status="critical", message=f"网络连接失败: {str(e)}")

    def check_ssl_certificate(self) -> HealthCheckResult:
        """检查SSL证书"""
        try:
            import socket
            import ssl
            from urllib.parse import urlparse

            if not self.base_url.startswith("https://"):
                return HealthCheckResult(component="ssl_certificate", status="healthy", message="未使用HTTPS，跳过SSL检查")

            parsed_url = urlparse(self.base_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or 443

            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

            # 检查证书过期时间
            not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
            days_left = (not_after - datetime.now()).days

            if days_left > 30:
                status = "healthy"
                message = f"SSL证书正常，{days_left}天后过期"
            elif days_left > 7:
                status = "warning"
                message = f"SSL证书即将过期，{days_left}天后过期"
            else:
                status = "critical"
                message = f"SSL证书即将过期，{days_left}天后过期"

            return HealthCheckResult(
                component="ssl_certificate",
                status=status,
                message=message,
                details={
                    "subject": dict(x[0] for x in cert["subject"]),
                    "issuer": dict(x[0] for x in cert["issuer"]),
                    "not_after": cert["notAfter"],
                    "days_left": days_left,
                },
            )

        except Exception as e:
            return HealthCheckResult(component="ssl_certificate", status="warning", message=f"SSL证书检查失败: {str(e)}")

    def check_external_apis(self) -> List[HealthCheckResult]:
        """检查外部API连接"""
        results = []

        # 检查的外部API列表
        external_apis = [
            ("百度API", "https://www.baidu.com"),
            # 可以添加更多外部API
        ]

        for name, url in external_apis:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    results.append(
                        HealthCheckResult(
                            component=f"external_api_{name.lower()}",
                            status="healthy",
                            message=f"{name}连接正常",
                            response_time=response_time,
                        )
                    )
                else:
                    results.append(
                        HealthCheckResult(
                            component=f"external_api_{name.lower()}",
                            status="warning",
                            message=f"{name}响应异常: {response.status_code}",
                        )
                    )

            except Exception as e:
                results.append(
                    HealthCheckResult(
                        component=f"external_api_{name.lower()}", status="warning", message=f"{name}连接失败: {str(e)}"
                    )
                )

        return results

    def bytes_to_human(self, bytes_value) -> str:
        """字节转换为人类可读格式"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f}PB"

    def get_summary(self) -> Dict:
        """获取健康检查摘要"""
        if not self.results:
            return {}

        summary = {
            "total": len(self.results),
            "healthy": len([r for r in self.results if r.status == "healthy"]),
            "warning": len([r for r in self.results if r.status == "warning"]),
            "critical": len([r for r in self.results if r.status == "critical"]),
        }

        if summary["critical"] > 0:
            summary["overall_status"] = "critical"
        elif summary["warning"] > 0:
            summary["overall_status"] = "warning"
        else:
            summary["overall_status"] = "healthy"

        return summary

    def save_results(self, filename: str = None):
        """保存检查结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_check_{timestamp}.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "results": [asdict(result) for result in self.results],
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return filename


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="QAToolBox 健康检查")
    parser.add_argument("--output", "-o", help="输出文件名")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")

    args = parser.parse_args()

    # 执行健康检查
    checker = HealthChecker()
    results = checker.check_all()
    summary = checker.get_summary()

    # 输出结果
    if args.json:
        output_data = {"summary": summary, "results": [asdict(result) for result in results]}
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    elif not args.quiet:
        print("=" * 60)
        print("QAToolBox 系统健康检查报告")
        print("=" * 60)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总体状态: {summary['overall_status'].upper()}")
        print(
            f"检查项目: {summary['total']} (健康: {summary['healthy']}, 警告: {summary['warning']}, 严重: {summary['critical']})"
        )
        print()

        for result in results:
            status_icon = {"healthy": "✅", "warning": "⚠️", "critical": "❌"}

            print(f"{status_icon.get(result.status, '❓')} {result.component}: {result.message}")
            if result.response_time:
                print(f"   响应时间: {result.response_time:.3f}s")
            if result.details:
                for key, value in result.details.items():
                    print(f"   {key}: {value}")
            print()

    # 保存结果
    if args.output:
        filename = checker.save_results(args.output)
        if not args.quiet:
            print(f"结果已保存到: {filename}")

    # 根据健康状态设置退出码
    if summary["overall_status"] == "critical":
        sys.exit(1)
    elif summary["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
