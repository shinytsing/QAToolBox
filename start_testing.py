#!/usr/bin/env python
"""
测试环境启动脚本
用于本地开发和测试
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    # 设置Django设置模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
    
    # 初始化Django
    django.setup()
    
    # 启动开发服务器
    execute_from_command_line([
        'manage.py', 
        'runserver', 
        '127.0.0.1:8001',  # 使用不同端口避免冲突
        '--noreload'  # 禁用自动重载以提高性能
    ])
