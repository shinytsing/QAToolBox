#!/usr/bin/env python3
"""
QAToolBox 依赖修复脚本
自动检测和修复缺失的依赖，保证功能完整性
"""
import os
import sys
import subprocess
import importlib.util

def check_and_install_package(package_name, pip_name=None):
    """检查并安装缺失的包"""
    if pip_name is None:
        pip_name = package_name
    
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} 缺失，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name])
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} 安装失败")
            return False

def main():
    """主函数"""
    print("🔧 开始检查和修复依赖...")
    
    # 核心依赖列表
    dependencies = [
        ('environ', 'django-environ'),
        ('decouple', 'python-decouple'),
        ('psutil', 'psutil'),
        ('PIL', 'Pillow'),
        ('rest_framework', 'djangorestframework'),
        ('corsheaders', 'django-cors-headers'),
        ('celery', 'celery'),
        ('redis', 'redis'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('lxml', 'lxml'),
        ('django_extensions', 'django-extensions'),
    ]
    
    failed_packages = []
    
    for package, pip_name in dependencies:
        if not check_and_install_package(package, pip_name):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ 以下包安装失败: {', '.join(failed_packages)}")
        return False
    else:
        print("\n✅ 所有依赖安装完成！")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
