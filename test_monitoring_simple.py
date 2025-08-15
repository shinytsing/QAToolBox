#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化监控系统测试
"""

import os
import sys
import django
import time
import json
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.monitoring_service import monitoring_service


def test_monitoring_service():
    """测试监控服务"""
    print("🔧 测试监控服务...")
    
    try:
        # 测试收集所有指标
        metrics = monitoring_service.collect_all_metrics()
        print(f"✅ 指标收集成功: {len(metrics)} 个模块")
        
        # 测试检查告警
        alerts = monitoring_service.check_all_alerts()
        print(f"✅ 告警检查成功: {len(alerts)} 个告警")
        
        # 测试获取仪表板数据
        dashboard_data = monitoring_service.get_dashboard_data()
        print(f"✅ 仪表板数据获取成功")
        print(f"   健康评分: {dashboard_data.get('health_score', 0)}")
        print(f"   告警总数: {len(alerts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 监控服务测试失败: {e}")
        return False


def test_system_monitor():
    """测试系统监控器"""
    print("🔍 测试系统监控器...")
    
    try:
        from apps.tools.services.monitoring_service import SystemMonitor
        
        monitor = SystemMonitor()
        metrics = monitor.get_system_metrics()
        alerts = monitor.check_alerts()
        
        print(f"✅ 系统监控器测试成功")
        print(f"   CPU使用率: {metrics.get('cpu', {}).get('percent', 0):.1f}%")
        print(f"   内存使用率: {metrics.get('memory', {}).get('percent', 0):.1f}%")
        print(f"   磁盘使用率: {metrics.get('disk', {}).get('percent', 0):.1f}%")
        print(f"   告警数量: {len(alerts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统监控器测试失败: {e}")
        return False


def test_cache_monitor():
    """测试缓存监控器"""
    print("💾 测试缓存监控器...")
    
    try:
        from apps.tools.services.monitoring_service import CacheMonitor
        
        monitor = CacheMonitor()
        stats = monitor.get_cache_stats()
        alerts = monitor.check_cache_alerts()
        
        print(f"✅ 缓存监控器测试成功")
        print(f"   告警数量: {len(alerts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存监控器测试失败: {e}")
        return False


def test_application_monitor():
    """测试应用监控器"""
    print("📱 测试应用监控器...")
    
    try:
        from apps.tools.services.monitoring_service import ApplicationMonitor
        
        monitor = ApplicationMonitor()
        stats = monitor.get_application_stats()
        alerts = monitor.check_application_alerts()
        
        print(f"✅ 应用监控器测试成功")
        print(f"   总用户数: {stats.get('total_users', 0)}")
        print(f"   今日活跃用户: {stats.get('active_users_today', 0)}")
        print(f"   活跃聊天室: {stats.get('active_chat_rooms', 0)}")
        print(f"   今日消息数: {stats.get('messages_today', 0)}")
        print(f"   告警数量: {len(alerts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用监控器测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🔧 QAToolBox 监控系统简化测试")
    print("=" * 50)
    
    tests = [
        test_monitoring_service,
        test_system_monitor,
        test_cache_monitor,
        test_application_monitor,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    success_count = sum(results)
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print("📊 测试结果总览:")
    print(f"   总测试数: {total_count}")
    print(f"   成功测试: {success_count}")
    print(f"   失败测试: {total_count - success_count}")
    print(f"   成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ 监控系统运行良好!")
    elif success_rate >= 60:
        print("⚠️ 监控系统基本可用，但需要优化")
    else:
        print("❌ 监控系统存在问题，需要修复")


if __name__ == '__main__':
    main()
