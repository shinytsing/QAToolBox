import os
import sys
import json
import yaml
import time
import signal
import subprocess
import threading
import requests
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ClashEmbeddedService:
    """内嵌Clash代理服务管理器"""
    
    def __init__(self):
        self.clash_process = None
        self.clash_config_path = None
        self.clash_ui_port = 9090
        self.clash_http_port = 7890
        self.clash_socks_port = 7891
        self.is_running = False
        self.start_time = None
        
        # 设置Clash相关路径
        self.setup_paths()
        
        # 初始化配置
        self.init_config()
    
    def setup_paths(self):
        """设置Clash相关路径"""
        # 创建Clash配置目录
        self.clash_dir = Path(settings.BASE_DIR) / 'clash_embedded'
        self.clash_dir.mkdir(exist_ok=True)
        
        # Clash配置文件路径
        self.clash_config_path = self.clash_dir / 'config.yaml'
        
        # Clash日志文件路径
        self.clash_log_path = self.clash_dir / 'clash.log'
        
        # Clash可执行文件路径（如果存在）
        self.clash_binary_path = self.find_clash_binary()
    
    def find_clash_binary(self) -> Optional[str]:
        """查找Clash可执行文件或检测ClashX Pro"""
        # 首先检查是否有独立的clash二进制文件
        possible_paths = [
            '/usr/local/bin/clash',
            '/usr/bin/clash',
            '/opt/homebrew/bin/clash',
            str(self.clash_dir / 'clash'),
            str(self.clash_dir / 'clash.exe'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        # 检查ClashX Pro是否在运行
        if self.is_clashx_running():
            return "clashx_pro"  # 特殊标识表示使用ClashX Pro
        
        return None
    
    def is_clashx_running(self) -> bool:
        """检查ClashX Pro是否在运行"""
        try:
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'ClashX Pro'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def init_config(self):
        """初始化Clash配置"""
        if not self.clash_config_path.exists():
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认的Clash配置"""
        config = {
            'port': self.clash_http_port,
            'socks-port': self.clash_socks_port,
            'allow-lan': False,
            'mode': 'rule',
            'log-level': 'info',
            'external-controller': f'127.0.0.1:{self.clash_ui_port}',
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
        
        with open(self.clash_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"创建默认Clash配置文件: {self.clash_config_path}")
    
    def load_existing_config(self) -> Dict:
        """加载现有的Clash配置"""
        try:
            with open(self.clash_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载Clash配置失败: {e}")
            return {}
    
    def update_config_with_proxies(self, proxies: List[Dict]):
        """使用代理列表更新配置"""
        config = self.load_existing_config()
        
        # 更新代理列表
        config['proxies'] = proxies
        
        # 更新代理组
        proxy_names = [p['name'] for p in proxies]
        config['proxy-groups'][0]['proxies'] = ['Auto'] + proxy_names
        config['proxy-groups'][1]['proxies'] = proxy_names
        
        # 保存配置
        with open(self.clash_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"更新Clash配置，包含 {len(proxies)} 个代理节点")
    
    def start_clash(self) -> Tuple[bool, str]:
        """启动Clash服务"""
        if self.is_running:
            return True, "Clash服务已在运行"
        
        # 检查Clash二进制文件
        if not self.clash_binary_path:
            return False, "未找到Clash可执行文件，请先安装Clash"
        
        # 如果检测到ClashX Pro，直接返回成功
        if self.clash_binary_path == "clashx_pro":
            if self.is_clashx_running():
                self.is_running = True
                self.start_time = time.time()
                logger.info("检测到ClashX Pro正在运行，服务已就绪")
                return True, "ClashX Pro正在运行，服务已就绪"
            else:
                return False, "ClashX Pro未运行，请先启动ClashX Pro"
        
        try:
            # 启动独立的Clash进程
            cmd = [
                self.clash_binary_path,
                '-f', str(self.clash_config_path),
                '-d', str(self.clash_dir)
            ]
            
            self.clash_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # 等待服务启动
            time.sleep(2)
            
            # 检查进程是否还在运行
            if self.clash_process.poll() is None:
                self.is_running = True
                self.start_time = time.time()
                
                # 启动监控线程
                self.monitor_thread = threading.Thread(target=self._monitor_clash)
                self.monitor_thread.daemon = True
                self.monitor_thread.start()
                
                logger.info("Clash服务启动成功")
                return True, "Clash服务启动成功"
            else:
                stdout, stderr = self.clash_process.communicate()
                error_msg = stderr.decode('utf-8') if stderr else "未知错误"
                return False, f"Clash启动失败: {error_msg}"
                
        except Exception as e:
            logger.error(f"启动Clash失败: {e}")
            return False, f"启动Clash失败: {str(e)}"
    
    def stop_clash(self) -> Tuple[bool, str]:
        """停止Clash服务"""
        if not self.is_running or not self.clash_process:
            return True, "Clash服务未运行"
        
        try:
            # 终止进程组
            if os.name != 'nt':
                os.killpg(os.getpgid(self.clash_process.pid), signal.SIGTERM)
            else:
                self.clash_process.terminate()
            
            # 等待进程结束
            self.clash_process.wait(timeout=10)
            
            self.is_running = False
            self.clash_process = None
            self.start_time = None
            
            logger.info("Clash服务已停止")
            return True, "Clash服务已停止"
            
        except subprocess.TimeoutExpired:
            # 强制杀死进程
            if os.name != 'nt':
                os.killpg(os.getpgid(self.clash_process.pid), signal.SIGKILL)
            else:
                self.clash_process.kill()
            
            self.is_running = False
            self.clash_process = None
            self.start_time = None
            
            return True, "Clash服务已强制停止"
            
        except Exception as e:
            logger.error(f"停止Clash失败: {e}")
            return False, f"停止Clash失败: {str(e)}"
    
    def restart_clash(self) -> Tuple[bool, str]:
        """重启Clash服务"""
        stop_success, stop_msg = self.stop_clash()
        if not stop_success:
            return False, f"停止服务失败: {stop_msg}"
        
        time.sleep(1)
        return self.start_clash()
    
    def _monitor_clash(self):
        """监控Clash进程"""
        while self.is_running and self.clash_process:
            if self.clash_process.poll() is not None:
                # 进程已结束
                self.is_running = False
                logger.warning("Clash进程意外结束")
                break
            time.sleep(5)
    
    def get_status(self) -> Dict:
        """获取Clash服务状态"""
        # 重新检查ClashX Pro状态
        if self.clash_binary_path == "clashx_pro":
            self.is_running = self.is_clashx_running()
        
        status = {
            'is_running': self.is_running,
            'start_time': self.start_time,
            'uptime': 0,
            'http_port': self.clash_http_port,
            'socks_port': self.clash_socks_port,
            'ui_port': self.clash_ui_port,
            'config_path': str(self.clash_config_path),
            'binary_path': self.clash_binary_path,
            'has_binary': self.clash_binary_path is not None,
            'service_type': 'ClashX Pro' if self.clash_binary_path == "clashx_pro" else 'Standalone Clash'
        }
        
        if self.start_time:
            status['uptime'] = int(time.time() - self.start_time)
        
        return status
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试Clash连接"""
        if not self.is_running:
            return False, "Clash服务未运行"
        
        try:
            # 测试HTTP代理
            proxies = {
                'http': f'http://127.0.0.1:{self.clash_http_port}',
                'https': f'http://127.0.0.1:{self.clash_http_port}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, f"连接正常，IP: {data.get('origin', 'unknown')}"
            else:
                return False, f"连接失败，状态码: {response.status_code}"
                
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"
    
    def get_proxy_info(self) -> Dict:
        """获取代理信息"""
        if not self.is_running:
            return {'error': 'Clash服务未运行'}
        
        try:
            # 通过Clash API获取代理信息
            api_url = f'http://127.0.0.1:{self.clash_ui_port}/proxies'
            response = requests.get(api_url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API请求失败: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'获取代理信息失败: {str(e)}'}
    
    def switch_proxy(self, group: str, proxy: str) -> Tuple[bool, str]:
        """切换代理"""
        if not self.is_running:
            return False, "Clash服务未运行"
        
        try:
            api_url = f'http://127.0.0.1:{self.clash_ui_port}/proxies/{group}'
            data = {'name': proxy}
            
            response = requests.put(
                api_url,
                json=data,
                timeout=5
            )
            
            if response.status_code == 204:
                return True, f"已切换到代理: {proxy}"
            else:
                return False, f"切换失败: {response.status_code}"
                
        except Exception as e:
            return False, f"切换代理失败: {str(e)}"
    
    def download_clash_binary(self) -> Tuple[bool, str]:
        """下载Clash二进制文件 - 使用备用方案"""
        try:
            import platform
            import gzip
            import shutil
            system = platform.system().lower()
            arch = platform.machine().lower()
            
            # 尝试多个下载源
            download_urls = self._get_clash_download_urls(system, arch)
            
            for i, url_info in enumerate(download_urls):
                try:
                    logger.info(f"尝试下载Clash (源 {i+1}/{len(download_urls)}): {url_info['source']}")
                    
                    # 设置请求头，模拟浏览器
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/octet-stream, */*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    response = requests.get(
                        url_info['url'], 
                        stream=True, 
                        timeout=60,
                        headers=headers,
                        verify=True
                    )
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
                    if system == 'windows':
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
                    if system != 'windows':
                        os.chmod(binary_path, 0o755)
                    
                    # 更新二进制路径
                    self.clash_binary_path = str(binary_path)
                    
                    logger.info(f"Clash二进制文件下载完成: {binary_path}")
                    return True, f"Clash二进制文件下载完成 (来源: {url_info['source']})"
                    
                except Exception as e:
                    logger.warning(f"下载源 {url_info['source']} 失败: {e}")
                    # 清理可能的部分下载文件
                    for cleanup_file in [self.clash_dir / 'clash', self.clash_dir / 'clash.exe', self.clash_dir / 'clash.gz']:
                        if cleanup_file.exists():
                            cleanup_file.unlink()
                    continue
            
            return False, "所有下载源都失败，请手动安装Clash或使用包管理器"
            
        except Exception as e:
            logger.error(f"下载Clash二进制文件失败: {e}")
            return False, f"下载失败: {str(e)}"
    
    def _get_clash_download_urls(self, system: str, arch: str) -> List[Dict]:
        """获取Clash下载URL列表 - 使用多个备用源"""
        urls = []
        
        if system == 'darwin':  # macOS
            if arch in ['arm64', 'aarch64']:
                urls = [
                    # 使用GitHub镜像站
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz',
                        'source': 'GitHub镜像站 (Premium 2023.08.17)'
                    },
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz',
                        'source': 'GitHub镜像站 (Latest)'
                    },
                    # 原始GitHub链接
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz',
                        'source': 'GitHub Premium (2023.08.17)'
                    },
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-arm64.gz',
                        'source': 'GitHub Latest'
                    },
                    # 备用下载源
                    {
                        'url': 'https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-darwin-arm64-2023.08.17.gz',
                        'source': 'FastGit镜像站'
                    }
                ]
            else:
                urls = [
                    # 使用GitHub镜像站
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz',
                        'source': 'GitHub镜像站 (Premium 2023.08.17)'
                    },
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz',
                        'source': 'GitHub镜像站 (Latest)'
                    },
                    # 原始GitHub链接
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz',
                        'source': 'GitHub Premium (2023.08.17)'
                    },
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz',
                        'source': 'GitHub Latest'
                    },
                    # 备用下载源
                    {
                        'url': 'https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-darwin-amd64-2023.08.17.gz',
                        'source': 'FastGit镜像站'
                    }
                ]
        elif system == 'linux':
            if arch in ['arm64', 'aarch64']:
                urls = [
                    # 使用GitHub镜像站
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz',
                        'source': 'GitHub镜像站 (Premium 2023.08.17)'
                    },
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz',
                        'source': 'GitHub镜像站 (Latest)'
                    },
                    # 原始GitHub链接
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz',
                        'source': 'GitHub Premium (2023.08.17)'
                    },
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-arm64.gz',
                        'source': 'GitHub Latest'
                    },
                    # 备用下载源
                    {
                        'url': 'https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-linux-arm64-2023.08.17.gz',
                        'source': 'FastGit镜像站'
                    }
                ]
            else:
                urls = [
                    # 使用GitHub镜像站
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz',
                        'source': 'GitHub镜像站 (Premium 2023.08.17)'
                    },
                    {
                        'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz',
                        'source': 'GitHub镜像站 (Latest)'
                    },
                    # 原始GitHub链接
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz',
                        'source': 'GitHub Premium (2023.08.17)'
                    },
                    {
                        'url': 'https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz',
                        'source': 'GitHub Latest'
                    },
                    # 备用下载源
                    {
                        'url': 'https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-linux-amd64-2023.08.17.gz',
                        'source': 'FastGit镜像站'
                    }
                ]
        elif system == 'windows':
            urls = [
                # 使用GitHub镜像站
                {
                    'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz',
                    'source': 'GitHub镜像站 (Premium 2023.08.17)'
                },
                {
                    'url': 'https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz',
                    'source': 'GitHub镜像站 (Latest)'
                },
                # 原始GitHub链接
                {
                    'url': 'https://github.com/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz',
                    'source': 'GitHub Premium (2023.08.17)'
                },
                {
                    'url': 'https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz',
                    'source': 'GitHub Latest'
                },
                # 备用下载源
                {
                    'url': 'https://download.fastgit.org/Dreamacro/clash/releases/download/premium/clash-windows-amd64-2023.08.17.gz',
                    'source': 'FastGit镜像站'
                }
            ]
        
        return urls
    
    def install_clash(self) -> Tuple[bool, str]:
        """安装Clash（通过包管理器或下载二进制文件）"""
        # 首先尝试通过包管理器安装
        if self._try_package_manager_install():
            return True, "通过包管理器安装Clash成功"
        
        # 如果包管理器安装失败，尝试下载二进制文件
        success, message = self.download_clash_binary()
        
        if not success:
            # 提供手动安装建议
            manual_install_guide = self._get_manual_install_guide()
            return False, f"{message}\n\n手动安装建议:\n{manual_install_guide}"
        
        return success, message
    
    def _get_manual_install_guide(self) -> str:
        """获取手动安装指南"""
        import platform
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            return """
macOS安装方法:

方法1 - 使用Homebrew (推荐):
  brew install clash

方法2 - 下载ClashX (图形界面):
  访问: https://github.com/yichengchen/clashX/releases
  下载最新版本的ClashX.dmg并安装

方法3 - 手动下载Clash二进制文件:
  访问: https://github.com/Dreamacro/clash/releases/latest
  下载适合macOS的版本，解压后放到 /usr/local/bin/

方法4 - 使用镜像站下载:
  wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-darwin-amd64.gz
  gunzip clash-darwin-amd64.gz
  chmod +x clash-darwin-amd64
  sudo mv clash-darwin-amd64 /usr/local/bin/clash
"""
        elif system == 'linux':
            return """
Linux安装方法:

方法1 - 使用包管理器:
  Ubuntu/Debian: sudo apt update && sudo apt install clash
  CentOS/RHEL: sudo yum install clash
  Arch Linux: sudo pacman -S clash

方法2 - 手动下载:
  wget https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz
  gunzip clash-linux-amd64.gz
  chmod +x clash-linux-amd64
  sudo mv clash-linux-amd64 /usr/local/bin/clash

方法3 - 使用镜像站:
  curl -L https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-linux-amd64.gz | gunzip > clash
  chmod +x clash
  sudo mv clash /usr/local/bin/
"""
        elif system == 'windows':
            return """
Windows安装方法:

方法1 - 下载Clash for Windows (推荐):
  访问: https://github.com/Fndroid/clash_for_windows_pkg/releases
  下载最新版本的Clash.for.Windows.Setup.exe并安装

方法2 - 手动下载Clash二进制文件:
  访问: https://github.com/Dreamacro/clash/releases/latest
  下载clash-windows-amd64.gz，解压后重命名为clash.exe
  放到系统PATH目录中

方法3 - 使用PowerShell下载:
  Invoke-WebRequest -Uri "https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest/download/clash-windows-amd64.gz" -OutFile "clash.gz"
  # 使用7-Zip或其他工具解压gz文件
"""
        else:
            return """
通用安装方法:

1. 访问GitHub发布页面:
   https://github.com/Dreamacro/clash/releases/latest

2. 下载适合您系统的版本:
   - macOS: clash-darwin-amd64.gz 或 clash-darwin-arm64.gz
   - Linux: clash-linux-amd64.gz 或 clash-linux-arm64.gz  
   - Windows: clash-windows-amd64.gz

3. 解压文件并设置执行权限

4. 将可执行文件放到系统PATH目录中

如果网络访问GitHub困难，可以尝试镜像站:
- https://ghproxy.com/https://github.com/Dreamacro/clash/releases/latest
- https://download.fastgit.org/Dreamacro/clash/releases/latest
"""
    
    def _try_package_manager_install(self) -> bool:
        """尝试通过包管理器安装Clash"""
        try:
            import platform
            system = platform.system().lower()
            
            if system == 'darwin':  # macOS
                # 尝试通过Homebrew安装
                result = subprocess.run(['brew', 'install', 'clash'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.clash_binary_path = '/opt/homebrew/bin/clash'
                    return True
            elif system == 'linux':
                # 尝试通过apt安装
                result = subprocess.run(['sudo', 'apt', 'update'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    result = subprocess.run(['sudo', 'apt', 'install', '-y', 'clash'], 
                                          capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        self.clash_binary_path = '/usr/bin/clash'
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"包管理器安装失败: {e}")
            return False


# 全局Clash服务实例
clash_service = ClashEmbeddedService()
