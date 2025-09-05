#!/usr/bin/env python3
"""
浏览器代理配置服务
自动配置Chrome/Edge/Safari等浏览器的代理设置
"""

import json
import logging
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class BrowserProxyConfig:
    """浏览器代理配置管理器"""

    def __init__(self, proxy_host: str = "127.0.0.1", proxy_port: int = 7890):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.system = platform.system().lower()

    def get_chrome_preferences_path(self) -> Optional[Path]:
        """获取Chrome配置文件路径"""
        if self.system == "darwin":  # macOS
            return Path.home() / "Library/Application Support/Google/Chrome/Default/Preferences"
        elif self.system == "windows":
            return Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Preferences"
        elif self.system == "linux":
            return Path.home() / ".config/google-chrome/Default/Preferences"
        return None

    def get_edge_preferences_path(self) -> Optional[Path]:
        """获取Edge配置文件路径"""
        if self.system == "darwin":  # macOS
            return Path.home() / "Library/Application Support/Microsoft Edge/Default/Preferences"
        elif self.system == "windows":
            return Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Preferences"
        elif self.system == "linux":
            return Path.home() / ".config/microsoft-edge/Default/Preferences"
        return None

    def backup_preferences(self, prefs_path: Path) -> bool:
        """备份浏览器配置文件"""
        try:
            if prefs_path.exists():
                backup_path = prefs_path.with_suffix(".backup")
                shutil.copy2(prefs_path, backup_path)
                logger.info(f"已备份配置文件: {backup_path}")
                return True
        except Exception as e:
            logger.error(f"备份配置文件失败: {e}")
        return False

    def configure_chrome_proxy(self) -> Tuple[bool, str]:
        """配置Chrome浏览器代理"""
        try:
            prefs_path = self.get_chrome_preferences_path()
            if not prefs_path or not prefs_path.exists():
                return False, "Chrome配置文件不存在，请先启动Chrome浏览器"

            # 备份原配置
            self.backup_preferences(prefs_path)

            # 读取现有配置
            with open(prefs_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)

            # 设置代理配置
            proxy_config = {
                "mode": "fixed_servers",
                "rules": {"singleProxy": {"scheme": "http", "host": self.proxy_host, "port": self.proxy_port}},
            }

            # 更新配置
            if "profile" not in prefs:
                prefs["profile"] = {}
            if "content_settings" not in prefs["profile"]:
                prefs["profile"]["content_settings"] = {}
            if "preferences" not in prefs["profile"]["content_settings"]:
                prefs["profile"]["content_settings"]["preferences"] = {}

            prefs["profile"]["content_settings"]["preferences"]["proxy"] = proxy_config

            # 保存配置
            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)

            logger.info("Chrome代理配置已更新")
            return True, "Chrome代理配置成功"

        except Exception as e:
            logger.error(f"配置Chrome代理失败: {e}")
            return False, f"配置Chrome代理失败: {str(e)}"

    def configure_edge_proxy(self) -> Tuple[bool, str]:
        """配置Edge浏览器代理"""
        try:
            prefs_path = self.get_edge_preferences_path()
            if not prefs_path or not prefs_path.exists():
                return False, "Edge配置文件不存在，请先启动Edge浏览器"

            # 备份原配置
            self.backup_preferences(prefs_path)

            # 读取现有配置
            with open(prefs_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)

            # 设置代理配置
            proxy_config = {
                "mode": "fixed_servers",
                "rules": {"singleProxy": {"scheme": "http", "host": self.proxy_host, "port": self.proxy_port}},
            }

            # 更新配置
            if "profile" not in prefs:
                prefs["profile"] = {}
            if "content_settings" not in prefs["profile"]:
                prefs["profile"]["content_settings"] = {}
            if "preferences" not in prefs["profile"]["content_settings"]:
                prefs["profile"]["content_settings"]["preferences"] = {}

            prefs["profile"]["content_settings"]["preferences"]["proxy"] = proxy_config

            # 保存配置
            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)

            logger.info("Edge代理配置已更新")
            return True, "Edge代理配置成功"

        except Exception as e:
            logger.error(f"配置Edge代理失败: {e}")
            return False, f"配置Edge代理失败: {str(e)}"

    def configure_safari_proxy(self) -> Tuple[bool, str]:
        """配置Safari浏览器代理（macOS）"""
        if self.system != "darwin":
            return False, "Safari代理配置仅支持macOS系统"

        try:
            # 使用networksetup命令配置系统代理
            cmd = [
                "networksetup",
                "-setwebproxy",
                "Wi-Fi",  # 网络服务名称，可能需要调整
                self.proxy_host,
                str(self.proxy_port),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # 同时设置HTTPS代理
                cmd_https = ["networksetup", "-setsecurewebproxy", "Wi-Fi", self.proxy_host, str(self.proxy_port)]
                subprocess.run(cmd_https, capture_output=True, text=True)

                logger.info("Safari代理配置已更新")
                return True, "Safari代理配置成功"
            else:
                return False, f"Safari代理配置失败: {result.stderr}"

        except Exception as e:
            logger.error(f"配置Safari代理失败: {e}")
            return False, f"配置Safari代理失败: {str(e)}"

    def configure_system_proxy(self) -> Tuple[bool, str]:
        """配置系统全局代理"""
        try:
            if self.system == "darwin":  # macOS
                return self._configure_macos_system_proxy()
            elif self.system == "windows":
                return self._configure_windows_system_proxy()
            elif self.system == "linux":
                return self._configure_linux_system_proxy()
            else:
                return False, f"不支持的操作系统: {self.system}"

        except Exception as e:
            logger.error(f"配置系统代理失败: {e}")
            return False, f"配置系统代理失败: {str(e)}"

    def _configure_macos_system_proxy(self) -> Tuple[bool, str]:
        """配置macOS系统代理"""
        try:
            # 获取当前网络服务
            result = subprocess.run(["networksetup", "-listallnetworkservices"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "无法获取网络服务列表"

            # 查找Wi-Fi或以太网服务
            services = result.stdout.split("\n")[1:]  # 跳过第一行标题
            network_service = None
            for service in services:
                if service.strip() and ("Wi-Fi" in service or "Ethernet" in service):
                    network_service = service.strip()
                    break

            if not network_service:
                return False, "未找到可用的网络服务"

            # 设置HTTP代理
            cmd_http = ["networksetup", "-setwebproxy", network_service, self.proxy_host, str(self.proxy_port)]

            result = subprocess.run(cmd_http, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"设置HTTP代理失败: {result.stderr}"

            # 设置HTTPS代理
            cmd_https = ["networksetup", "-setsecurewebproxy", network_service, self.proxy_host, str(self.proxy_port)]

            result = subprocess.run(cmd_https, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"设置HTTPS代理失败: {result.stderr}"

            logger.info(f"macOS系统代理配置成功，网络服务: {network_service}")
            return True, f"macOS系统代理配置成功，网络服务: {network_service}"

        except Exception as e:
            return False, f"配置macOS系统代理失败: {str(e)}"

    def _configure_windows_system_proxy(self) -> Tuple[bool, str]:
        """配置Windows系统代理"""
        try:
            import winreg

            # 设置注册表项
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                # 启用代理
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)

                # 设置代理服务器
                proxy_server = f"{self.proxy_host}:{self.proxy_port}"
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)

                # 设置代理覆盖
                winreg.SetValueEx(
                    key,
                    "ProxyOverride",
                    0,
                    winreg.REG_SZ,
                    "localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*",
                )

            logger.info("Windows系统代理配置成功")
            return True, "Windows系统代理配置成功"

        except Exception as e:
            return False, f"配置Windows系统代理失败: {str(e)}"

    def _configure_linux_system_proxy(self) -> Tuple[bool, str]:
        """配置Linux系统代理"""
        try:
            # 设置环境变量
            proxy_env = {
                "http_proxy": f"http://{self.proxy_host}:{self.proxy_port}",
                "https_proxy": f"http://{self.proxy_host}:{self.proxy_port}",
                "HTTP_PROXY": f"http://{self.proxy_host}:{self.proxy_port}",
                "HTTPS_PROXY": f"http://{self.proxy_host}:{self.proxy_port}",
                "no_proxy": "localhost,127.0.0.1,::1",
                "NO_PROXY": "localhost,127.0.0.1,::1",
            }

            # 写入到shell配置文件
            shell_configs = [".bashrc", ".zshrc", ".profile"]
            for config_file in shell_configs:
                config_path = Path.home() / config_file
                if config_path.exists():
                    with open(config_path, "a") as f:
                        f.write("\n# Clash代理配置\n")
                        for key, value in proxy_env.items():
                            f.write(f'export {key}="{value}"\n')

            logger.info("Linux系统代理配置成功")
            return True, "Linux系统代理配置成功"

        except Exception as e:
            return False, f"配置Linux系统代理失败: {str(e)}"

    def disable_proxy(self) -> Tuple[bool, str]:
        """禁用代理"""
        try:
            if self.system == "darwin":  # macOS
                return self._disable_macos_proxy()
            elif self.system == "windows":
                return self._disable_windows_proxy()
            elif self.system == "linux":
                return self._disable_linux_proxy()
            else:
                return False, f"不支持的操作系统: {self.system}"

        except Exception as e:
            logger.error(f"禁用代理失败: {e}")
            return False, f"禁用代理失败: {str(e)}"

    def _disable_macos_proxy(self) -> Tuple[bool, str]:
        """禁用macOS代理"""
        try:
            # 获取网络服务
            result = subprocess.run(["networksetup", "-listallnetworkservices"], capture_output=True, text=True)
            if result.returncode != 0:
                return False, "无法获取网络服务列表"

            services = result.stdout.split("\n")[1:]
            network_service = None
            for service in services:
                if service.strip() and ("Wi-Fi" in service or "Ethernet" in service):
                    network_service = service.strip()
                    break

            if not network_service:
                return False, "未找到可用的网络服务"

            # 禁用HTTP代理
            cmd_http = ["networksetup", "-setwebproxystate", network_service, "off"]
            subprocess.run(cmd_http, capture_output=True, text=True)

            # 禁用HTTPS代理
            cmd_https = ["networksetup", "-setsecurewebproxystate", network_service, "off"]
            subprocess.run(cmd_https, capture_output=True, text=True)

            logger.info("macOS代理已禁用")
            return True, "macOS代理已禁用"

        except Exception as e:
            return False, f"禁用macOS代理失败: {str(e)}"

    def _disable_windows_proxy(self) -> Tuple[bool, str]:
        """禁用Windows代理"""
        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)

            logger.info("Windows代理已禁用")
            return True, "Windows代理已禁用"

        except Exception as e:
            return False, f"禁用Windows代理失败: {str(e)}"

    def _disable_linux_proxy(self) -> Tuple[bool, str]:
        """禁用Linux代理"""
        try:
            # 清除环境变量
            shell_configs = [".bashrc", ".zshrc", ".profile"]
            for config_file in shell_configs:
                config_path = Path.home() / config_file
                if config_path.exists():
                    # 读取文件内容
                    with open(config_path, "r") as f:
                        lines = f.readlines()

                    # 过滤掉代理相关的行
                    filtered_lines = []
                    skip_next = False
                    for line in lines:
                        if "# Clash代理配置" in line:
                            skip_next = True
                            continue
                        if skip_next and line.startswith("export ") and ("proxy" in line.lower() or "PROXY" in line):
                            continue
                        if skip_next and line.strip() == "":
                            skip_next = False
                            continue
                        filtered_lines.append(line)

                    # 写回文件
                    with open(config_path, "w") as f:
                        f.writelines(filtered_lines)

            logger.info("Linux代理已禁用")
            return True, "Linux代理已禁用"

        except Exception as e:
            return False, f"禁用Linux代理失败: {str(e)}"

    def get_proxy_status(self) -> Dict:
        """获取当前代理状态"""
        status = {
            "system": self.system,
            "proxy_host": self.proxy_host,
            "proxy_port": self.proxy_port,
            "system_proxy_enabled": False,
            "browsers": {},
        }

        try:
            if self.system == "darwin":
                # 检查macOS系统代理状态
                result = subprocess.run(["networksetup", "-getwebproxy", "Wi-Fi"], capture_output=True, text=True)
                if result.returncode == 0 and "Enabled: Yes" in result.stdout:
                    status["system_proxy_enabled"] = True

            # 检查浏览器配置
            chrome_path = self.get_chrome_preferences_path()
            if chrome_path and chrome_path.exists():
                try:
                    with open(chrome_path, "r", encoding="utf-8") as f:
                        prefs = json.load(f)
                    if "profile" in prefs and "content_settings" in prefs["profile"]:
                        if "preferences" in prefs["profile"]["content_settings"]:
                            if "proxy" in prefs["profile"]["content_settings"]["preferences"]:
                                status["browsers"]["chrome"] = True
                except Exception:
                    pass

            edge_path = self.get_edge_preferences_path()
            if edge_path and edge_path.exists():
                try:
                    with open(edge_path, "r", encoding="utf-8") as f:
                        prefs = json.load(f)
                    if "profile" in prefs and "content_settings" in prefs["profile"]:
                        if "preferences" in prefs["profile"]["content_settings"]:
                            if "proxy" in prefs["profile"]["content_settings"]["preferences"]:
                                status["browsers"]["edge"] = True
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"获取代理状态失败: {e}")

        return status

    def auto_configure_all(self) -> Dict:
        """自动配置所有可用的代理"""
        results = {
            "system_proxy": {"success": False, "message": ""},
            "chrome": {"success": False, "message": ""},
            "edge": {"success": False, "message": ""},
            "safari": {"success": False, "message": ""},
        }

        # 配置系统代理
        success, message = self.configure_system_proxy()
        results["system_proxy"] = {"success": success, "message": message}

        # 配置Chrome
        success, message = self.configure_chrome_proxy()
        results["chrome"] = {"success": success, "message": message}

        # 配置Edge
        success, message = self.configure_edge_proxy()
        results["edge"] = {"success": success, "message": message}

        # 配置Safari (仅macOS)
        if self.system == "darwin":
            success, message = self.configure_safari_proxy()
            results["safari"] = {"success": success, "message": message}

        return results


# 全局实例
browser_proxy_config = BrowserProxyConfig()
