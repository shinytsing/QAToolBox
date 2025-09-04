#!/usr/bin/env python3
"""
代理池管理命令
"""

import json

from django.core.management.base import BaseCommand

from apps.tools.services.proxy_pool import proxy_pool


class Command(BaseCommand):
    help = "管理虚拟IP代理池"

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["status", "refresh", "test", "clear", "add"], help="执行的操作")
        parser.add_argument("--proxy", type=str, help="添加代理时指定代理地址 (格式: ip:port)")
        parser.add_argument("--count", type=int, default=10, help="测试代理数量")

    def handle(self, *args, **options):
        action = options["action"]

        if action == "status":
            self.show_status()
        elif action == "refresh":
            self.refresh_proxies()
        elif action == "test":
            self.test_proxies(options["count"])
        elif action == "clear":
            self.clear_failed_proxies()
        elif action == "add":
            self.add_proxy(options["proxy"])

    def show_status(self):
        """显示代理池状态"""
        stats = proxy_pool.get_stats()

        self.stdout.write(self.style.SUCCESS("🔍 代理池状态"))
        self.stdout.write(f"总代理数: {stats['total_proxies']}")
        self.stdout.write(f"可用代理数: {stats['working_proxies']}")
        self.stdout.write(f"失败代理数: {stats['failed_proxies']}")
        self.stdout.write(f"成功率: {stats['success_rate']:.1f}%")
        self.stdout.write(f"平均响应时间: {stats['avg_response_time']:.2f}秒")
        self.stdout.write(f"最后更新: {stats['last_update'] or '从未更新'}")

        # 显示前5个最佳代理
        available_proxies = [p for p in proxy_pool.proxies if p.proxy not in proxy_pool.failed_proxies and p.fail_count < 3]

        if available_proxies:
            available_proxies.sort(key=lambda x: (x.fail_count, x.response_time if x.response_time > 0 else 999))
            self.stdout.write(self.style.SUCCESS("\n🏆 前5个最佳代理:"))
            for i, proxy in enumerate(available_proxies[:5], 1):
                response_time = proxy.response_time or 0
                success_count = proxy.success_count or 0
                fail_count = proxy.fail_count or 0
                self.stdout.write(
                    f"{i}. {proxy.proxy} " f"(响应: {response_time:.2f}s, 成功: {success_count}, 失败: {fail_count})"
                )

    def refresh_proxies(self):
        """刷新代理池"""
        self.stdout.write(self.style.WARNING("🔄 正在刷新代理池..."))

        old_count = len(proxy_pool.proxies)
        proxy_pool._fetch_fresh_proxies()
        new_count = len(proxy_pool.proxies)

        self.stdout.write(self.style.SUCCESS(f"✅ 代理池刷新完成! 从 {old_count} 个更新到 {new_count} 个代理"))

    def test_proxies(self, count):
        """测试代理"""
        self.stdout.write(self.style.WARNING(f"🧪 正在测试前 {count} 个代理..."))

        test_proxies = proxy_pool.proxies[:count]
        working_count = 0

        for i, proxy_info in enumerate(test_proxies, 1):
            self.stdout.write(f"测试 {i}/{len(test_proxies)}: {proxy_info.proxy}")

            if proxy_pool._test_proxy(proxy_info):
                working_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ 可用 ({proxy_info.response_time or 0:.2f}s)"))
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ 失败"))

        success_rate = (working_count / len(test_proxies)) * 100 if test_proxies else 0
        self.stdout.write(self.style.SUCCESS(f"\n🎯 测试完成: {working_count}/{len(test_proxies)} 可用 ({success_rate:.1f}%)"))

    def clear_failed_proxies(self):
        """清理失败的代理"""
        failed_count = len(proxy_pool.failed_proxies)
        proxy_pool.failed_proxies.clear()

        # 重置失败计数
        for proxy_info in proxy_pool.proxies:
            proxy_info.fail_count = 0

        proxy_pool._save_proxies()

        self.stdout.write(self.style.SUCCESS(f"🧹 已清理 {failed_count} 个失败代理记录"))

    def add_proxy(self, proxy_address):
        """添加新代理"""
        if not proxy_address:
            self.stdout.write(self.style.ERROR("❌ 请使用 --proxy 参数指定代理地址"))
            return

        if ":" not in proxy_address:
            self.stdout.write(self.style.ERROR("❌ 代理格式错误，应为 ip:port"))
            return

        try:
            ip, port = proxy_address.split(":")
            if not (ip and port.isdigit()):
                raise ValueError("格式错误")
        except ValueError:
            self.stdout.write(self.style.ERROR("❌ 代理格式错误，应为 ip:port"))
            return

        # 检查是否已存在
        existing = any(p.proxy == proxy_address for p in proxy_pool.proxies)
        if existing:
            self.stdout.write(self.style.WARNING(f"⚠️ 代理 {proxy_address} 已存在"))
            return

        # 添加新代理
        from apps.tools.services.proxy_pool import ProxyInfo

        new_proxy = ProxyInfo(
            proxy=proxy_address,
            protocol="http",
            country="manual",
            anonymity="unknown",
            last_checked=None,
            success_count=0,
            fail_count=0,
            response_time=0,
            source="manual",
        )

        proxy_pool.proxies.append(new_proxy)
        proxy_pool._save_proxies()

        self.stdout.write(self.style.SUCCESS(f"✅ 已添加代理: {proxy_address}"))

        # 测试新添加的代理
        self.stdout.write("🧪 正在测试新代理...")
        if proxy_pool._test_proxy(new_proxy):
            self.stdout.write(self.style.SUCCESS(f"✅ 新代理测试成功!"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️ 新代理测试失败，但已添加到池中"))
