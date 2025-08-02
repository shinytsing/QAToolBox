#!/bin/bash

# 一键提交到GitHub脚本
# 使用方法: ./git_push.sh [可选提交信息]

# 获取当前时间作为默认提交信息
current_time=$(date '+%Y:%m:%d %H:%M:%S')

# 如果提供了提交信息参数，则使用提供的信息，否则使用当前时间
if [ $# -eq 0 ]; then
    commit_message="$current_time"
else
    commit_message="$1"
fi

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