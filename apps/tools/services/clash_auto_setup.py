import os
import sys
import subprocess
import platform
import requests
import logging
from typing import Tuple, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ClashAutoSetup:
    """Clash自动安装和配置工具"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.arch = platform.machine().lower()
        self.clash_dir = Path.home() / '.clash'
        self.clash_binary = None
        
    def detect_system(self) -> Dict:
        """检测系统信息"""
        return {
            'system': self.system,
            'arch': self.arch,
            'python_version': sys.version,
            'platform': platform.platform()
        }
    
    def check_clash_installed(self) -> Tuple[bool, str]:
        """检查Clash是否已安装"""
        possible_paths = [
            '/usr/local/bin/clash',
            '/usr/bin/clash',
            '/opt/homebrew/bin/clash',
            str(self.clash_dir / 'clash'),
            str(self.clash_dir / 'clash.exe'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.clash_binary = path
                return True, f"找到Clash: {path}"
        
        return False, "未找到Clash安装"
    
    def install_clash_macos(self) -> Tuple[bool, str]:
        """在macOS上安装Clash"""
        try:
            # 检查Homebrew
            if subprocess.run(['which', 'brew'], capture_output=True).returncode == 0:
                # 使用Homebrew安装
                result = subprocess.run(['brew', 'install', 'clash'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.clash_binary = '/opt/homebrew/bin/clash'
                    return True, "通过Homebrew安装Clash成功"
            
            # 下载二进制文件
            return self.download_clash_binary()
            
        except Exception as e:
            return False, f"macOS安装失败: {str(e)}"
    
    def install_clash_linux(self) -> Tuple[bool, str]:
        """在Linux上安装Clash"""
        try:
            # 尝试通过包管理器安装
            if subprocess.run(['which', 'apt'], capture_output=True).returncode == 0:
                # Ubuntu/Debian
                result = subprocess.run(['sudo', 'apt', 'update'], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    result = subprocess.run(['sudo', 'apt', 'install', '-y', 'clash'], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        self.clash_binary = '/usr/bin/clash'
                        return True, "通过apt安装Clash成功"
            
            elif subprocess.run(['which', 'yum'], capture_output=True).returncode == 0:
                # CentOS/RHEL
                result = subprocess.run(['sudo', 'yum', 'install', '-y', 'clash'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.clash_binary = '/usr/bin/clash'
                    return True, "通过yum安装Clash成功"
            
            # 下载二进制文件
            return self.download_clash_binary()
            
        except Exception as e:
            return False, f"Linux安装失败: {str(e)}"
    
    def install_clash_windows(self) -> Tuple[bool, str]:
        """在Windows上安装Clash"""
        try:
            # 检查Chocolatey
            if subprocess.run(['where', 'choco'], capture_output=True, shell=True).returncode == 0:
                result = subprocess.run(['choco', 'install', 'clash', '-y'], 
                                      capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    self.clash_binary = 'clash'
                    return True, "通过Chocolatey安装Clash成功"
            
            # 下载二进制文件
            return self.download_clash_binary()
            
        except Exception as e:
            return False, f"Windows安装失败: {str(e)}"
    
    def download_clash_binary(self) -> Tuple[bool, str]:
        """下载Clash二进制文件 - 使用多个备用源"""
        try:
            import gzip
            import shutil
            
            # 创建目录
            self.clash_dir.mkdir(exist_ok=True)
            
            # 获取下载URL列表
            urls = self.get_download_urls()
            if not urls:
                return False, f"不支持的系统架构: {self.system} {self.arch}"
            
            # 尝试每个下载源
            for i, url in enumerate(urls):
                try:
                    logger.info(f"尝试下载Clash (源 {i+1}/{len(urls)}): {url}")
                    
                    # 设置请求头，模拟浏览器
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/octet-stream, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    response = requests.get(url, stream=True, timeout=60, headers=headers, verify=True)
                    response.raise_for_status()
                    
                    # 检查文件大小
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) < 1024:  # 小于1KB可能是错误页面
                        raise Exception(f"下载文件过小，可能是错误页面: {content_length} bytes")
                    
                    # 保存压缩文件
                    compressed_path = self.clash_dir / 'clash.gz'
                    with open(compressed_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    # 解压gzip文件
                    binary_path = self.clash_dir / 'clash'
                    if self.system == 'windows':
                        binary_path = self.clash_dir / 'clash.exe'
                    
                    with gzip.open(compressed_path, 'rb') as f_in:
                        with open(binary_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # 删除压缩文件
                    compressed_path.unlink()
                    
                    # 验证文件
                    if not binary_path.exists() or binary_path.stat().st_size < 1024:
                        raise Exception("下载的文件无效或损坏")
                    
                    # 设置执行权限
                    if self.system != 'windows':
                        os.chmod(binary_path, 0o755)
                    
                    self.clash_binary = str(binary_path)
                    return True, f"Clash下载完成: {binary_path} (源 {i+1})"
                    
                except Exception as e:
                    logger.warning(f"下载源 {i+1} 失败: {e}")
                    # 清理可能的部分下载文件
                    for cleanup_file in [self.clash_dir / 'clash', self.clash_dir / 'clash.exe', self.clash_dir / 'clash.gz']:
                        if cleanup_file.exists():
                            cleanup_file.unlink()
                    if i == len(urls) - 1:  # 最后一个源也失败了
                        return False, f"所有下载源都失败，最后错误: {str(e)}"
                    continue
            
            return False, "所有下载源都失败"
            
        except Exception as e:
            return False, f"下载Clash失败: {str(e)}"
    
    def get_download_urls(self) -> List[str]:
        """获取下载URL列表（多个备用源）"""
        urls = []
        
        if self.system == 'darwin':  # macOS
            if self.arch in ['arm64', 'aarch64']:
                urls = [
                    # 使用GitHub镜像站
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz",
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz",
                    # 原始GitHub链接
                    "https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz",
                    "https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz",
                    # 备用下载源
                    "https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz"
                ]
            else:
                urls = [
                    # 使用GitHub镜像站
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz",
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz",
                    # 原始GitHub链接
                    "https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz",
                    "https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz",
                    # 备用下载源
                    "https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz"
                ]
        elif self.system == 'linux':
            if self.arch in ['arm64', 'aarch64']:
                urls = [
                    # 使用GitHub镜像站
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz",
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                    # 原始GitHub链接
                    "https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz",
                    "https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz",
                    # 备用下载源
                    "https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz"
                ]
            else:
                urls = [
                    # 使用GitHub镜像站
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz",
                    "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                    # 原始GitHub链接
                    "https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz",
                    "https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz",
                    # 备用下载源
                    "https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz"
                ]
        elif self.system == 'windows':
            urls = [
                # 使用GitHub镜像站
                "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz",
                "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz",
                # 原始GitHub链接
                "https://github.com/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz",
                "https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz",
                # 备用下载源
                "https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz"
            ]
        
        return urls
    
    def create_default_config(self) -> Tuple[bool, str]:
        """创建默认配置"""
        try:
            config_path = self.clash_dir / 'config.yaml'
            
            config = {
                'port': 7890,
                'socks-port': 7891,
                'allow-lan': False,
                'mode': 'rule',
                'log-level': 'info',
                'external-controller': '127.0.0.1:9090',
                'secret': '',
                'dns': {
                    'enable': True,
                    'ipv6': False,
                    'nameserver': [
                        '223.5.5.5',
                        '180.76.76.76',
                        '119.29.29.29',
                        '8.8.8.8',
                        '1.1.1.1'
                    ],
                    'fallback': [
                        '8.8.8.8',
                        '1.1.1.1',
                        'tls://dns.google:853'
                    ]
                },
                'proxies': [],
                'proxy-groups': [
                    {
                        'name': 'PROXY',
                        'type': 'select',
                        'proxies': ['DIRECT']
                    },
                    {
                        'name': 'Auto',
                        'type': 'url-test',
                        'url': 'https://www.youtube.com/favicon.ico',
                        'interval': 300,
                        'proxies': []
                    }
                ],
                'rules': [
                    'DOMAIN-SUFFIX,cn,DIRECT',
                    'GEOIP,CN,DIRECT',
                    'MATCH,PROXY'
                ]
            }
            
            import yaml
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return True, f"默认配置已创建: {config_path}"
            
        except Exception as e:
            return False, f"创建配置失败: {str(e)}"
    
    def setup_system_proxy(self) -> Tuple[bool, str]:
        """设置系统代理"""
        try:
            if self.system == 'darwin':  # macOS
                return self.setup_macos_proxy()
            elif self.system == 'linux':
                return self.setup_linux_proxy()
            elif self.system == 'windows':
                return self.setup_windows_proxy()
            else:
                return False, f"不支持的系统: {self.system}"
                
        except Exception as e:
            return False, f"设置系统代理失败: {str(e)}"
    
    def setup_macos_proxy(self) -> Tuple[bool, str]:
        """设置macOS系统代理"""
        try:
            # 使用networksetup命令设置代理
            subprocess.run([
                'networksetup', '-setwebproxy', 'Wi-Fi', '127.0.0.1', '7890'
            ], check=True)
            
            subprocess.run([
                'networksetup', '-setsecurewebproxy', 'Wi-Fi', '127.0.0.1', '7890'
            ], check=True)
            
            subprocess.run([
                'networksetup', '-setsocksfirewallproxy', 'Wi-Fi', '127.0.0.1', '7891'
            ], check=True)
            
            return True, "macOS系统代理设置成功"
            
        except Exception as e:
            return False, f"macOS代理设置失败: {str(e)}"
    
    def setup_linux_proxy(self) -> Tuple[bool, str]:
        """设置Linux系统代理"""
        try:
            # 设置环境变量
            proxy_env = {
                'http_proxy': 'http://127.0.0.1:7890',
                'https_proxy': 'http://127.0.0.1:7890',
                'socks_proxy': 'socks5://127.0.0.1:7891'
            }
            
            # 写入shell配置文件
            shell_configs = ['.bashrc', '.zshrc', '.profile']
            for config_file in shell_configs:
                config_path = Path.home() / config_file
                if config_path.exists():
                    with open(config_path, 'a') as f:
                        f.write('\n# Clash代理设置\n')
                        for key, value in proxy_env.items():
                            f.write(f'export {key.upper()}={value}\n')
            
            return True, "Linux系统代理设置成功"
            
        except Exception as e:
            return False, f"Linux代理设置失败: {str(e)}"
    
    def setup_windows_proxy(self) -> Tuple[bool, str]:
        """设置Windows系统代理"""
        try:
            import winreg
            
            # 设置注册表
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                               0, winreg.KEY_WRITE)
            
            winreg.SetValueEx(key, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'ProxyServer', 0, winreg.REG_SZ, '127.0.0.1:7890')
            
            winreg.CloseKey(key)
            
            return True, "Windows系统代理设置成功"
            
        except Exception as e:
            return False, f"Windows代理设置失败: {str(e)}"
    
    def auto_setup(self) -> Tuple[bool, str, Dict]:
        """自动安装和配置Clash"""
        result = {
            'system_info': self.detect_system(),
            'clash_binary': None,
            'config_path': None,
            'proxy_setup': False
        }
        
        try:
            # 1. 检查是否已安装
            installed, msg = self.check_clash_installed()
            if not installed:
                # 2. 安装Clash
                if self.system == 'darwin':
                    success, msg = self.install_clash_macos()
                elif self.system == 'linux':
                    success, msg = self.install_clash_linux()
                elif self.system == 'windows':
                    success, msg = self.install_clash_windows()
                else:
                    return False, f"不支持的操作系统: {self.system}", result
                
                if not success:
                    return False, msg, result
            
            result['clash_binary'] = self.clash_binary
            
            # 3. 创建默认配置
            success, msg = self.create_default_config()
            if not success:
                return False, msg, result
            
            result['config_path'] = str(self.clash_dir / 'config.yaml')
            
            # 4. 设置系统代理（可选）
            success, msg = self.setup_system_proxy()
            result['proxy_setup'] = success
            
            return True, "Clash自动安装和配置完成", result
            
        except Exception as e:
            return False, f"自动安装失败: {str(e)}", result


# 全局自动安装实例
clash_auto_setup = ClashAutoSetup()
