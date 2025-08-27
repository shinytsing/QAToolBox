#!/bin/bash
# 清理不需要的部署脚本
# 保留最优化的阿里云一键部署脚本

echo "🧹 开始清理不需要的部署脚本..."

# 要删除的脚本列表（保留最优化的）
SCRIPTS_TO_DELETE=(
    "deploy_aliyun_one_click.sh"
    "deploy_aliyun_fixed.sh"
    "enterprise_smart_deploy.sh"
    "enterprise_full_deploy.sh"
    "deploy_complete_final.sh"
    "deploy_complete_full_features.sh"
    "deploy_one_click_ultimate.sh"
    "deploy_complete_ubuntu.sh"
    "deploy_ubuntu_production.sh"
    "deploy_robust_final.sh"
    "deploy_modeshift_complete.sh"
    "deploy_full_project.sh"
    "deploy_local_project.sh"
    "deploy_complete_with_all_deps.sh"
    "deploy_ubuntu24_fixed.sh"
    "deploy_china_fast.sh"
    "deploy_china_fixed.sh"
    "deploy_china.sh"
    "deploy_with_gitee.sh"
    "deploy_manual_docker.sh"
    "deploy_simple.sh"
    "deploy_quick_start.sh"
    "deploy_smart_fix.sh"
    "fresh_start_deploy.sh"
    "fresh_deploy_from_git.sh"
    "simple_direct_deploy.sh"
    "quick_deploy.sh"
    "one_line_deploy.sh"
    "install.sh"
    "emergency_nuclear_deploy.sh"
    "ultimate_emergency_fix.sh"
    "final_emergency_fix.sh"
    "ultimate_fix.sh"
    "final_fix_deployment.sh"
    "smart_fix_deploy.sh"
    "keep_full_features_fix.sh"
    "fix_current_deploy.sh"
    "fix_deployment_issues.sh"
    "fix_final_frontend_issues.sh"
    "fix_frontend_display.sh"
    "fix_dependencies_and_settings.sh"
    "fix_missing_deps.sh"
    "fix_ssl_setup.sh"
    "fix_captcha_and_dependencies.sh"
    "fix_python_distutils.sh"
    "fix_ubuntu24_deps.sh"
    "fix_ubuntu_24_packages.sh"
    "fix_ubuntu_download_speed.sh"
    "fix_apt_pkg.sh"
    "fix_user_deploy.sh"
    "fix_psutil_deploy.sh"
    "fix_502_error.sh"
    "fix_syntax_error.sh"
    "fix_image_libs_conflict.sh"
    "fix_static_and_urls.sh"
    "fix_nginx_ssl_config.sh"
    "fix_and_start_django.sh"
    "quick_fix_now.sh"
    "quick_fix_permissions.sh"
    "quick_local_fix.sh"
    "emergency_fix_deployment.sh"
    "kill_emergency_mode.sh"
    "diagnose_frontend.sh"
    "find_missing_space.sh"
    "find_space_hog.sh"
    "find_project.sh"
    "cleanup_project.sh"
    "start_services.sh"
    "setup_auto_deploy.sh"
    "test_deployment.sh"
    "commit_deployment.sh"
    "backup.sh"
    "docker-health-check.sh"
    "monitor.sh"
    "auto_install_all_deps.sh"
    "install_missing_dependencies.sh"
)

# 要保留的脚本（最优化的）
SCRIPTS_TO_KEEP=(
    "deploy_aliyun_ultimate.sh"  # 新创建的终极部署脚本
)

echo "📋 要删除的脚本数量: ${#SCRIPTS_TO_DELETE[@]}"
echo "💎 要保留的脚本: ${SCRIPTS_TO_KEEP[*]}"

# 确认删除
read -p "⚠️  确定要删除这些脚本吗？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消删除操作"
    exit 1
fi

# 删除脚本
deleted_count=0
for script in "${SCRIPTS_TO_DELETE[@]}"; do
    if [ -f "$script" ]; then
        rm -f "$script"
        echo "🗑️  已删除: $script"
        ((deleted_count++))
    fi
done

echo ""
echo "✅ 清理完成！"
echo "📊 删除了 $deleted_count 个脚本"
echo "💎 保留了最优化的部署脚本: ${SCRIPTS_TO_KEEP[*]}"
echo ""
echo "🚀 现在可以使用以下命令进行阿里云一键部署："
echo "   sudo bash deploy_aliyun_ultimate.sh"
