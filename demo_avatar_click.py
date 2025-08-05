#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头像点击进入里世界功能演示脚本
"""

import webbrowser
import time
import os

def main():
    print("🎭 头像点击进入里世界功能演示")
    print("=" * 50)
    
    print("\n📋 功能说明:")
    print("1. 在任意页面的右上角找到用户头像")
    print("2. 连续点击头像四次（3秒内完成）")
    print("3. 第四次点击会触发特殊动画效果")
    print("4. 1秒后自动跳转到里世界页面")
    
    print("\n🎯 测试步骤:")
    print("1. 打开测试页面: test_avatar_click.html")
    print("2. 或者访问主页: http://localhost:8001/")
    print("3. 尝试点击头像四次")
    
    print("\n🔧 技术特点:")
    print("- 阻止事件冒泡，不影响下拉菜单")
    print("- 3秒倒计时自动重置")
    print("- 每次点击都有视觉反馈")
    print("- 全局生效，所有页面都可以使用")
    
    # 检查测试页面是否存在
    if os.path.exists("test_avatar_click.html"):
        print("\n📁 测试页面已创建: test_avatar_click.html")
        choice = input("是否打开测试页面? (y/n): ")
        if choice.lower() == 'y':
            webbrowser.open("file://" + os.path.abspath("test_avatar_click.html"))
    else:
        print("\n❌ 测试页面不存在")
    
    print("\n🚀 服务器状态:")
    try:
        import requests
        response = requests.get("http://localhost:8001/", timeout=2)
        if response.status_code == 200:
            print("✅ 服务器运行正常: http://localhost:8001/")
            choice = input("是否打开主页? (y/n): ")
            if choice.lower() == 'y':
                webbrowser.open("http://localhost:8001/")
        else:
            print("⚠️  服务器响应异常")
    except:
        print("❌ 服务器未运行，请先启动: python manage.py runserver 8001")
    
    print("\n🎉 演示完成！")
    print("=" * 50)

if __name__ == "__main__":
    main() 