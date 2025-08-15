#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QAToolBox 简化性能测试脚本
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    from django.contrib.auth.models import User
    from django.test import Client
    from django.db import connection
    print("✅ Django环境设置成功")
except Exception as e:
    print(f"❌ Django环境设置失败: {e}")
    sys.exit(1)

class SimplePerformanceTester:
    def __init__(self):
        self.client = Client()
        self.results = {}
        
    def test_database_connection(self):
        """测试数据库连接性能"""
        print("\n🔗 数据库连接测试")
        print("-" * 40)
        
        start_time = time.time()
        try:
            # 测试基本查询
            user_count = User.objects.count()
            print(f"✅ 数据库连接正常，用户总数: {user_count}")
            
            # 测试查询性能
            users = list(User.objects.all()[:100])
            query_time = time.time() - start_time
            print(f"✅ 查询100个用户耗时: {query_time:.3f}秒")
            
            return query_time
        except Exception as e:
            print(f"❌ 数据库测试失败: {e}")
            return None

    def test_memory_usage(self):
        """测试内存使用"""
        print("\n💾 内存使用测试")
        print("-" * 40)
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 初始内存使用: {initial_memory:.2f} MB")
        
        # 创建一些测试数据
        test_users = []
        for i in range(100):
            try:
                user = User.objects.create_user(
                    username=f'perf_test_user_{i}',
                    email=f'perf_test_{i}@test.com',
                    password='test123456'
                )
                test_users.append(user)
            except Exception as e:
                print(f"⚠️ 创建用户 {i} 失败: {e}")
                break
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"📊 最终内存使用: {final_memory:.2f} MB")
        print(f"📊 内存增长: {memory_increase:.2f} MB")
        print(f"📊 创建用户数: {len(test_users)}")
        
        # 清理测试数据
        for user in test_users:
            try:
                user.delete()
            except:
                pass
        
        return memory_increase

    def test_concurrent_operations(self, max_threads=10):
        """测试并发操作"""
        print(f"\n🔄 并发操作测试 (最大线程数: {max_threads})")
        print("-" * 40)
        
        def worker(thread_id):
            """工作线程函数"""
            try:
                # 创建用户
                user = User.objects.create_user(
                    username=f'concurrent_user_{thread_id}',
                    email=f'concurrent_{thread_id}@test.com',
                    password='test123456'
                )
                
                # 模拟一些操作
                time.sleep(0.1)
                
                # 清理
                user.delete()
                return True
            except Exception as e:
                print(f"❌ 线程 {thread_id} 失败: {e}")
                return False
        
        start_time = time.time()
        success_count = 0
        
        threads = []
        for i in range(max_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        print(f"✅ 并发测试完成")
        print(f"📊 总耗时: {total_time:.3f}秒")
        print(f"📊 平均每线程: {total_time/max_threads:.3f}秒")
        
        return total_time

    def test_system_resources(self):
        """测试系统资源"""
        print("\n🖥️ 系统资源测试")
        print("-" * 40)
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"📊 CPU使用率: {cpu_percent}%")
        
        # 内存使用率
        memory = psutil.virtual_memory()
        print(f"📊 内存使用率: {memory.percent}%")
        print(f"📊 可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB")
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        print(f"📊 磁盘使用率: {disk.percent}%")
        print(f"📊 可用磁盘空间: {disk.free / 1024 / 1024 / 1024:.2f} GB")
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent
        }

    def test_web_requests(self):
        """测试Web请求性能"""
        print("\n🌐 Web请求性能测试")
        print("-" * 40)
        
        try:
            # 测试首页请求
            start_time = time.time()
            response = self.client.get('/')
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"✅ 首页请求成功")
            print(f"📊 响应时间: {response_time:.3f}秒")
            print(f"📊 状态码: {response.status_code}")
            
            # 测试多个请求
            times = []
            for i in range(10):
                start = time.time()
                self.client.get('/')
                end = time.time()
                times.append(end - start)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"📊 10次请求统计:")
            print(f"   平均时间: {avg_time:.3f}秒")
            print(f"   最短时间: {min_time:.3f}秒")
            print(f"   最长时间: {max_time:.3f}秒")
            
            return {
                'avg': avg_time,
                'min': min_time,
                'max': max_time
            }
            
        except Exception as e:
            print(f"❌ Web请求测试失败: {e}")
            return None

    def generate_report(self):
        """生成测试报告"""
        print("\n📋 性能测试报告")
        print("=" * 60)
        
        print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 测试项目: {len(self.results)}")
        
        # 性能评估
        print(f"\n🎯 性能评估:")
        
        if 'web_response' in self.results:
            avg_time = self.results['web_response']['avg']
            if avg_time < 0.1:
                print("   🌟 Web响应性能: 优秀")
            elif avg_time < 0.3:
                print("   ✅ Web响应性能: 良好")
            elif avg_time < 0.5:
                print("   ⚠️ Web响应性能: 一般")
            else:
                print("   ❌ Web响应性能: 需要优化")
        
        if 'memory_increase' in self.results:
            memory_increase = self.results['memory_increase']
            if memory_increase < 10:
                print("   🌟 内存使用: 优秀")
            elif memory_increase < 50:
                print("   ✅ 内存使用: 良好")
            elif memory_increase < 100:
                print("   ⚠️ 内存使用: 一般")
            else:
                print("   ❌ 内存使用: 需要优化")
        
        print(f"\n💡 优化建议:")
        print("   ✅ 定期监控系统资源使用")
        print("   ✅ 优化数据库查询")
        print("   ✅ 使用缓存机制")
        print("   ✅ 考虑负载均衡")
        print("   ✅ 定期清理无用数据")

def main():
    """主测试函数"""
    print("🚀 QAToolBox 简化性能测试")
    print("=" * 60)
    
    tester = SimplePerformanceTester()
    
    try:
        # 1. 数据库连接测试
        db_time = tester.test_database_connection()
        tester.results['db_query'] = db_time
        
        # 2. 内存使用测试
        memory_increase = tester.test_memory_usage()
        tester.results['memory_increase'] = memory_increase
        
        # 3. 并发操作测试
        concurrent_time = tester.test_concurrent_operations(max_threads=5)
        tester.results['concurrent_time'] = concurrent_time
        
        # 4. 系统资源测试
        system_resources = tester.test_system_resources()
        tester.results['system_resources'] = system_resources
        
        # 5. Web请求测试
        web_performance = tester.test_web_requests()
        tester.results['web_response'] = web_performance
        
        # 6. 生成报告
        tester.generate_report()
        
        print(f"\n🎉 性能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
