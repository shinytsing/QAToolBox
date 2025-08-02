#!/bin/bash

# 一键提交到GitHub脚本
# 使用方法: ./git_push.sh "提交信息"

# 检查是否提供了提交信息
if [ $# -eq 0 ]; then
    echo "请提供提交信息"
    echo "使用方法: ./git_push.sh \"提交信息\""
    exit 1
fi

# 获取提交信息
commit_message="$1"

echo "开始一键提交到GitHub..."

# 添加所有文件到暂存区
echo "1. 添加所有文件到暂存区..."
git add .

# 提交更改
echo "2. 提交更改..."
git commit -m "$commit_message"

# 推送到远程仓库
echo "3. 推送到远程仓库..."
git push

echo "✅ 提交完成！"
echo "提交信息: $commit_message" 