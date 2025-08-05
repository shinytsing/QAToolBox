#!/usr/bin/env python3
"""
自动启动社交媒体爬虫
根据订阅频率自动运行，无需手动干预
"""

import os
import sys
import django
import signal
import time
import logging
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.social_media_crawler import run_continuous_crawler
from apps.tools.models import SocialMediaSubscription

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class AutoCrawler:
    def __init__(self):
        self.running = True
        self.logger = logging.getLogger(__name__)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理退出信号"""
        self.logger.info(f"收到退出信号 {signum}，正在停止爬虫...")
        self.running = False
    
    def check_subscriptions(self):
        """检查订阅状态"""
        try:
            active_subscriptions = SocialMediaSubscription.objects.filter(status='active')
            print(f"发现 {active_subscriptions.count()} 个活跃订阅")
            
            # 显示订阅统计
            frequency_stats = {}
            for sub in active_subscriptions:
                freq = sub.check_frequency
                if freq not in frequency_stats:
                    frequency_stats[freq] = []
                frequency_stats[freq].append(sub)
            
            print("订阅频率统计:")
            for freq in sorted(frequency_stats.keys()):
                count = len(frequency_stats[freq])
                print(f"  {freq}分钟频率: {count} 个订阅")
            
            return active_subscriptions.count() > 0
        except Exception as e:
            print(f"检查订阅状态时出错: {str(e)}")
            return False
    
    def start(self):
        """启动自动爬虫"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 社交媒体订阅自动爬虫")
        self.logger.info("=" * 60)
        self.logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("功能特点:")
        self.logger.info("  ✅ 根据订阅频率自动调度")
        self.logger.info("  ✅ 智能检查间隔")
        self.logger.info("  ✅ 实时状态监控")
        self.logger.info("  ✅ 优雅退出处理")
        self.logger.info("  ✅ 详细日志记录")
        self.logger.info("=" * 60)
        
        # 检查活跃订阅
        if not self.check_subscriptions():
            self.logger.warning("⚠️  没有活跃订阅，爬虫将等待新订阅...")
        
        self.logger.info("开始自动运行...")
        self.logger.info("按 Ctrl+C 停止")
        self.logger.info("-" * 60)
        
        try:
            while self.running:
                try:
                    # 检查是否有活跃订阅
                    if self.check_subscriptions():
                        # 运行爬虫任务
                        run_continuous_crawler()
                    else:
                        # 没有活跃订阅，等待5分钟后重试
                        self.logger.info("没有活跃订阅，等待5分钟后重试...")
                        time.sleep(300)
                except KeyboardInterrupt:
                    self.logger.info("用户手动停止")
                    break
                except Exception as e:
                    self.logger.error(f"爬虫运行异常: {str(e)}")
                    self.logger.info("等待30秒后重试...")
                    time.sleep(30)
        except Exception as e:
            self.logger.error(f"爬虫启动失败: {str(e)}")
        finally:
            self.logger.info(f"爬虫已停止 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info("=" * 60)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动社交媒体爬虫')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--log', type=str, help='日志文件路径')
    parser.add_argument('--check-only', action='store_true', help='仅检查订阅状态，不运行爬虫')
    
    args = parser.parse_args()
    
    if args.log:
        # 自定义日志文件
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(args.log),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    if args.check_only:
        # 仅检查订阅状态
        print("检查订阅状态...")
        crawler = AutoCrawler()
        crawler.check_subscriptions()
        return
    
    if args.daemon:
        # 守护进程模式
        try:
            import daemon
            with daemon.DaemonContext():
                crawler = AutoCrawler()
                crawler.start()
        except ImportError:
            print("警告: daemon模块未安装，以普通模式运行")
            crawler = AutoCrawler()
            crawler.start()
    else:
        # 普通模式
        crawler = AutoCrawler()
        crawler.start()

if __name__ == '__main__':
    main() 