#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头像点击进入里世界 - 最终功能演示
包含赛博哥特主题和故障艺术效果
"""

import webbrowser
import time
import os
import sys

def print_banner():
    print("🎭" * 50)
    print("🎭 头像点击进入里世界 - 最终功能演示 🎭")
    print("🎭" * 50)

def print_feature_list():
    print("\n📋 功能特性:")
    print("=" * 50)
    print("🎯 头像点击四次进入里世界")
    print("⚡ 3秒倒计时自动重置")
    print("✨ 每次点击视觉反馈")
    print("🎨 第四次点击特殊动画")
    print("🌌 赛博哥特故障艺术效果")
    print("🔄 故障等级自动重置")
    print("🎪 主题切换功能")
    print("📱 响应式设计")

def print_test_pages():
    print("\n🎯 测试页面:")
    print("=" * 50)
    print("1. 基础测试: test_avatar_click.html")
    print("2. 增强测试: test_avatar_click_enhanced.html")
    print("3. 主页测试: http://localhost:8001/")
    print("4. 里世界: http://localhost:8001/tools/vanity-os/")

def check_server():
    print("\n🚀 服务器状态检查:")
    print("=" * 50)
    try:
        import requests
        response = requests.get("http://localhost:8001/", timeout=3)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print("⚠️  服务器响应异常")
            return False
    except:
        print("❌ 服务器未运行")
        return False

def open_test_pages():
    print("\n🌐 打开测试页面:")
    print("=" * 50)
    
    # 检查测试页面
    pages = [
        ("test_avatar_click.html", "基础测试页面"),
        ("test_avatar_click_enhanced.html", "增强测试页面")
    ]
    
    for page, description in pages:
        if os.path.exists(page):
            print(f"✅ {description}: {page}")
        else:
            print(f"❌ {description}: {page} (不存在)")
    
    # 询问是否打开页面
    choice = input("\n是否打开测试页面? (y/n): ")
    if choice.lower() == 'y':
        for page, description in pages:
            if os.path.exists(page):
                print(f"正在打开 {description}...")
                webbrowser.open("file://" + os.path.abspath(page))
                time.sleep(1)

def open_server_pages():
    if check_server():
        choice = input("\n是否打开服务器页面? (y/n): ")
        if choice.lower() == 'y':
            print("正在打开主页...")
            webbrowser.open("http://localhost:8001/")
            time.sleep(2)
            
            choice2 = input("是否打开里世界页面? (y/n): ")
            if choice2.lower() == 'y':
                print("正在打开里世界...")
                webbrowser.open("http://localhost:8001/tools/vanity-os/")

def print_instructions():
    print("\n📖 使用说明:")
    print("=" * 50)
    print("1. 在任意页面的右上角找到用户头像")
    print("2. 连续点击头像四次（3秒内完成）")
    print("3. 观察每次点击的视觉反馈")
    print("4. 第四次点击会触发特殊动画效果")
    print("5. 1秒后自动跳转到里世界页面")
    print("\n🎨 赛博哥特模式:")
    print("1. 在增强测试页面选择赛博哥特模式")
    print("2. 点击页面任意位置增加故障等级")
    print("3. 观察不同等级的故障艺术效果")
    print("4. 5秒后故障等级自动重置")

def print_technical_details():
    print("\n🔧 技术实现:")
    print("=" * 50)
    print("• 事件监听: addEventListener('click')")
    print("• 事件阻止: e.stopPropagation()")
    print("• 定时器管理: setTimeout/clearTimeout")
    print("• CSS动画: @keyframes glitch")
    print("• 故障效果: transform + filter")
    print("• 主题切换: classList.add/remove")
    print("• 响应式: CSS media queries")

def main():
    print_banner()
    print_feature_list()
    print_test_pages()
    print_instructions()
    print_technical_details()
    
    # 检查并打开测试页面
    open_test_pages()
    
    # 检查并打开服务器页面
    open_server_pages()
    
    print("\n🎉 演示完成！")
    print("=" * 50)
    print("感谢使用头像点击进入里世界功能！")
    print("🎭" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 演示已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        sys.exit(1) 