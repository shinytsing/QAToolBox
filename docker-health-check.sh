#!/bin/bash

# Docker 健康检查脚本

set -e

# 检查Web服务
if curl -f http://localhost:8000/health/ &> /dev/null; then
    echo "Web服务正常"
    exit 0
else
    echo "Web服务异常"
    exit 1
fi

