from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
import logging
from ..services.clash_service import clash_service
from ..services.clash_config_manager import ClashConfigManager
import platform

logger = logging.getLogger(__name__)


def clash_dashboard(request):
    """Clash内嵌代理仪表板"""
    return render(request, "tools/clash_dashboard.html")


@csrf_exempt
@require_http_methods(["GET"])
def clash_status_api(request):
    """获取Clash服务状态"""
    try:
        status = clash_service.get_status()
        return JsonResponse({"success": True, "data": status})
    except Exception as e:
        logger.error(f"获取Clash状态失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def clash_start_api(request):
    """启动Clash服务"""
    try:
        success, message = clash_service.start_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"启动Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_stop_api(request):
    """停止Clash服务"""
    try:
        success, message = clash_service.stop_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"停止Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_restart_api(request):
    """重启Clash服务"""
    try:
        success, message = clash_service.restart_clash()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"重启Clash失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_test_connection_api(request):
    """测试Clash连接"""
    try:
        success, message = clash_service.test_connection()
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"测试Clash连接失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_proxy_info_api(request):
    """获取代理信息 - 隐藏敏感信息"""
    try:
        proxy_info = clash_service.get_proxy_info()

        # 隐藏敏感信息，只返回基本信息
        safe_proxy_info = {
            "status": proxy_info.get("status", "unknown"),
            "current_proxy": proxy_info.get("current_proxy", ""),
            "available_proxies": len(proxy_info.get("proxies", [])),
            "proxy_groups": proxy_info.get("proxy_groups", []),
            "connection_status": proxy_info.get("connection_status", "unknown"),
        }

        return JsonResponse({"success": True, "data": safe_proxy_info})
    except Exception as e:
        logger.error(f"获取代理信息失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_switch_proxy_api(request):
    """切换代理"""
    try:
        data = json.loads(request.body)
        group = data.get("group", "PROXY")
        proxy = data.get("proxy")

        if not proxy:
            return JsonResponse({"success": False, "error": "请指定代理名称"})

        success, message = clash_service.switch_proxy(group, proxy)
        return JsonResponse({"success": success, "message": message})
    except Exception as e:
        logger.error(f"切换代理失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_install_api(request):
    """安装Clash"""
    try:
        success, message = clash_service.install_clash()

        if success:
            return JsonResponse({"success": True, "message": message, "type": "success"})
        else:
            # 安装失败，提供详细的错误信息和解决方案
            return JsonResponse(
                {
                    "success": False,
                    "message": message,
                    "type": "error",
                    "solutions": _get_clash_install_solutions(),
                    "manual_guide": _get_manual_install_guide(),
                }
            )

    except Exception as e:
        logger.error(f"安装Clash失败: {e}")
        return JsonResponse(
            {
                "success": False,
                "message": f"安装过程中发生错误: {str(e)}",
                "type": "error",
                "solutions": _get_clash_install_solutions(),
                "manual_guide": _get_manual_install_guide(),
            }
        )


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def clash_config_api(request):
    """获取Clash配置 - 隐藏敏感信息"""
    try:
        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config = config_manager.export_config()

        # 隐藏敏感配置信息
        safe_config = {
            "port": config.get("port", 7890),
            "socks-port": config.get("socks-port", 7891),
            "allow-lan": config.get("allow-lan", False),
            "mode": config.get("mode", "rule"),
            "log-level": config.get("log-level", "info"),
            "external-controller": config.get("external-controller", "127.0.0.1:9090"),
        }

        # 获取代理列表但隐藏敏感信息
        proxies = config_manager.get_proxy_list()
        safe_proxies = []
        for proxy in proxies:
            safe_proxy = {
                "name": proxy.get("name", ""),
                "type": proxy.get("type", ""),
                "server": proxy.get("server", ""),
                "port": proxy.get("port", ""),
                "country": proxy.get("country", ""),
                "city": proxy.get("city", ""),
            }
            # 隐藏密码、密钥等敏感信息
            safe_proxies.append(safe_proxy)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "config": safe_config,
                    "proxies": safe_proxies,
                    "proxy_groups": config_manager.get_proxy_groups(),
                    "rules": config_manager.get_rules(),
                },
            }
        )
    except Exception as e:
        logger.error(f"获取Clash配置失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_update_config_api(request):
    """更新Clash配置"""
    try:
        data = json.loads(request.body)
        config_data = data.get("config")

        if not config_data:
            return JsonResponse({"success": False, "error": "请提供配置数据"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        success = config_manager.import_config(config_data)

        if success:
            config_manager.save_config()
            return JsonResponse({"success": True, "message": "配置更新成功"})
        else:
            return JsonResponse({"success": False, "error": "配置格式错误"})
    except Exception as e:
        logger.error(f"更新Clash配置失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_add_proxy_api(request):
    """添加代理节点"""
    try:
        data = json.loads(request.body)
        proxy_config = data.get("proxy")

        if not proxy_config:
            return JsonResponse({"success": False, "error": "请提供代理配置"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config_manager.add_proxy(proxy_config)
        config_manager.save_config()

        return JsonResponse({"success": True, "message": "代理节点添加成功"})
    except Exception as e:
        logger.error(f"添加代理节点失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def clash_remove_proxy_api(request):
    """移除代理节点"""
    try:
        data = json.loads(request.body)
        proxy_name = data.get("proxy_name")

        if not proxy_name:
            return JsonResponse({"success": False, "error": "请指定代理名称"})

        config_manager = ClashConfigManager(clash_service.clash_config_path)
        config_manager.remove_proxy(proxy_name)
        config_manager.save_config()

        return JsonResponse({"success": True, "message": "代理节点移除成功"})
    except Exception as e:
        logger.error(f"移除代理节点失败: {e}")
        return JsonResponse({"success": False, "error": str(e)})


def _get_clash_install_solutions():
    """获取Clash安装解决方案"""
    system = platform.system().lower()

    solutions = [
        {
            "title": "方案1: 使用包管理器安装 (推荐)",
            "description": "这是最简单快捷的安装方式",
            "commands": _get_package_manager_commands(system),
            "difficulty": "简单",
        },
        {
            "title": "方案2: 下载图形界面版本",
            "description": "适合不熟悉命令行的用户",
            "links": _get_gui_download_links(system),
            "difficulty": "简单",
        },
        {
            "title": "方案3: 手动下载二进制文件",
            "description": "适合需要自定义安装位置的用户",
            "commands": _get_manual_download_commands(system),
            "difficulty": "中等",
        },
        {
            "title": "方案4: 使用镜像站下载",
            "description": "适合网络访问GitHub困难的用户",
            "commands": _get_mirror_download_commands(system),
            "difficulty": "中等",
        },
    ]

    return solutions


def _get_package_manager_commands(system):
    """获取包管理器安装命令"""
    if system == "darwin":  # macOS
        return [
            "brew install clash",
            '# 如果没有Homebrew，先安装: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        ]
    elif system == "linux":
        return [
            "# Ubuntu/Debian:",
            "sudo apt update && sudo apt install clash",
            "",
            "# CentOS/RHEL:",
            "sudo yum install clash",
            "",
            "# Arch Linux:",
            "sudo pacman -S clash",
        ]
    elif system == "windows":
        return [
            "# 使用Chocolatey:",
            "choco install clash",
            "",
            "# 如果没有Chocolatey，先安装:",
            "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
        ]
    else:
        return ["请查看官方文档获取安装方法"]


def _get_gui_download_links(system):
    """获取图形界面下载链接"""
    if system == "darwin":  # macOS
        return [
            {"name": "ClashX", "url": "https://github.com/yichengchen/clashX/releases", "description": "macOS专用图形界面版本"}
        ]
    elif system == "windows":
        return [
            {
                "name": "Clash for Windows",
                "url": "https://github.com/Fndroid/clash_for_windows_pkg/releases",
                "description": "Windows专用图形界面版本",
            }
        ]
    else:
        return [
            {
                "name": "ClashX Pro",
                "url": "https://github.com/yichengchen/clashX/releases",
                "description": "跨平台图形界面版本",
            }
        ]


def _get_manual_download_commands(system):
    """获取手动下载命令"""
    arch = platform.machine().lower()

    if system == "darwin":  # macOS
        if arch in ["arm64", "aarch64"]:
            return [
                "curl -L https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
        else:
            return [
                "curl -L https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
    elif system == "linux":
        if arch in ["arm64", "aarch64"]:
            return [
                "wget https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                "gunzip clash-linux-arm64.gz",
                "chmod +x clash-linux-arm64",
                "sudo mv clash-linux-arm64 /usr/local/bin/clash",
            ]
        else:
            return [
                "wget https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                "gunzip clash-linux-amd64.gz",
                "chmod +x clash-linux-amd64",
                "sudo mv clash-linux-amd64 /usr/local/bin/clash",
            ]
    elif system == "windows":
        return [
            'Invoke-WebRequest -Uri "https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz" -OutFile "clash.gz"',
            "# 使用7-Zip或其他工具解压gz文件",
            "# 将解压后的文件重命名为clash.exe并放到PATH目录中",
        ]
    else:
        return ["请访问 https://github.com/Dreamacro/clash/releases/latest 下载适合您系统的版本"]


def _get_mirror_download_commands(system):
    """获取镜像站下载命令"""
    arch = platform.machine().lower()

    if system == "darwin":  # macOS
        if arch in ["arm64", "aarch64"]:
            return [
                "curl -L https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
        else:
            return [
                "curl -L https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz -o clash.gz",
                "gunzip clash.gz",
                "chmod +x clash",
                "sudo mv clash /usr/local/bin/",
            ]
    elif system == "linux":
        if arch in ["arm64", "aarch64"]:
            return [
                "wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                "gunzip clash-linux-arm64.gz",
                "chmod +x clash-linux-arm64",
                "sudo mv clash-linux-arm64 /usr/local/bin/clash",
            ]
        else:
            return [
                "wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                "gunzip clash-linux-amd64.gz",
                "chmod +x clash-linux-amd64",
                "sudo mv clash-linux-amd64 /usr/local/bin/clash",
            ]
    else:
        return ["请使用镜像站访问: https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest"]


def _get_manual_install_guide():
    """获取详细的手动安装指南"""
    system = platform.system().lower()
    arch = platform.machine().lower()

    guide = {"system_info": f"{system} ({arch})", "steps": [], "troubleshooting": []}

    if system == "darwin":  # macOS
        guide["steps"] = [
            "1. 打开终端 (Terminal)",
            "2. 检查是否已安装Homebrew: brew --version",
            '3. 如果没有Homebrew，先安装: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            "4. 安装Clash: brew install clash",
            "5. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = [
            "如果Homebrew安装失败，请检查网络连接",
            "如果权限不足，使用sudo运行命令",
            "如果仍然失败，尝试下载ClashX图形界面版本",
        ]
    elif system == "linux":
        guide["steps"] = [
            "1. 打开终端",
            "2. 更新包管理器: sudo apt update (Ubuntu/Debian) 或 sudo yum update (CentOS/RHEL)",
            "3. 安装Clash: sudo apt install clash (Ubuntu/Debian) 或 sudo yum install clash (CentOS/RHEL)",
            "4. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = ["如果包管理器中没有clash，尝试手动下载", "确保有sudo权限", "检查网络连接是否正常"]
    elif system == "windows":
        guide["steps"] = [
            "1. 以管理员身份打开PowerShell",
            "2. 检查是否已安装Chocolatey: choco --version",
            "3. 如果没有Chocolatey，先安装 (见上面的命令)",
            "4. 安装Clash: choco install clash",
            "5. 验证安装: clash --version",
        ]
        guide["troubleshooting"] = [
            "如果PowerShell执行策略限制，运行: Set-ExecutionPolicy RemoteSigned",
            "确保以管理员身份运行",
            "如果仍然失败，下载Clash for Windows图形界面版本",
        ]
    else:
        guide["steps"] = [
            "1. 访问 https://github.com/Dreamacro/clash/releases/latest",
            "2. 下载适合您系统的版本",
            "3. 解压文件并设置执行权限",
            "4. 将可执行文件放到系统PATH目录中",
        ]
        guide["troubleshooting"] = ["确保下载的是正确的系统架构版本", "检查文件权限设置", "确保可执行文件在系统PATH中"]

    return guide
