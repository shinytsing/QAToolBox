#!/usr/bin/env python3
"""
版本跟踪器测试脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.tools.utils.version_tracker import VersionTracker

def test_version_tracker():
    """测试版本跟踪器功能"""
    print("🧪 版本跟踪器测试")
    print("=" * 50)
    
    # 创建版本跟踪器
    tracker = VersionTracker()
    
    # 测试基本信息
    print(f"📋 当前版本: {tracker.get_current_version()}")
    print(f"📅 项目启动: {tracker.get_project_start_date()}")
    print(f"⏱️ 开发周期: {tracker.get_development_duration()}")
    print(f"📊 版本总数: {tracker.get_version_count()}")
    print(f"🎯 功能总数: {tracker.get_total_features()}")
    
    print("\n📝 版本历史:")
    print("-" * 50)
    
    # 获取所有版本
    versions = tracker.get_all_versions()
    for version in versions:
        formatted_date = tracker.format_date_for_display(version['date'])
        print(f"v{version['version']} ({formatted_date}): {version['title']}")
        print(f"   功能: {', '.join(version['features'])}")
        print(f"   描述: {version['description']}")
        print()
    
    # 测试版本查找
    print("🔍 版本查找测试:")
    print("-" * 30)
    
    test_version = "1.0.0"
    version_info = tracker.get_version_by_number(test_version)
    if version_info:
        print(f"✅ 找到版本 {test_version}: {version_info['title']}")
    else:
        print(f"❌ 未找到版本 {test_version}")
    
    # 测试日期格式化
    print("\n📅 日期格式化测试:")
    print("-" * 30)
    
    test_dates = ["2023-11-20", "2024-01-15", "2024-01-20"]
    for date in test_dates:
        formatted = tracker.format_date_for_display(date)
        print(f"{date} -> {formatted}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_version_tracker()
