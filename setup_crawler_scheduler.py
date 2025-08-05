#!/usr/bin/env python3
"""
设置社交媒体爬虫定时任务
"""

import os
import sys
import django
import subprocess
import time
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import SocialMediaSubscription

def run_crawler_task():
    """运行爬虫任务"""
    try:
        print(f"[{datetime.now()}] 开始运行爬虫任务...")
        
        # 获取所有活跃的订阅
        active_subscriptions = SocialMediaSubscription.objects.filter(status='active')
        print(f"找到 {active_subscriptions.count()} 个活跃订阅")
        
        # 运行爬虫命令
        result = subprocess.run([
            sys.executable, 'manage.py', 'run_social_crawler'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] 爬虫任务完成")
            print("输出:", result.stdout)
        else:
            print(f"[{datetime.now()}] 爬虫任务失败")
            print("错误:", result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now()}] 爬虫任务异常: {str(e)}")

def run_continuous_crawler():
    """持续运行爬虫任务"""
    print("启动持续爬虫任务...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            run_crawler_task()
            
            # 等待5分钟
            print(f"[{datetime.now()}] 等待5分钟后进行下一轮检查...")
            time.sleep(300)  # 5分钟 = 300秒
            
    except KeyboardInterrupt:
        print("\n爬虫任务已停止")

def check_subscription_status():
    """检查订阅状态"""
    print("=== 订阅状态检查 ===")
    
    active_subscriptions = SocialMediaSubscription.objects.filter(status='active')
    print(f"活跃订阅数量: {active_subscriptions.count()}")
    
    for sub in active_subscriptions:
        print(f"- {sub.target_user_name} ({sub.get_platform_display()}) - 检查频率: {sub.check_frequency}分钟")
        print(f"  最后检查: {sub.last_check}")
        print(f"  订阅类型: {sub.subscription_types}")
        print()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='社交媒体爬虫任务管理')
    parser.add_argument('--continuous', action='store_true', help='持续运行爬虫任务')
    parser.add_argument('--once', action='store_true', help='运行一次爬虫任务')
    parser.add_argument('--status', action='store_true', help='检查订阅状态')
    
    args = parser.parse_args()
    
    if args.status:
        check_subscription_status()
    elif args.continuous:
        run_continuous_crawler()
    elif args.once:
        run_crawler_task()
    else:
        print("请指定运行模式:")
        print("  --once       运行一次爬虫任务")
        print("  --continuous 持续运行爬虫任务")
        print("  --status     检查订阅状态")

if __name__ == '__main__':
    main() 