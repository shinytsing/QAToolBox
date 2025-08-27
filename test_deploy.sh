#!/bin/bash
# =============================================================================
# QAToolBox 部署脚本测试工具
# =============================================================================
# 用于测试部署脚本的语法和基本功能
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# 测试结果统计
total_tests=0
passed_tests=0
failed_tests=0

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((passed_tests++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((failed_tests++))
}

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((total_tests++))
    echo -e "${YELLOW}🧪 测试: $test_name${NC}"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_success "$test_name 通过"
    else
        log_error "$test_name 失败"
    fi
    echo ""
}

# 主测试函数
main() {
    echo -e "${BLUE}🚀 QAToolBox 部署脚本测试${NC}"
    echo "=========================================="
    echo ""
    
    # 测试脚本文件存在性
    run_test "部署脚本文件存在" "[ -f deploy_aliyun.sh ]"
    run_test "Git部署脚本文件存在" "[ -f git_deploy.sh ]"
    run_test "部署文档存在" "[ -f README_DEPLOY.md ]"
    
    # 测试脚本可执行权限
    run_test "部署脚本可执行" "[ -x deploy_aliyun.sh ]"
    run_test "Git部署脚本可执行" "[ -x git_deploy.sh ]"
    
    # 测试脚本语法
    run_test "部署脚本语法检查" "bash -n deploy_aliyun.sh"
    run_test "Git部署脚本语法检查" "bash -n git_deploy.sh"
    
    # 测试脚本帮助功能
    run_test "Git部署脚本帮助功能" "./git_deploy.sh --help"
    
    # 测试配置文件
    run_test "生产配置文件存在" "[ -f config/settings/aliyun_production.py ]"
    run_test "requirements文件存在" "[ -f requirements.txt ]"
    run_test "环境变量示例存在" "[ -f env.example ]"
    
    # 测试Django项目结构
    run_test "Django manage.py存在" "[ -f manage.py ]"
    run_test "Django WSGI文件存在" "[ -f wsgi.py ]"
    run_test "Django URLs文件存在" "[ -f urls.py ]"
    
    # 测试Django应用
    run_test "users应用存在" "[ -d apps/users ]"
    run_test "tools应用存在" "[ -d apps/tools ]"
    run_test "content应用存在" "[ -d apps/content ]"
    
    # 测试模板和静态文件
    run_test "模板目录存在" "[ -d templates ]"
    run_test "静态文件目录存在" "[ -d static ] || [ -d src/static ]"
    
    # 显示测试结果
    echo "=========================================="
    echo -e "${BLUE}📊 测试结果统计${NC}"
    echo -e "总测试数: $total_tests"
    echo -e "${GREEN}通过: $passed_tests${NC}"
    echo -e "${RED}失败: $failed_tests${NC}"
    
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 所有测试通过！${NC}"
        echo -e "${BLUE}✨ 脚本已准备好用于部署${NC}"
        return 0
    else
        echo -e "${RED}⚠️ 有 $failed_tests 个测试失败${NC}"
        echo -e "${YELLOW}💡 请检查失败的测试项${NC}"
        return 1
    fi
}

# 显示使用说明
show_usage() {
    cat << EOF
${BLUE}🧪 QAToolBox 部署脚本测试工具${NC}

${YELLOW}用法:${NC}
  $0 [选项]

${YELLOW}选项:${NC}
  -h, --help    显示此帮助信息

${YELLOW}功能:${NC}
  • 检查部署脚本文件完整性
  • 验证脚本语法正确性
  • 测试脚本可执行权限
  • 验证Django项目结构
  • 检查配置文件完整性

${YELLOW}示例:${NC}
  # 运行完整测试
  $0

  # 在部署前测试
  $0 && echo "可以开始部署"
EOF
}

# 参数解析
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}未知参数: $1${NC}"
        show_usage
        exit 1
        ;;
esac
