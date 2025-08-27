#!/bin/bash
# 修复Ubuntu系统pip wheel冲突问题
# 解决 "Cannot uninstall wheel 0.42.0" 错误

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 开始修复pip wheel冲突问题...${NC}"

# 检查系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID=$ID
else
    echo -e "${RED}❌ 无法检测系统类型${NC}"
    exit 1
fi

if [ "$OS_ID" != "ubuntu" ] && [ "$OS_ID" != "debian" ]; then
    echo -e "${YELLOW}⚠️  此脚本专为Ubuntu/Debian系统设计${NC}"
    exit 0
fi

echo -e "${GREEN}✅ 检测到系统: $OS_ID${NC}"

# 方法1: 尝试使用--break-system-packages
echo -e "${YELLOW}📦 方法1: 尝试使用--break-system-packages...${NC}"
if python3 -m pip install --upgrade pip setuptools wheel --break-system-packages 2>/dev/null; then
    echo -e "${GREEN}✅ 方法1成功！pip升级完成${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  方法1失败，尝试方法2...${NC}"
fi

# 方法2: 强制重新安装，忽略已安装的包
echo -e "${YELLOW}📦 方法2: 强制重新安装...${NC}"
if python3 -m pip install --upgrade --force-reinstall --ignore-installed pip setuptools wheel 2>/dev/null; then
    echo -e "${GREEN}✅ 方法2成功！pip升级完成${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  方法2失败，尝试方法3...${NC}"
fi

# 方法3: 只升级pip和setuptools，不升级wheel
echo -e "${YELLOW}📦 方法3: 跳过wheel，只升级pip和setuptools...${NC}"
if python3 -m pip install --upgrade --force-reinstall pip setuptools 2>/dev/null; then
    echo -e "${GREEN}✅ 方法3成功！pip和setuptools升级完成（跳过wheel）${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  方法3失败，尝试方法4...${NC}"
fi

# 方法4: 使用apt升级系统pip
echo -e "${YELLOW}📦 方法4: 使用apt升级系统pip...${NC}"
if apt install -y --only-upgrade python3-pip 2>/dev/null; then
    echo -e "${GREEN}✅ 方法4成功！使用apt升级系统pip完成${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  方法4失败，尝试方法5...${NC}"
fi

# 方法5: 完全重新安装python3-pip
echo -e "${YELLOW}📦 方法5: 完全重新安装python3-pip...${NC}"
if apt remove -y python3-pip && apt install -y python3-pip 2>/dev/null; then
    echo -e "${GREEN}✅ 方法5成功！重新安装python3-pip完成${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  方法5失败，尝试方法6...${NC}"
fi

# 方法6: 手动修复wheel包
echo -e "${YELLOW}📦 方法6: 手动修复wheel包...${NC}"
if python3 -m pip install --upgrade --force-reinstall --no-deps wheel 2>/dev/null; then
    echo -e "${GREEN}✅ 方法6成功！wheel包修复完成${NC}"
    # 再次尝试升级pip
    if python3 -m pip install --upgrade pip setuptools 2>/dev/null; then
        echo -e "${GREEN}✅ pip升级也成功了！${NC}"
        exit 0
    fi
else
    echo -e "${YELLOW}⚠️  方法6失败，尝试最终方法...${NC}"
fi

# 最终方法: 使用get-pip.py重新安装
echo -e "${YELLOW}📦 最终方法: 使用get-pip.py重新安装...${NC}"
if curl -fsSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py --force-reinstall 2>/dev/null; then
    echo -e "${GREEN}✅ 最终方法成功！使用get-pip.py重新安装完成${NC}"
    rm -f get-pip.py
    exit 0
else
    echo -e "${RED}❌ 所有方法都失败了！${NC}"
    echo -e "${YELLOW}💡 建议手动检查系统状态或联系系统管理员${NC}"
    exit 1
fi
