#!/bin/bash

# 环境切换脚本
# 用法: ./switch_env.sh [testing|production|aliyun]

ENV=${1:-testing}

case $ENV in
    "testing")
        echo "切换到测试环境..."
        export DJANGO_SETTINGS_MODULE=config.settings.testing
        echo "测试环境配置:"
        echo "- 数据库: SQLite (db_test.sqlite3)"
        echo "- 端口: 8001"
        echo "- 调试: 开启"
        echo "- 静态文件: 开发模式"
        echo ""
        echo "启动命令: python start_testing.py"
        ;;
    "production")
        echo "切换到生产环境..."
        export DJANGO_SETTINGS_MODULE=config.settings.production
        echo "生产环境配置:"
        echo "- 数据库: PostgreSQL"
        echo "- 端口: 8000"
        echo "- 调试: 关闭"
        echo "- 静态文件: 生产模式"
        echo ""
        echo "启动命令: python start_public_server.py"
        ;;
    "aliyun")
        echo "切换到阿里云环境..."
        export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
        echo "阿里云环境配置:"
        echo "- 数据库: PostgreSQL"
        echo "- 缓存: Redis"
        echo "- 端口: 8000"
        echo "- 调试: 关闭"
        echo "- 静态文件: 生产模式"
        echo "- 日志: /var/log/qatoolbox/"
        echo ""
        echo "启动命令: python start_aliyun.py"
        ;;
    *)
        echo "用法: $0 [testing|production|aliyun]"
        echo ""
        echo "环境说明:"
        echo "  testing   - 本地测试环境 (SQLite, 端口8001)"
        echo "  production - 本地生产环境 (PostgreSQL, 端口8000)"
        echo "  aliyun    - 阿里云生产环境 (PostgreSQL + Redis)"
        exit 1
        ;;
esac

echo "当前环境: $DJANGO_SETTINGS_MODULE"
