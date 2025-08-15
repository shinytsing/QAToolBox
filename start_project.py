#!/usr/bin/env python
"""
QAToolBox 项目启动脚本
用于快速启动开发环境
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import django
        print(f"✅ Django版本: {django.get_version()}")
    except ImportError:
        print("❌ Django未安装，请先安装依赖")
        return False
    
    try:
        import rest_framework
        print("✅ Django REST Framework已安装")
    except ImportError:
        print("❌ Django REST Framework未安装")
        return False
    
    return True

def install_dependencies():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    
    # 检查是否存在虚拟环境
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  建议在虚拟环境中运行项目")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    try:
        # 安装开发环境依赖
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements/dev.txt'], check=True)
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def setup_environment():
    """设置环境变量"""
    print("🔧 设置环境变量...")
    
    # 检查.env文件是否存在
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 创建.env文件...")
        env_example = Path('env.example')
        if env_example.exists():
            with open(env_example, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ .env文件创建完成")
        else:
            print("⚠️  env.example文件不存在")
    else:
        print("✅ .env文件已存在")

def setup_database():
    """设置数据库"""
    print("🗄️  设置数据库...")
    
    try:
        # 运行数据库初始化脚本
        subprocess.run([sys.executable, 'setup_database.py'], check=True)
        print("✅ 数据库设置完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

def start_development_server():
    """启动开发服务器"""
    print("🚀 启动统一服务器（API + WebSocket）...")
    
    try:
        # 启动统一服务器脚本
        subprocess.run([
            sys.executable, 'start_unified_server.py'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='QAToolBox 项目启动脚本')
    parser.add_argument('--install', action='store_true', help='安装依赖')
    parser.add_argument('--setup', action='store_true', help='设置数据库')
    parser.add_argument('--server', action='store_true', help='启动开发服务器')
    parser.add_argument('--all', action='store_true', help='执行所有步骤')
    
    args = parser.parse_args()
    
    print("🎯 QAToolBox 项目启动脚本")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 如果没有指定参数，默认执行所有步骤
    if not any([args.install, args.setup, args.server, args.all]):
        args.all = True
    
    if args.all or args.install:
        # 检查依赖
        if not check_dependencies():
            if not install_dependencies():
                sys.exit(1)
    
    if args.all or args.setup:
        # 设置环境
        setup_environment()
        
        # 设置数据库
        if not setup_database():
            sys.exit(1)
    
    if args.all or args.server:
        # 启动服务器
        start_development_server()

if __name__ == '__main__':
    main() 