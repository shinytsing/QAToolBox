#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试头像点击进入里世界功能
"""

import requests
import webbrowser
import time

def test_server():
    """测试服务器状态"""
    print("🔍 测试服务器状态...")
    try:
        response = requests.get("http://localhost:8001/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False

def test_vanity_os():
    """测试里世界页面"""
    print("🔍 测试里世界页面...")
    try:
        response = requests.get("http://localhost:8001/tools/vanity-os/", timeout=5)
        if response.status_code == 200:
            print("✅ 里世界页面可访问")
            return True
        else:
            print(f"⚠️  里世界页面响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 里世界页面连接失败: {e}")
        return False

def open_test_pages():
    """打开测试页面"""
    print("\n🌐 打开测试页面...")
    
    # 打开基础测试页面
    print("📄 打开基础测试页面...")
    webbrowser.open("file://" + __import__('os').path.abspath("test_avatar_click.html"))
    time.sleep(1)
    
    # 打开增强测试页面
    print("📄 打开增强测试页面...")
    webbrowser.open("file://" + __import__('os').path.abspath("test_avatar_click_enhanced.html"))
    time.sleep(1)
    
    # 打开主页
    print("🏠 打开主页...")
    webbrowser.open("http://localhost:8001/")
    time.sleep(1)

def main():
    print("🎭 头像点击进入里世界 - 快速测试")
    print("=" * 50)
    
    # 测试服务器
    if not test_server():
        print("❌ 服务器测试失败，请先启动服务器")
        return
    
    # 测试里世界页面
    if not test_vanity_os():
        print("⚠️  里世界页面测试失败，但基础功能可能正常")
    
    print("\n✅ 基础测试通过！")
    print("\n📋 测试步骤:")
    print("1. 在测试页面中点击头像四次")
    print("2. 观察每次点击的视觉反馈")
    print("3. 第四次点击会触发特殊动画")
    print("4. 1秒后跳转到里世界页面")
    
    # 询问是否打开测试页面
    choice = input("\n是否打开测试页面? (y/n): ")
    if choice.lower() == 'y':
        open_test_pages()
        print("\n🎉 测试页面已打开！")
        print("请尝试点击头像四次来测试功能")
    else:
        print("\n👋 测试完成")
    
    print("\n" + "=" * 50)
    print("🎭 头像点击进入里世界功能测试完成 🎭")

if __name__ == "__main__":
    main() 