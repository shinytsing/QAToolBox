#!/bin/bash

# QAToolBox 统一服务器启动脚本
# 同时启动API服务和WebSocket聊天服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Python环境
check_python() {
    print_info "检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未找到，请先安装Python3"
        exit 1
    fi
    
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Python版本: $python_version"
}

# 检查虚拟环境
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "建议在虚拟环境中运行"
        echo "   创建虚拟环境: python3 -m venv venv"
        echo "   激活虚拟环境: source venv/bin/activate"
        echo ""
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    else
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查项目依赖..."
    
    if ! python3 -c "import django, channels, daphne" 2>/dev/null; then
        print_warning "缺少必要依赖，正在安装..."
        pip install -r requirements/dev.txt
        print_success "依赖安装完成"
    else
        print_success "所有依赖已安装"
    fi
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用..."
    
    local asgi_port=${1:-8000}
    local api_port=${2:-8001}
    
    if lsof -Pi :$asgi_port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $asgi_port 已被占用"
        read -p "是否终止占用进程? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$asgi_port | xargs kill -9
            print_success "已终止端口 $asgi_port 的占用进程"
        fi
    fi
    
    if lsof -Pi :$api_port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "端口 $api_port 已被占用"
        read -p "是否终止占用进程? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            lsof -ti:$api_port | xargs kill -9
            print_success "已终止端口 $api_port 的占用进程"
        fi
    fi
}

# 显示帮助信息
show_help() {
    echo "🎯 QAToolBox 统一服务器启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help              显示此帮助信息"
    echo "  -p, --port PORT         ASGI服务器端口 (默认: 8000)"
    echo "  -a, --api-port PORT     API服务器端口 (默认: 8001)"
    echo "  --no-redis              跳过Redis检查"
    echo "  --no-migrate            跳过数据库迁移"
    echo "  --no-static             跳过静态文件收集"
    echo "  --asgi-only             仅启动ASGI服务器"
    echo "  --api-only              仅启动API服务器"
    echo "  --dev                   开发模式（跳过一些检查）"
    echo ""
    echo "示例:"
    echo "  $0                      # 使用默认配置启动所有服务"
    echo "  $0 --port 8000 --api-port 8001  # 指定端口"
    echo "  $0 --asgi-only          # 仅启动WebSocket服务器"
    echo "  $0 --api-only           # 仅启动API服务器"
    echo "  $0 --dev                # 开发模式"
}

# 主函数
main() {
    local asgi_port=8000
    local api_port=8001
    local no_redis=false
    local no_migrate=false
    local no_static=false
    local asgi_only=false
    local api_only=false
    local dev_mode=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--port)
                asgi_port="$2"
                shift 2
                ;;
            -a|--api-port)
                api_port="$2"
                shift 2
                ;;
            --no-redis)
                no_redis=true
                shift
                ;;
            --no-migrate)
                no_migrate=true
                shift
                ;;
            --no-static)
                no_static=true
                shift
                ;;
            --asgi-only)
                asgi_only=true
                shift
                ;;
            --api-only)
                api_only=true
                shift
                ;;
            --dev)
                dev_mode=true
                shift
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo "🎯 QAToolBox 统一服务器启动脚本"
    echo "============================================================"
    
    # 基本检查
    check_python
    check_venv
    check_dependencies
    
    # 检查端口占用
    if [[ "$dev_mode" != true ]]; then
        check_ports $asgi_port $api_port
    fi
    
    # 构建Python脚本参数
    local python_args=""
    [[ "$no_redis" == true ]] && python_args="$python_args --no-redis"
    [[ "$no_migrate" == true ]] && python_args="$python_args --no-migrate"
    [[ "$no_static" == true ]] && python_args="$python_args --no-static"
    [[ "$asgi_only" == true ]] && python_args="$python_args --asgi-only"
    [[ "$api_only" == true ]] && python_args="$python_args --api-only"
    [[ "$asgi_port" != "8000" ]] && python_args="$python_args --port $asgi_port"
    [[ "$api_port" != "8001" ]] && python_args="$python_args --api-port $api_port"
    
    # 启动统一服务器
    print_info "启动统一服务器..."
    echo "📍 ASGI服务器: http://localhost:$asgi_port"
    echo "📍 API服务器: http://localhost:$api_port"
    echo "🔌 WebSocket: ws://localhost:$asgi_port/ws/"
    echo "⏹️  按 Ctrl+C 停止所有服务器"
    echo "------------------------------------------------------------"
    
    python3 start_unified_server.py $python_args
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}🛑 收到中断信号，正在停止服务器...${NC}"; exit 0' INT TERM

# 运行主函数
main "$@"
