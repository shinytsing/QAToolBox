#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本测试脚本
"""

import os
import sys
import time

print("🚀 开始基本测试...")

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    print("✅ Django设置成功")
    
    from django.contrib.auth.models import User
    from django.test import Client
    
    # 测试数据库连接
    user_count = User.objects.count()
    print(f"📊 数据库连接正常，用户总数: {user_count}")
    
    # 测试Web请求
    client = Client()
    start_time = time.time()
    response = client.get('/')
    end_time = time.time()
    
    print(f"📊 Web请求测试:")
    print(f"   状态码: {response.status_code}")
    print(f"   响应时间: {end_time - start_time:.3f}秒")
    
    # 测试用户创建
    start_time = time.time()
    test_user = User.objects.create_user(
        username=f'test_user_{int(time.time())}',
        email=f'test_{int(time.time())}@test.com',
        password='test123456'
    )
    end_time = time.time()
    
    print(f"📊 用户创建测试:")
    print(f"   创建时间: {end_time - start_time:.3f}秒")
    
    # 清理测试用户
    test_user.delete()
    print("✅ 测试用户已清理")
    
    print("🎉 基本测试完成!")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
