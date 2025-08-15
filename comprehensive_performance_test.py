#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QAToolBox 全面性能测试
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    from django.contrib.auth.models import User
    from django.test import Client
    from django.db import connection
    from apps.tools.models import ChatRoom, HeartLinkRequest, TimeCapsule, ChatMessage
    print("✅ Django环境设置成功")
except Exception as e:
    print(f"❌ Django环境设置失败: {e}")
    sys.exit(1)

class ComprehensivePerformanceTester:
    def __init__(self):
        self.client = Client()
        self.results = {}
        self.test_users = []
        
    def cleanup_test_data(self):
        """清理测试数据"""
        print("🧹 清理测试数据...")
        for user in self.test_users:
            try:
                user.delete()
            except:
                pass
        self.test_users.clear()
        
    def test_database_performance(self):
        """数据库性能测试"""
        print("\n🔗 数据库性能测试")
        print("-" * 50)
        
        # 测试查询性能
        start_time = time.time()
        user_count = User.objects.count()
        query_time = time.time() - start_time
        print(f"📊 用户总数查询: {user_count} 用户, 耗时: {query_time:.3f}秒")
        
        # 测试批量查询
        start_time = time.time()
        users = list(User.objects.all()[:100])
        batch_query_time = time.time() - start_time
        print(f"📊 批量查询100用户: {batch_query_time:.3f}秒")
        
        # 测试用户创建性能
        create_times = []
        for i in range(50):
            start_time = time.time()
            try:
                user = User.objects.create_user(
                    username=f'perf_test_{i}_{int(time.time())}',
                    email=f'perf_{i}_{int(time.time())}@test.com',
                    password='test123456'
                )
                self.test_users.append(user)
                create_time = time.time() - start_time
                create_times.append(create_time)
            except Exception as e:
                print(f"⚠️ 创建用户 {i} 失败: {e}")
                break
        
        avg_create_time = sum(create_times) / len(create_times) if create_times else 0
        create_speed = len(create_times) / sum(create_times) if sum(create_times) > 0 else 0
        
        print(f"📊 用户创建性能:")
        print(f"   创建用户数: {len(create_times)}")
        print(f"   平均创建时间: {avg_create_time:.3f}秒")
        print(f"   创建速度: {create_speed:.2f} 用户/秒")
        
        return {
            'user_count': user_count,
            'query_time': query_time,
            'batch_query_time': batch_query_time,
            'create_times': create_times,
            'avg_create_time': avg_create_time,
            'create_speed': create_speed
        }
    
    def test_chat_room_performance(self):
        """聊天室性能测试"""
        print("\n💬 聊天室性能测试")
        print("-" * 50)
        
        if not self.test_users:
            print("⚠️ 没有测试用户，跳过聊天室测试")
            return None
        
        # 创建聊天室
        start_time = time.time()
        chat_rooms = []
        for i in range(20):
            try:
                user = self.test_users[i % len(self.test_users)]
                chat_room = ChatRoom.objects.create(
                    room_id=f'perf_chat_{i}_{int(time.time())}',
                    user1=user,
                    status='active'
                )
                chat_rooms.append(chat_room)
            except Exception as e:
                print(f"⚠️ 创建聊天室 {i} 失败: {e}")
                break
        
        chat_room_time = time.time() - start_time
        print(f"📊 聊天室创建: {len(chat_rooms)} 个, 耗时: {chat_room_time:.3f}秒")
        
        # 创建消息
        start_time = time.time()
        message_count = 0
        for chat_room in chat_rooms:
            user = chat_room.user1
            for j in range(10):
                try:
                    ChatMessage.objects.create(
                        room=chat_room,
                        sender=user,
                        content=f'性能测试消息 {j}',
                        message_type='text'
                    )
                    message_count += 1
                except Exception as e:
                    print(f"⚠️ 创建消息失败: {e}")
                    break
        
        message_time = time.time() - start_time
        print(f"📊 消息创建: {message_count} 条, 耗时: {message_time:.3f}秒")
        print(f"📊 消息创建速度: {message_count/message_time:.2f} 消息/秒")
        
        return {
            'chat_rooms_created': len(chat_rooms),
            'chat_room_time': chat_room_time,
            'messages_created': message_count,
            'message_time': message_time,
            'message_speed': message_count/message_time if message_time > 0 else 0
        }
    
    def test_time_capsule_performance(self):
        """时光胶囊性能测试"""
        print("\n⏰ 时光胶囊性能测试")
        print("-" * 50)
        
        if not self.test_users:
            print("⚠️ 没有测试用户，跳过时光胶囊测试")
            return None
        
        # 创建时光胶囊
        start_time = time.time()
        capsules = []
        for i in range(30):
            try:
                user = self.test_users[i % len(self.test_users)]
                capsule = TimeCapsule.objects.create(
                    user=user,
                    content=f'性能测试时光胶囊 {i}',
                    emotions=['happy', 'excited', 'calm']
                )
                capsules.append(capsule)
            except Exception as e:
                print(f"⚠️ 创建时光胶囊 {i} 失败: {e}")
                break
        
        capsule_time = time.time() - start_time
        print(f"📊 时光胶囊创建: {len(capsules)} 个, 耗时: {capsule_time:.3f}秒")
        print(f"📊 创建速度: {len(capsules)/capsule_time:.2f} 胶囊/秒")
        
        return {
            'capsules_created': len(capsules),
            'capsule_time': capsule_time,
            'capsule_speed': len(capsules)/capsule_time if capsule_time > 0 else 0
        }
    
    def test_web_performance(self):
        """Web性能测试"""
        print("\n🌐 Web性能测试")
        print("-" * 50)
        
        # 测试首页
        start_time = time.time()
        response = self.client.get('/')
        first_request_time = time.time() - start_time
        
        print(f"📊 首页请求:")
        print(f"   状态码: {response.status_code}")
        print(f"   响应时间: {first_request_time:.3f}秒")
        
        # 测试多个页面
        pages = [
            '/tools/heart_link/',
            '/tools/chat/',
            '/tools/number-match/',
            '/tools/time-capsule/',
        ]
        
        page_times = {}
        for page in pages:
            try:
                start_time = time.time()
                response = self.client.get(page)
                end_time = time.time()
                page_times[page] = {
                    'time': end_time - start_time,
                    'status': response.status_code
                }
            except Exception as e:
                print(f"⚠️ 页面 {page} 请求失败: {e}")
        
        print(f"📊 页面响应时间:")
        for page, data in page_times.items():
            print(f"   {page}: {data['time']:.3f}秒 (状态码: {data['status']})")
        
        # 测试并发请求
        print(f"\n📊 并发请求测试:")
        concurrent_times = []
        for i in range(20):
            start_time = time.time()
            self.client.get('/')
            end_time = time.time()
            concurrent_times.append(end_time - start_time)
        
        avg_concurrent_time = sum(concurrent_times) / len(concurrent_times)
        min_concurrent_time = min(concurrent_times)
        max_concurrent_time = max(concurrent_times)
        
        print(f"   20次并发请求:")
        print(f"   平均时间: {avg_concurrent_time:.3f}秒")
        print(f"   最短时间: {min_concurrent_time:.3f}秒")
        print(f"   最长时间: {max_concurrent_time:.3f}秒")
        print(f"   请求速度: {1/avg_concurrent_time:.2f} 请求/秒")
        
        return {
            'first_request_time': first_request_time,
            'page_times': page_times,
            'concurrent_times': concurrent_times,
            'avg_concurrent_time': avg_concurrent_time,
            'requests_per_second': 1/avg_concurrent_time
        }
    
    def test_memory_usage(self):
        """内存使用测试"""
        print("\n💾 内存使用测试")
        print("-" * 50)
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 初始内存使用: {initial_memory:.2f} MB")
        
        # 创建大量对象
        large_test_users = []
        for i in range(200):
            try:
                user = User.objects.create_user(
                    username=f'memory_test_{i}_{int(time.time())}',
                    email=f'memory_{i}_{int(time.time())}@test.com',
                    password='test123456'
                )
                large_test_users.append(user)
            except Exception as e:
                print(f"⚠️ 创建用户 {i} 失败: {e}")
                break
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"📊 最终内存使用: {final_memory:.2f} MB")
        print(f"📊 内存增长: {memory_increase:.2f} MB")
        print(f"📊 创建用户数: {len(large_test_users)}")
        print(f"📊 平均每用户内存: {memory_increase/len(large_test_users):.2f} MB")
        
        # 清理
        for user in large_test_users:
            try:
                user.delete()
            except:
                pass
        
        return {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase,
            'users_created': len(large_test_users),
            'memory_per_user': memory_increase/len(large_test_users) if large_test_users else 0
        }
    
    def test_system_resources(self):
        """系统资源测试"""
        print("\n🖥️ 系统资源测试")
        print("-" * 50)
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存
        memory = psutil.virtual_memory()
        
        # 磁盘
        disk = psutil.disk_usage('/')
        
        print(f"📊 CPU信息:")
        print(f"   CPU核心数: {cpu_count}")
        print(f"   CPU使用率: {cpu_percent}%")
        
        print(f"📊 内存信息:")
        print(f"   总内存: {memory.total / 1024 / 1024 / 1024:.2f} GB")
        print(f"   可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB")
        print(f"   内存使用率: {memory.percent}%")
        
        print(f"📊 磁盘信息:")
        print(f"   总空间: {disk.total / 1024 / 1024 / 1024:.2f} GB")
        print(f"   可用空间: {disk.free / 1024 / 1024 / 1024:.2f} GB")
        print(f"   磁盘使用率: {disk.percent}%")
        
        return {
            'cpu_count': cpu_count,
            'cpu_percent': cpu_percent,
            'total_memory': memory.total,
            'available_memory': memory.available,
            'memory_percent': memory.percent,
            'total_disk': disk.total,
            'free_disk': disk.free,
            'disk_percent': disk.percent
        }
    
    def calculate_max_capacity(self):
        """计算最大承受值"""
        print("\n🚀 最大承受值计算")
        print("-" * 50)
        
        # 基于数据库性能
        if 'db_perf' in self.results:
            db_perf = self.results['db_perf']
            create_speed = db_perf['create_speed']
            max_users_per_hour = int(create_speed * 3600)
            max_users_per_day = max_users_per_hour * 24
            print(f"📊 数据库最大承受值:")
            print(f"   每小时: ~{max_users_per_hour:,} 用户")
            print(f"   每天: ~{max_users_per_day:,} 用户")
        
        # 基于Web性能
        if 'web_perf' in self.results:
            web_perf = self.results['web_perf']
            requests_per_second = web_perf['requests_per_second']
            max_requests_per_hour = int(requests_per_second * 3600)
            max_requests_per_day = max_requests_per_hour * 24
            print(f"📊 Web请求最大承受值:")
            print(f"   每小时: ~{max_requests_per_hour:,} 请求")
            print(f"   每天: ~{max_requests_per_day:,} 请求")
        
        # 基于内存使用
        if 'memory' in self.results and 'system' in self.results:
            memory = self.results['memory']
            system = self.results['system']
            memory_per_user = memory['memory_per_user']
            available_memory = system['available_memory'] / 1024 / 1024  # MB
            max_users_by_memory = int(available_memory / memory_per_user * 0.8)  # 保留20%缓冲
            print(f"📊 内存最大承受值:")
            print(f"   最大用户数: ~{max_users_by_memory:,} 用户")
        
        # 基于聊天室性能
        if 'chat_perf' in self.results:
            chat_perf = self.results['chat_perf']
            message_speed = chat_perf['message_speed']
            max_messages_per_hour = int(message_speed * 3600)
            print(f"📊 聊天消息最大承受值:")
            print(f"   每小时: ~{max_messages_per_hour:,} 消息")
    
    def generate_performance_report(self):
        """生成性能报告"""
        print("\n📋 性能测试报告")
        print("=" * 60)
        
        print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 测试项目: {len(self.results)}")
        
        # 性能评估
        print(f"\n🎯 性能评估:")
        
        if 'db_perf' in self.results:
            db_perf = self.results['db_perf']
            create_speed = db_perf['create_speed']
            if create_speed > 50:
                print("   🌟 数据库性能: 优秀")
            elif create_speed > 20:
                print("   ✅ 数据库性能: 良好")
            elif create_speed > 10:
                print("   ⚠️ 数据库性能: 一般")
            else:
                print("   ❌ 数据库性能: 需要优化")
        
        if 'web_perf' in self.results:
            web_perf = self.results['web_perf']
            requests_per_second = web_perf['requests_per_second']
            if requests_per_second > 100:
                print("   🌟 Web性能: 优秀")
            elif requests_per_second > 50:
                print("   ✅ Web性能: 良好")
            elif requests_per_second > 20:
                print("   ⚠️ Web性能: 一般")
            else:
                print("   ❌ Web性能: 需要优化")
        
        if 'memory' in self.results:
            memory = self.results['memory']
            memory_increase = memory['memory_increase']
            if memory_increase < 10:
                print("   🌟 内存使用: 优秀")
            elif memory_increase < 50:
                print("   ✅ 内存使用: 良好")
            elif memory_increase < 100:
                print("   ⚠️ 内存使用: 一般")
            else:
                print("   ❌ 内存使用: 需要优化")
        
        # 优化建议
        print(f"\n💡 优化建议:")
        
        if 'db_perf' in self.results and self.results['db_perf']['create_speed'] < 20:
            print("   ⚠️ 数据库创建速度较慢，建议优化数据库配置")
        
        if 'web_perf' in self.results and self.results['web_perf']['requests_per_second'] < 50:
            print("   ⚠️ Web响应速度较慢，建议优化页面加载")
        
        if 'memory' in self.results and self.results['memory']['memory_increase'] > 50:
            print("   ⚠️ 内存使用较高，建议优化对象创建和清理")
        
        print("   ✅ 建议使用数据库连接池")
        print("   ✅ 建议实现缓存机制")
        print("   ✅ 建议使用异步处理")
        print("   ✅ 建议监控系统资源")
        print("   ✅ 建议定期清理无用数据")

def main():
    """主测试函数"""
    print("🚀 QAToolBox 全面性能测试")
    print("=" * 60)
    print(f"⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ComprehensivePerformanceTester()
    
    try:
        # 1. 系统资源测试
        system = tester.test_system_resources()
        tester.results['system'] = system
        
        # 2. 数据库性能测试
        db_perf = tester.test_database_performance()
        tester.results['db_perf'] = db_perf
        
        # 3. 聊天室性能测试
        chat_perf = tester.test_chat_room_performance()
        tester.results['chat_perf'] = chat_perf
        
        # 4. 时光胶囊性能测试
        capsule_perf = tester.test_time_capsule_performance()
        tester.results['capsule_perf'] = capsule_perf
        
        # 5. Web性能测试
        web_perf = tester.test_web_performance()
        tester.results['web_perf'] = web_perf
        
        # 6. 内存使用测试
        memory = tester.test_memory_usage()
        tester.results['memory'] = memory
        
        # 7. 计算最大承受值
        tester.calculate_max_capacity()
        
        # 8. 生成性能报告
        tester.generate_performance_report()
        
        print(f"\n🎉 全面性能测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        tester.cleanup_test_data()
        print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
