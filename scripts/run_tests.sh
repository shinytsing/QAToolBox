#!/bin/bash
set -e

# QAToolBox 自动化测试脚本
# 运行各种类型的测试

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
TEST_TYPE="all"
COVERAGE=true
PARALLEL=true
VERBOSE=false
FAIL_FAST=false
GENERATE_REPORT=true
CLEAN_CACHE=true

# 显示帮助
show_help() {
    cat << EOF
QAToolBox 自动化测试脚本

使用方法:
    $0 [选项] [测试类型]

测试类型:
    unit            单元测试
    integration     集成测试
    api             API测试
    e2e             端到端测试
    performance     性能测试
    security        安全测试
    all             所有测试 (默认)

选项:
    -h, --help          显示帮助信息
    -v, --verbose       详细输出
    -f, --fail-fast     遇到失败立即停止
    --no-coverage       跳过覆盖率统计
    --no-parallel       不使用并行测试
    --no-report         不生成测试报告
    --no-clean          不清理缓存
    --smoke             只运行冒烟测试

示例:
    $0 unit --verbose           # 运行单元测试，详细输出
    $0 api --fail-fast          # 运行API测试，遇到失败立即停止
    $0 e2e --no-parallel        # 运行E2E测试，不使用并行
    $0 --smoke                  # 只运行冒烟测试
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -f|--fail-fast)
                FAIL_FAST=true
                shift
                ;;
            --no-coverage)
                COVERAGE=false
                shift
                ;;
            --no-parallel)
                PARALLEL=false
                shift
                ;;
            --no-report)
                GENERATE_REPORT=false
                shift
                ;;
            --no-clean)
                CLEAN_CACHE=false
                shift
                ;;
            --smoke)
                TEST_TYPE="smoke"
                shift
                ;;
            unit|integration|api|e2e|performance|security|all)
                TEST_TYPE=$1
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查依赖
check_dependencies() {
    log_info "检查测试依赖..."
    
    cd "$PROJECT_DIR"
    
    # 检查Python虚拟环境
    if [[ ! -d "venv" ]]; then
        log_error "未找到虚拟环境，请先运行部署脚本"
        exit 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查pytest
    if ! python -c "import pytest" 2>/dev/null; then
        log_info "安装测试依赖..."
        pip install -r requirements/testing.txt
    fi
    
    log_success "依赖检查完成"
}

# 清理缓存
clean_cache() {
    if [[ "$CLEAN_CACHE" != true ]]; then
        return 0
    fi
    
    log_info "清理测试缓存..."
    
    cd "$PROJECT_DIR"
    
    # 清理Python缓存
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理pytest缓存
    rm -rf .pytest_cache 2>/dev/null || true
    
    # 清理覆盖率文件
    rm -f .coverage 2>/dev/null || true
    rm -rf htmlcov 2>/dev/null || true
    
    log_success "缓存清理完成"
}

# 设置测试环境
setup_test_environment() {
    log_info "设置测试环境..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE="config.settings.development"
    export DJANGO_TEST_PROCESSES=auto
    
    # 创建测试报告目录
    mkdir -p test_reports
    mkdir -p test_reports/coverage
    mkdir -p test_reports/junit
    
    log_success "测试环境设置完成"
}

# 构建pytest命令
build_pytest_command() {
    local test_path="$1"
    local cmd="python -m pytest"
    
    # 基础参数
    cmd="$cmd $test_path"
    
    # 详细输出
    if [[ "$VERBOSE" == true ]]; then
        cmd="$cmd -v"
    fi
    
    # 快速失败
    if [[ "$FAIL_FAST" == true ]]; then
        cmd="$cmd -x"
    fi
    
    # 并行执行
    if [[ "$PARALLEL" == true ]]; then
        cmd="$cmd -n auto"
    fi
    
    # 覆盖率
    if [[ "$COVERAGE" == true ]]; then
        cmd="$cmd --cov=apps --cov-report=html --cov-report=term --cov-report=xml"
    fi
    
    # JUnit XML报告
    if [[ "$GENERATE_REPORT" == true ]]; then
        cmd="$cmd --junit-xml=test_reports/junit/$(basename $test_path).xml"
    fi
    
    # HTML报告
    if [[ "$GENERATE_REPORT" == true ]]; then
        cmd="$cmd --html=test_reports/$(basename $test_path)_report.html --self-contained-html"
    fi
    
    echo "$cmd"
}

# 运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."
    
    local cmd=$(build_pytest_command "tests/unit/")
    
    if eval "$cmd"; then
        log_success "单元测试通过"
        return 0
    else
        log_error "单元测试失败"
        return 1
    fi
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."
    
    local cmd=$(build_pytest_command "tests/integration/")
    
    if eval "$cmd"; then
        log_success "集成测试通过"
        return 0
    else
        log_error "集成测试失败"
        return 1
    fi
}

# 运行API测试
run_api_tests() {
    log_info "运行API测试..."
    
    local cmd=$(build_pytest_command "tests/integration/test_api.py")
    cmd="$cmd -m api"
    
    if eval "$cmd"; then
        log_success "API测试通过"
        return 0
    else
        log_error "API测试失败"
        return 1
    fi
}

# 运行E2E测试
run_e2e_tests() {
    log_info "运行端到端测试..."
    
    # 检查是否安装了playwright
    if ! python -c "import playwright" 2>/dev/null; then
        log_info "安装Playwright..."
        pip install playwright
        playwright install
    fi
    
    # 启动测试服务器
    log_info "启动测试服务器..."
    python manage.py runserver 8000 &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 5
    
    # 运行E2E测试
    local cmd=$(build_pytest_command "tests/e2e/")
    cmd="$cmd --browser chromium --headless"
    
    local result=0
    if eval "$cmd"; then
        log_success "E2E测试通过"
    else
        log_error "E2E测试失败"
        result=1
    fi
    
    # 停止测试服务器
    kill $SERVER_PID 2>/dev/null || true
    
    return $result
}

# 运行性能测试
run_performance_tests() {
    log_info "运行性能测试..."
    
    # 检查Locust
    if ! python -c "import locust" 2>/dev/null; then
        log_info "安装Locust..."
        pip install locust
    fi
    
    # 启动应用服务器
    log_info "启动应用服务器进行性能测试..."
    python manage.py runserver 8000 &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 5
    
    # 运行性能测试
    local result=0
    if locust -f tests/performance/locustfile.py \
        --host=http://localhost:8000 \
        --users 50 \
        --spawn-rate 5 \
        --run-time 60s \
        --headless \
        --html test_reports/performance_report.html; then
        log_success "性能测试完成"
    else
        log_error "性能测试失败"
        result=1
    fi
    
    # 停止服务器
    kill $SERVER_PID 2>/dev/null || true
    
    return $result
}

# 运行安全测试
run_security_tests() {
    log_info "运行安全测试..."
    
    # 检查bandit
    if ! python -c "import bandit" 2>/dev/null; then
        log_info "安装安全检查工具..."
        pip install bandit safety
    fi
    
    local result=0
    
    # 运行bandit安全扫描
    log_info "运行Bandit安全扫描..."
    if bandit -r apps/ -f json -o test_reports/bandit_report.json; then
        log_success "Bandit安全扫描通过"
    else
        log_warning "Bandit发现安全问题，请检查报告"
        result=1
    fi
    
    # 运行safety检查
    log_info "运行Safety依赖安全检查..."
    if safety check --json --output test_reports/safety_report.json; then
        log_success "Safety检查通过"
    else
        log_warning "Safety发现安全漏洞，请检查报告"
        result=1
    fi
    
    # 运行安全相关的pytest测试
    local cmd=$(build_pytest_command "tests/")
    cmd="$cmd -m security"
    
    if eval "$cmd"; then
        log_success "安全功能测试通过"
    else
        log_error "安全功能测试失败"
        result=1
    fi
    
    return $result
}

# 运行冒烟测试
run_smoke_tests() {
    log_info "运行冒烟测试..."
    
    # 启动服务器
    python manage.py runserver 8000 &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 5
    
    # 运行冒烟测试
    local result=0
    if python scripts/smoke_test.py --url http://localhost:8000; then
        log_success "冒烟测试通过"
    else
        log_error "冒烟测试失败"
        result=1
    fi
    
    # 停止服务器
    kill $SERVER_PID 2>/dev/null || true
    
    return $result
}

# 生成测试总结报告
generate_summary_report() {
    if [[ "$GENERATE_REPORT" != true ]]; then
        return 0
    fi
    
    log_info "生成测试总结报告..."
    
    local report_file="test_reports/test_summary_$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>QAToolBox 测试报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .summary { margin: 20px 0; }
        .test-type { margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; }
        .pass { border-left-color: #28a745; }
        .fail { border-left-color: #dc3545; }
        .links { margin: 20px 0; }
        .links a { margin-right: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>QAToolBox 测试报告</h1>
        <p>生成时间: $(date)</p>
        <p>测试类型: $TEST_TYPE</p>
    </div>
    
    <div class="summary">
        <h2>测试概要</h2>
        <p>详细的测试结果请查看对应的报告文件。</p>
    </div>
    
    <div class="links">
        <h2>报告链接</h2>
        <a href="coverage/index.html">覆盖率报告</a>
        <a href="unit_report.html">单元测试报告</a>
        <a href="integration_report.html">集成测试报告</a>
        <a href="e2e_report.html">E2E测试报告</a>
        <a href="performance_report.html">性能测试报告</a>
    </div>
</body>
</html>
EOF
    
    log_success "测试总结报告已生成: $report_file"
}

# 主函数
main() {
    # 解析参数
    parse_arguments "$@"
    
    log_info "开始运行测试 - 类型: $TEST_TYPE"
    
    # 执行测试前的准备工作
    check_dependencies
    clean_cache
    setup_test_environment
    
    local overall_result=0
    
    # 根据测试类型运行相应测试
    case $TEST_TYPE in
        "unit")
            run_unit_tests || overall_result=1
            ;;
        "integration")
            run_integration_tests || overall_result=1
            ;;
        "api")
            run_api_tests || overall_result=1
            ;;
        "e2e")
            run_e2e_tests || overall_result=1
            ;;
        "performance")
            run_performance_tests || overall_result=1
            ;;
        "security")
            run_security_tests || overall_result=1
            ;;
        "smoke")
            run_smoke_tests || overall_result=1
            ;;
        "all")
            run_unit_tests || overall_result=1
            run_integration_tests || overall_result=1
            run_api_tests || overall_result=1
            
            # E2E和性能测试可能较慢，根据需要执行
            if [[ "$FAIL_FAST" != true ]] || [[ $overall_result -eq 0 ]]; then
                run_e2e_tests || overall_result=1
                run_performance_tests || overall_result=1
                run_security_tests || overall_result=1
            fi
            ;;
        *)
            log_error "未知测试类型: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # 生成报告
    generate_summary_report
    
    # 输出结果
    if [[ $overall_result -eq 0 ]]; then
        log_success "🎉 所有测试通过！"
        echo ""
        echo "测试报告位置: test_reports/"
        
        if [[ "$COVERAGE" == true ]] && [[ -f "htmlcov/index.html" ]]; then
            echo "覆盖率报告: htmlcov/index.html"
        fi
    else
        log_error "❌ 测试失败！请检查测试报告。"
        echo ""
        echo "测试报告位置: test_reports/"
        exit 1
    fi
}

# 执行主函数
main "$@"
