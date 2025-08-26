#!/bin/bash

# =============================================================================
# QAToolBox 项目路径诊断脚本
# 快速找到Django项目的实际位置
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================"
echo "    🔍 QAToolBox 项目路径诊断"
echo "========================================"
echo -e "${NC}"

echo -e "${BLUE}1. 检查常见路径...${NC}"
COMMON_PATHS=(
    "/home/qatoolbox/QAToolBox"
    "/home/qatoolbox/QAToolbox"
    "/home/qatoolbox/qatoolbox"
    "/opt/QAToolBox"
    "/var/www/QAToolBox"
    "/root/QAToolBox"
    "/home/ubuntu/QAToolBox"
    "/home/admin/QAToolBox"
)

for path in "${COMMON_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo -e "${GREEN}✅ 目录存在: $path${NC}"
        if [ -f "$path/manage.py" ]; then
            echo -e "${GREEN}   ✅ 包含 manage.py${NC}"
        else
            echo -e "${YELLOW}   ❌ 不包含 manage.py${NC}"
            echo -e "${BLUE}   📁 目录内容:${NC}"
            ls -la "$path" | head -10
        fi
        echo
    else
        echo -e "${RED}❌ 目录不存在: $path${NC}"
    fi
done

echo -e "${BLUE}2. 全局搜索 manage.py 文件...${NC}"
MANAGE_FILES=$(find /home /opt /var/www /root 2>/dev/null -name "manage.py" -type f | head -10)

if [ -n "$MANAGE_FILES" ]; then
    echo -e "${GREEN}找到以下 manage.py 文件:${NC}"
    for file in $MANAGE_FILES; do
        dir_path=$(dirname "$file")
        echo -e "${GREEN}📁 $dir_path${NC}"
        echo -e "   📄 $file"
        
        # 检查是否是Django项目
        if grep -q "django" "$file" 2>/dev/null; then
            echo -e "${GREEN}   ✅ 确认是Django项目${NC}"
        fi
        
        # 显示目录内容
        echo -e "${BLUE}   📋 目录内容:${NC}"
        ls -la "$dir_path" | head -5
        echo
    done
else
    echo -e "${RED}❌ 未找到任何 manage.py 文件${NC}"
fi

echo -e "${BLUE}3. 检查用户目录...${NC}"
if [ -d "/home/qatoolbox" ]; then
    echo -e "${GREEN}✅ qatoolbox用户目录存在${NC}"
    echo -e "${BLUE}📋 /home/qatoolbox 内容:${NC}"
    ls -la /home/qatoolbox/
    echo
else
    echo -e "${RED}❌ qatoolbox用户目录不存在${NC}"
fi

echo -e "${BLUE}4. 检查Git仓库...${NC}"
GIT_DIRS=$(find /home /opt /var/www /root 2>/dev/null -name ".git" -type d | head -5)
if [ -n "$GIT_DIRS" ]; then
    echo -e "${GREEN}找到以下Git仓库:${NC}"
    for git_dir in $GIT_DIRS; do
        project_dir=$(dirname "$git_dir")
        echo -e "${GREEN}📁 $project_dir${NC}"
        
        # 检查远程仓库
        if [ -f "$git_dir/config" ]; then
            remote_url=$(grep -A1 "\[remote" "$git_dir/config" | grep "url" | head -1)
            if [[ "$remote_url" == *"QAToolbox"* ]] || [[ "$remote_url" == *"QAToolBox"* ]]; then
                echo -e "${GREEN}   ✅ 这是QAToolBox仓库！${NC}"
                echo -e "   🔗 $remote_url"
            fi
        fi
        echo
    done
fi

echo -e "${BLUE}5. 推荐操作...${NC}"
echo -e "${YELLOW}基于检查结果，建议:${NC}"

# 如果找到了manage.py文件
if [ -n "$MANAGE_FILES" ]; then
    BEST_PATH=""
    for file in $MANAGE_FILES; do
        dir_path=$(dirname "$file")
        if [[ "$dir_path" == *"QAToolBox"* ]] || [[ "$dir_path" == *"QAToolbox"* ]]; then
            BEST_PATH="$dir_path"
            break
        fi
    done
    
    if [ -n "$BEST_PATH" ]; then
        echo -e "${GREEN}✅ 推荐使用项目路径: $BEST_PATH${NC}"
        echo
        echo -e "${BLUE}快速修复命令:${NC}"
        echo "cd $BEST_PATH"
        echo "sudo chown -R qatoolbox:qatoolbox $BEST_PATH"
        echo "sudo -u qatoolbox python3 -m venv .venv"
        echo "sudo -u qatoolbox .venv/bin/pip install Django"
        echo "sudo -u qatoolbox .venv/bin/python manage.py check"
    else
        FIRST_PATH=$(dirname $(echo "$MANAGE_FILES" | head -1))
        echo -e "${YELLOW}⚠️ 使用第一个找到的Django项目: $FIRST_PATH${NC}"
    fi
else
    echo -e "${RED}❌ 需要重新克隆项目${NC}"
    echo -e "${BLUE}建议执行:${NC}"
    echo "cd /home/qatoolbox"
    echo "git clone https://github.com/shinytsing/QAToolbox.git QAToolBox"
fi

echo -e "${GREEN}========================================"
echo "    ✅ 诊断完成"
echo "========================================"
echo -e "${NC}"
