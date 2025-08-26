#!/bin/bash

# =============================================================================
# QAToolBox 项目清理脚本
# 删除历史部署文件和不必要的文件，简化项目结构
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}========================================"
echo "    🧹 QAToolBox 项目清理"
echo "========================================"
echo -e "${NC}"

# 确认操作
echo -e "${YELLOW}⚠️  此操作将删除大量历史文件，请确认：${NC}"
echo "即将删除："
echo "• 所有历史部署脚本"
echo "• 所有.md文档文件（除README.md外）"
echo "• 测试和示例文件"
echo "• 配置和日志文件"
echo

read -p "确定要继续吗？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

echo

# 删除历史部署脚本
log_info "删除历史部署脚本"
DEPLOY_SCRIPTS=(
    "auto_clone_deploy.sh"
    "china_network_deploy.sh"
    "complete_solution.sh"
    "deploy_aliyun_centos.sh"
    "deploy_complete_ubuntu.sh"
    "deploy_shenyiqing_production.sh"
    "deploy_smart_fix.sh"
    "deploy_ubuntu_production.sh"
    "deploy.py"
    "deploy.sh"
    "emergency_fix_deployment.sh"
    "emergency_security_response.sh"
    "final_fix_deployment.sh"
    "find_project.sh"
    "fix_502_error.sh"
    "fix_centos8_repos.sh"
    "fix_current_deploy.sh"
    "fix_dependencies_and_settings.sh"
    "fix_deployment_issues.sh"
    "fix_nginx_ssl_config.sh"
    "fix_psutil_deploy.sh"
    "fix_static_and_urls.sh"
    "fix_ubuntu_24_apt.sh"
    "fix_ubuntu_24_packages.sh"
    "fix_ubuntu_download_speed.sh"
    "fresh_deploy_from_git.sh"
    "fresh_start_deploy.sh"
    "keep_full_features_fix.sh"
    "one_click_install.sh"
    "perfect_deploy_china.sh"
    "quick_fix_now.sh"
    "quick_local_fix.sh"
    "setup_auto_deploy.sh"
    "simple_direct_deploy.sh"
    "smart_fix_deploy.sh"
    "ultimate_bypass_fix.sh"
    "ultimate_fix.sh"
)

for script in "${DEPLOY_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        rm "$script"
        echo "  ✅ 删除: $script"
    fi
done

# 删除文档和说明文件
log_info "删除文档和说明文件"
DOC_FILES=(
    "ALIYUN_DEPLOY_GUIDE.md"
    "BUSINESS_PROXY_GUIDE.md"
    "CLASH_SETUP_GUIDE.md"
    "DEPLOY_SMART_README.md"
    "DEPLOY_V2.md"
    "ENHANCED_FEATURES_SUMMARY.md"
    "EXERCISE_DROP_ZONE_ENHANCEMENT_SUMMARY.md"
    "FILE_PATH_FIX_SUMMARY.md"
    "FINAL_HEART_LINK_FIX_SUMMARY.md"
    "FINAL_REPORT.md"
    "FINAL_THREE_ISSUES_FIX_SUMMARY.md"
    "FITNESS_ENHANCEMENT_SUMMARY.md"
    "GOOD_PEOPLE_GUIDE_README.md"
    "GOOD_PEOPLE_GUIDE_SUMMARY.md"
    "HEART_LINK_FIX_SUMMARY.md"
    "HEART_LINK_FIXES_SUMMARY.md"
    "JAVASCRIPT_SYNTAX_FIX_SUMMARY.md"
    "NETWORK_DEPLOY_SUCCESS.md"
    "PROJECT_REFACTOR_SUMMARY.md"
    "PROXY_SYSTEM_README.md"
    "QUICK_START_ALIYUN.md"
    "QUICK_START.md"
    "SIMPLE_DIARY_FIX_SUMMARY.md"
    "SOCIAL_API_FIX_SUMMARY.md"
    "START_CLASH.md"
    "WEBSOCKET_MESSAGE_SYNC_GUIDE.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [ -f "$doc" ]; then
        rm "$doc"
        echo "  ✅ 删除: $doc"
    fi
done

# 删除测试和示例文件
log_info "删除测试和示例文件"
TEST_FILES=(
    "calendar_feature_guide.txt"
    "date_test.html"
    "good_people_guide_demo.html"
    "google_encoding_test.json"
    "heart_link_test_guide.md"
    "image_viewer_test_guide.txt"
    "proxy_diagnostic.html"
    "simple_diary_output.html"
    "test_enhanced_features_report.json"
)

for test in "${TEST_FILES[@]}"; do
    if [ -f "$test" ]; then
        rm "$test"
        echo "  ✅ 删除: $test"
    fi
done

# 删除配置和日志文件
log_info "删除配置和日志文件"
CONFIG_FILES=(
    "captcha.png"
    "clash_config_youtube_optimized.yaml"
    "crawler.log"
    "db.sqlite3"
    "env.production"
    "git_push.sh"
    "nginx_https.conf"
    "proxy_pool.json"
    "server.log"
    "settings.py"
)

for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        rm "$config"
        echo "  ✅ 删除: $config"
    fi
done

# 删除启动脚本（保留关键的）
log_info "删除多余的启动脚本"
START_SCRIPTS=(
    "install_clashx.sh"
    "quick_start_clash.sh"
    "quick_start.py"
    "run_asgi_server.py"
    "simple_https_server.py"
    "simple_start.py"
    "start_asgi.sh"
    "start_auto_crawler.py"
    "start_chat_cleanup.py"
    "start_clash_proxy.sh"
    "start_good_people_guide.sh"
    "start_heart_link.sh"
    "start_https_server.py"
    "start_https_with_nginx.sh"
    "start_project.py"
    "start_proxy_service.sh"
    "start_server.sh"
    "start_unified_server.py"
    "start_with_websocket.sh"
)

for start in "${START_SCRIPTS[@]}"; do
    if [ -f "$start" ]; then
        rm "$start"
        echo "  ✅ 删除: $start"
    fi
done

# 删除工具脚本
log_info "删除工具脚本"
TOOL_SCRIPTS=(
    "enhanced_proxy_server.py"
    "local_proxy_server.py"
    "mobile_api_enhancement.py"
    "setup_api.py"
    "setup_crawler_scheduler.py"
    "setup_database.py"
    "setup_selenium.py"
    "setup_ssh_key_auth.sh"
    "setup_travel_apis.py"
)

for tool in "${TOOL_SCRIPTS[@]}"; do
    if [ -f "$tool" ]; then
        rm "$tool"
        echo "  ✅ 删除: $tool"
    fi
done

# 删除目录（如果为空或不重要）
log_info "清理目录"
DIRS_TO_CLEAN=(
    "logs"
    "ssl"
    "test_audio"
    "docs"
)

for dir in "${DIRS_TO_CLEAN[@]}"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "  ✅ 删除目录: $dir"
    fi
done

# 清理Docker相关文件（如果不需要）
log_info "清理Docker文件"
DOCKER_FILES=(
    "docker-compose.optimized.yml"
    "docker-compose.yml"
    "Dockerfile"
    "Dockerfile.optimized"
)

echo -e "${YELLOW}是否删除Docker相关文件？(y/N):${NC}"
read -p "" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for docker in "${DOCKER_FILES[@]}"; do
        if [ -f "$docker" ]; then
            rm "$docker"
            echo "  ✅ 删除: $docker"
        fi
    done
fi

# 清理k8s目录
if [ -d "k8s" ]; then
    echo -e "${YELLOW}是否删除k8s部署配置？(y/N):${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "k8s"
        echo "  ✅ 删除目录: k8s"
    fi
fi

# 清理deploy目录
if [ -d "deploy" ]; then
    echo -e "${YELLOW}是否删除deploy目录？(y/N):${NC}"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "deploy"
        echo "  ✅ 删除目录: deploy"
    fi
fi

# 保留的重要文件列表
echo
log_success "清理完成！保留的重要文件："
echo "📁 核心代码："
echo "  • manage.py"
echo "  • wsgi.py, asgi.py, urls.py, views.py"
echo "  • apps/ (应用代码)"
echo "  • config/ (配置)"
echo "  • templates/ (模板)"
echo "  • static/ (静态文件)"
echo "  • requirements/ (依赖)"

echo
echo "⚙️ 配置文件："
echo "  • requirements.txt"
echo "  • env.example"
echo "  • nginx.conf"
echo "  • pyproject.toml, pytest.ini, setup.cfg"
echo "  • Makefile"

echo
echo "🚀 部署文件："
echo "  • start_services.sh (服务启动)"
echo "  • auto_install_all_deps.sh (依赖安装)"

echo
echo "📖 文档："
echo "  • README.md"

echo
echo -e "${GREEN}🎉 项目清理完成！现在结构更简洁了。${NC}"
echo -e "${BLUE}下一步：运行简单部署脚本${NC}"
