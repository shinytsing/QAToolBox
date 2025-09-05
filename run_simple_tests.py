#!/usr/bin/env python
"""
简化的测试运行脚本
用于本地CI/CD测试
"""

import os
import subprocess
import sys

import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test_minimal")
django.setup()


def run_tests():
    """运行测试"""
    print("🧪 开始运行测试...")

    # 测试命令
    test_cmd = [
        "python",
        "-m",
        "pytest",
        "tests/unit/test_basic_coverage.py",
        "--cov=apps",
        "--cov-report=term",
        "--cov-report=xml",
        "--cov-report=html",
        "-v",
        "--tb=short",
        "--maxfail=10",
    ]

    try:
        result = subprocess.run(test_cmd, check=True, capture_output=True, text=True)
        print("✅ 测试通过!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 测试失败!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_code_quality():
    """运行代码质量检查"""
    print("🔍 开始代码质量检查...")

    # 代码格式化检查
    try:
        subprocess.run(["python", "-m", "black", "--check", "."], check=True)
        print("✅ Black格式化检查通过")
    except subprocess.CalledProcessError:
        print("❌ Black格式化检查失败")
        return False

    # 导入排序检查
    try:
        subprocess.run(["python", "-m", "isort", "--check-only", "."], check=True)
        print("✅ isort导入排序检查通过")
    except subprocess.CalledProcessError:
        print("❌ isort导入排序检查失败")
        return False

    return True


def main():
    """主函数"""
    print("🚀 开始本地CI/CD测试...")

    # 运行代码质量检查
    if not run_code_quality():
        print("❌ 代码质量检查失败")
        sys.exit(1)

    # 运行测试
    if not run_tests():
        print("❌ 测试失败")
        sys.exit(1)

    print("🎉 所有检查通过! 可以推送到GitHub")


if __name__ == "__main__":
    main()
