#!/usr/bin/env python
"""
聊天室清理定时任务启动脚本
"""

import os
import sys
import time
import logging
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from django.core.management import call_command
from django.utils import timezone

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_cleanup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_cleanup_task():
    """运行清理任务"""
    try:
        logger.info("开始执行聊天室清理任务...")
        
        # 执行聊天室清理
        call_command('cleanup_chat_rooms', minutes=10)
        
        # 执行心动链接清理
        call_command('cleanup_heart_links')
        
        logger.info("清理任务执行完成")
        
    except Exception as e:
        logger.error(f"清理任务执行失败: {e}")

def main():
    """主函数"""
    logger.info("聊天室清理定时任务启动")
    logger.info("清理间隔: 5分钟")
    logger.info("断开连接后清理时间: 10分钟")
    
    try:
        while True:
            current_time = timezone.now()
            logger.info(f"当前时间: {current_time}")
            
            # 执行清理任务
            run_cleanup_task()
            
            # 等待5分钟
            logger.info("等待5分钟后执行下一次清理...")
            time.sleep(300)  # 5分钟 = 300秒
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止...")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        logger.info("聊天室清理定时任务已停止")

if __name__ == '__main__':
    main()
