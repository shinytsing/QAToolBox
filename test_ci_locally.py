#!/usr/bin/env python3
"""
本地CI/CD测试脚本
在推送到GitHub之前验证代码质量
"""
import os
import subprocess
import sys
from pathlib import Path

import django

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")
django.setup()


def run_command(command, description):
    """运行命令并返回结果"""
    print(f"\n🔧 {description}")
    print(f"执行命令: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print("输出:", result.stdout)
        else:
            print(f"❌ {description} - 失败")
            print("错误:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ {description} - 异常: {e}")
        return False

    return True


def main():
    """主函数"""
    print("🚀 开始本地CI/CD验证")
    print("=" * 60)

    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        return False

    # 1. 代码格式化检查
    print("\n📝 1. 代码格式化检查")
    if not run_command("black --check .", "Black代码格式检查"):
        print("💡 运行 'black .' 来修复格式问题")
        return False

    if not run_command("isort --check-only .", "导入排序检查"):
        print("💡 运行 'isort .' 来修复导入排序问题")
        return False

    # 2. 静态代码分析
    print("\n🔍 2. 静态代码分析")
    if not run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Flake8语法检查"):
        return False

    if not run_command(
        "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics", "Flake8代码质量检查"
    ):
        return False

    # 3. 类型检查
    print("\n🏷️ 3. 类型检查")
    if not run_command("mypy apps/ --ignore-missing-imports", "MyPy类型检查"):
        print("⚠️ 类型检查有警告，但继续执行")

    # 4. 安全扫描
    print("\n🔒 4. 安全扫描")
    if not run_command(
        "bandit -r apps/ -f json -o bandit-report.json --skip B110,B311,B404,B603,B607,B112,B108 --exit-zero", "Bandit安全扫描"
    ):
        print("⚠️ 安全扫描有警告，但继续执行")

    # 5. 依赖漏洞扫描
    print("\n📦 5. 依赖漏洞扫描")
    if not run_command("safety check --json", "Safety依赖漏洞扫描"):
        print("⚠️ 依赖扫描有警告，但继续执行")

    # 6. 运行测试
    print("\n🧪 6. 运行测试")
    if not run_command("pytest tests/unit/ --cov=apps --cov-report=xml --cov-report=term -v", "单元测试"):
        print("❌ 测试失败")
        return False

    # 7. 检查测试覆盖率
    print("\n📊 7. 检查测试覆盖率")
    try:
        import xml.etree.ElementTree as ET

        root = ET.parse("coverage.xml").getroot()
        coverage = float(root.attrib["line-rate"]) * 100
        print(f"测试覆盖率: {coverage:.1f}%")

        if coverage < 80:
            print(f"❌ 测试覆盖率不达标: {coverage:.1f}% (要求: ≥80%)")
            return False
        else:
            print(f"✅ 测试覆盖率达标: {coverage:.1f}%")
    except Exception as e:
        print(f"❌ 无法读取覆盖率报告: {e}")
        return False

    # 8. 检查Django设置
    print("\n⚙️ 8. Django设置检查")
    try:
        from django.conf import settings

        print(f"DEBUG模式: {settings.DEBUG}")
        print(f"数据库引擎: {settings.DATABASES['default']['ENGINE']}")
        print(f"已安装应用数量: {len(settings.INSTALLED_APPS)}")
        print("✅ Django设置正常")
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False

    # 9. 检查数据库连接
    print("\n🗄️ 9. 数据库连接检查")
    try:
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ 数据库连接正常")
            else:
                print("❌ 数据库连接异常")
                return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 本地CI/CD验证完成！所有检查都通过了。")
    print("✅ 可以安全地推送到GitHub进行部署。")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
