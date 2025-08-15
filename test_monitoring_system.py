#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控系统测试脚本
测试监控服务的各项功能
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

from django.test import Client
from django.contrib.auth.models import User
from apps.tools.services.monitoring_service import (
    monitoring_service, SystemMonitor, DatabaseMonitor, 
    CacheMonitor, ApplicationMonitor, PerformanceMonitor
)
from apps.tools.services.cache_service import CacheManager


class MonitoringSystemTester:
    """监控系统测试器"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = {}
    
    def test_system_monitor(self):
        """测试系统监控器"""
        print("🔍 测试系统监控器...")
        
        try:
            monitor = SystemMonitor()
            metrics = monitor.get_system_metrics()
            alerts = monitor.check_alerts()
            
            self.test_results['system_monitor'] = {
                'success': True,
                'metrics': metrics,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 系统监控器测试成功")
            print(f"   CPU使用率: {metrics.get('cpu', {}).get('percent', 0):.1f}%")
            print(f"   内存使用率: {metrics.get('memory', {}).get('percent', 0):.1f}%")
            print(f"   磁盘使用率: {metrics.get('disk', {}).get('percent', 0):.1f}%")
            print(f"   告警数量: {len(alerts)}")
            
        except Exception as e:
            self.test_results['system_monitor'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 系统监控器测试失败: {e}")
    
    def test_database_monitor(self):
        """测试数据库监控器"""
        print("🗄️ 测试数据库监控器...")
        
        try:
            monitor = DatabaseMonitor()
            stats = monitor.get_connection_stats()
            alerts = monitor.check_database_alerts()
            
            self.test_results['database_monitor'] = {
                'success': True,
                'stats': stats,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 数据库监控器测试成功")
            print(f"   活跃连接数: {stats.get('active_connections', 0)}")
            print(f"   慢查询数量: {len(stats.get('slow_queries', []))}")
            print(f"   告警数量: {len(alerts)}")
            
        except Exception as e:
            self.test_results['database_monitor'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 数据库监控器测试失败: {e}")
    
    def test_cache_monitor(self):
        """测试缓存监控器"""
        print("💾 测试缓存监控器...")
        
        try:
            monitor = CacheMonitor()
            stats = monitor.get_cache_stats()
            alerts = monitor.check_cache_alerts()
            
            self.test_results['cache_monitor'] = {
                'success': True,
                'stats': stats,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 缓存监控器测试成功")
            if 'hit_rate' in stats:
                print(f"   命中率: {stats['hit_rate']:.2%}")
            if 'used_memory' in stats:
                print(f"   内存使用: {stats['used_memory'] / 1024 / 1024:.2f}MB")
            print(f"   告警数量: {len(alerts)}")
            
        except Exception as e:
            self.test_results['cache_monitor'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 缓存监控器测试失败: {e}")
    
    def test_application_monitor(self):
        """测试应用监控器"""
        print("📱 测试应用监控器...")
        
        try:
            monitor = ApplicationMonitor()
            stats = monitor.get_application_stats()
            alerts = monitor.check_application_alerts()
            
            self.test_results['application_monitor'] = {
                'success': True,
                'stats': stats,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 应用监控器测试成功")
            print(f"   总用户数: {stats.get('total_users', 0)}")
            print(f"   今日活跃用户: {stats.get('active_users_today', 0)}")
            print(f"   活跃聊天室: {stats.get('active_chat_rooms', 0)}")
            print(f"   今日消息数: {stats.get('messages_today', 0)}")
            print(f"   告警数量: {len(alerts)}")
            
        except Exception as e:
            self.test_results['application_monitor'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 应用监控器测试失败: {e}")
    
    def test_performance_monitor(self):
        """测试性能监控器"""
        print("⚡ 测试性能监控器...")
        
        try:
            monitor = PerformanceMonitor()
            
            # 模拟一些请求
            endpoints = ['/tools/', '/tools/heart_link/', '/tools/chat_enhanced/']
            for endpoint in endpoints:
                for i in range(5):
                    response_time = 0.1 + (i * 0.05)  # 模拟不同的响应时间
                    monitor.record_response_time(endpoint, response_time)
                    time.sleep(0.01)
            
            metrics = monitor.get_performance_metrics()
            alerts = monitor.check_performance_alerts()
            
            self.test_results['performance_monitor'] = {
                'success': True,
                'metrics': metrics,
                'alerts': alerts,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 性能监控器测试成功")
            print(f"   监控端点数量: {len(metrics)}")
            print(f"   告警数量: {len(alerts)}")
            
        except Exception as e:
            self.test_results['performance_monitor'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 性能监控器测试失败: {e}")
    
    def test_monitoring_service(self):
        """测试监控服务主类"""
        print("🎯 测试监控服务主类...")
        
        try:
            # 测试收集所有指标
            metrics = monitoring_service.collect_all_metrics()
            
            # 测试检查所有告警
            alerts = monitoring_service.check_all_alerts()
            
            # 测试获取仪表板数据
            dashboard_data = monitoring_service.get_dashboard_data()
            
            self.test_results['monitoring_service'] = {
                'success': True,
                'metrics': metrics,
                'alerts': alerts,
                'dashboard_data': dashboard_data,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 监控服务主类测试成功")
            print(f"   健康评分: {dashboard_data.get('health_score', 0)}")
            print(f"   告警总数: {len(alerts)}")
            print(f"   指标模块数: {len(metrics)}")
            
        except Exception as e:
            self.test_results['monitoring_service'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 监控服务主类测试失败: {e}")
    
    def test_cache_manager(self):
        """测试缓存管理器"""
        print("🔧 测试缓存管理器...")
        
        try:
            # 测试缓存统计
            stats = CacheManager.get_cache_stats()
            
            # 测试缓存操作
            test_key = 'test_monitoring_key'
            test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
            
            # 设置缓存
            from django.core.cache import cache
            cache.set(test_key, test_data, timeout=60)
            
            # 获取缓存
            retrieved_data = cache.get(test_key)
            
            # 删除缓存
            cache.delete(test_key)
            
            self.test_results['cache_manager'] = {
                'success': True,
                'stats': stats,
                'test_data': test_data,
                'retrieved_data': retrieved_data,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ 缓存管理器测试成功")
            print(f"   缓存统计: {len(stats)} 项")
            print(f"   测试数据设置: {'成功' if retrieved_data == test_data else '失败'}")
            
        except Exception as e:
            self.test_results['cache_manager'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ 缓存管理器测试失败: {e}")
    
    def test_web_requests(self):
        """测试Web请求"""
        print("🌐 测试Web请求...")
        
        try:
            # 创建测试用户
            test_user, created = User.objects.get_or_create(
                username='test_monitoring_user',
                defaults={'email': 'test@example.com'}
            )
            if created:
                test_user.set_password('testpass123')
                test_user.is_staff = True
                test_user.save()
            
            # 登录
            self.client.login(username='test_monitoring_user', password='testpass123')
            
            # 测试监控页面
            response = self.client.get('/tools/monitoring/')
            
            # 测试监控API
            api_response = self.client.get('/tools/monitoring/data/')
            
            self.test_results['web_requests'] = {
                'success': True,
                'monitoring_page_status': response.status_code,
                'api_status': api_response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"✅ Web请求测试成功")
            print(f"   监控页面状态: {response.status_code}")
            print(f"   监控API状态: {api_response.status_code}")
            
            # 清理测试用户
            test_user.delete()
            
        except Exception as e:
            self.test_results['web_requests'] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"❌ Web请求测试失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始监控系统测试...")
        print("=" * 50)
        
        self.test_system_monitor()
        print()
        
        self.test_database_monitor()
        print()
        
        self.test_cache_monitor()
        print()
        
        self.test_application_monitor()
        print()
        
        self.test_performance_monitor()
        print()
        
        self.test_monitoring_service()
        print()
        
        self.test_cache_manager()
        print()
        
        self.test_web_requests()
        print()
        
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("📊 生成测试报告...")
        print("=" * 50)
        
        # 计算成功率
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"📈 测试结果总览:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功测试: {successful_tests}")
        print(f"   失败测试: {total_tests - successful_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        print()
        
        # 详细结果
        print("📋 详细测试结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 成功" if result.get('success', False) else "❌ 失败"
            print(f"   {test_name}: {status}")
            if not result.get('success', False):
                print(f"      错误: {result.get('error', '未知错误')}")
        
        print()
        
        # 保存报告
        report_file = f"monitoring_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 测试报告已保存到: {report_file}")
        
        # 返回测试结果
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }


def main():
    """主函数"""
    print("🔧 QAToolBox 监控系统测试")
    print("=" * 50)
    
    tester = MonitoringSystemTester()
    results = tester.run_all_tests()
    
    print("🎉 测试完成!")
    print(f"总体成功率: {results['success_rate']:.1f}%")
    
    if results['success_rate'] >= 80:
        print("✅ 监控系统运行良好!")
    elif results['success_rate'] >= 60:
        print("⚠️ 监控系统基本可用，但需要优化")
    else:
        print("❌ 监控系统存在问题，需要修复")


if __name__ == '__main__':
    main()
