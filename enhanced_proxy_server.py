#!/usr/bin/env python3
"""
增强版HTTP代理服务器 - 直接支持翻墙功能
"""

import socket
import threading
import time
import requests
from urllib.parse import urlparse
import json

class EnhancedProxyServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        
        # 翻墙代理配置
        self.proxy_pools = [
            # 公共代理池
            {
                'name': 'Public-Proxy-1',
                'server': '51.79.50.46',
                'port': 9302
            },
            {
                'name': 'Public-Proxy-2',
                'server': '51.79.50.31', 
                'port': 9302
            },
            {
                'name': 'Public-Proxy-3',
                'server': '51.79.50.22',
                'port': 9302
            }
        ]
        
        # 当前使用的代理
        self.current_proxy = None
        self.proxy_failures = {}
        
    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 增强版翻墙代理服务器已启动: http://{self.host}:{self.port}")
            print("💡 支持自动翻墙访问外网")
            print("🔧 代理地址: 127.0.0.1:8080")
            print("🌐 测试命令: curl -x http://127.0.0.1:8080 https://google.com")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"❌ 客户端连接错误: {e}")
                        
        except Exception as e:
            print(f"❌ 代理服务器启动失败: {e}")
        finally:
            self.stop()
    
    def get_working_proxy(self):
        """获取可用的代理"""
        if self.current_proxy and self.proxy_failures.get(self.current_proxy['name'], 0) < 3:
            return self.current_proxy
            
        # 测试所有代理
        for proxy in self.proxy_pools:
            proxy_name = proxy['name']
            if self.proxy_failures.get(proxy_name, 0) >= 3:
                continue
                
            try:
                test_url = 'http://httpbin.org/ip'
                proxy_url = f"http://{proxy['server']}:{proxy['port']}"
                
                response = requests.get(
                    test_url,
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=5,
                    verify=False
                )
                
                if response.status_code == 200:
                    self.current_proxy = proxy
                    print(f"✅ 切换到代理: {proxy_name}")
                    return proxy
                    
            except Exception as e:
                print(f"❌ 代理 {proxy_name} 测试失败: {e}")
                self.proxy_failures[proxy_name] = self.proxy_failures.get(proxy_name, 0) + 1
        
        print("⚠️  所有代理都不可用，使用直接连接")
        return None
    
    def handle_client(self, client_socket, address):
        """处理客户端请求"""
        try:
            # 接收HTTP请求
            request = client_socket.recv(4096).decode('utf-8')
            if not request:
                return
                
            # 解析请求行
            lines = request.split('\n')
            if not lines:
                return
                
            request_line = lines[0].strip()
            method, url, version = request_line.split(' ')
            
            # 解析URL和协议
            protocol = 'http'
            if url.startswith('http://'):
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                path = parsed_url.path
                protocol = 'http'
            elif url.startswith('https://'):
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                path = parsed_url.path
                protocol = 'https'
            else:
                # 相对URL，从Host头获取主机
                host = None
                for line in lines:
                    if line.startswith('Host:'):
                        host = line.split(':')[1].strip()
                        break
                path = url
                
            if not host:
                client_socket.close()
                return
                
            # 构建目标URL
            target_url = f"{protocol}://{host}{path}"
            
            print(f"🌐 代理请求: {method} {target_url}")
            
            # 判断是否需要翻墙
            need_proxy = any(domain in host.lower() for domain in [
                'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
                'instagram.com', 'github.com', 'netflix.com', 'amazon.com'
            ])
            
            # 获取代理配置
            proxy_config = None
            if need_proxy:
                proxy_config = self.get_working_proxy()
            
            # 转发请求到目标服务器
            try:
                # 构建请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                # 发送请求
                if proxy_config:
                    proxy_url = f"http://{proxy_config['server']}:{proxy_config['port']}"
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    print(f"🔧 使用翻墙代理: {proxy_config['name']}")
                    
                    response = requests.get(
                        target_url,
                        headers=headers,
                        proxies=proxies,
                        timeout=20,
                        verify=False,
                        allow_redirects=True
                    )
                else:
                    print(f"🌍 直接连接: {host}")
                    response = requests.get(
                        target_url,
                        headers=headers,
                        timeout=15,
                        verify=False,
                        allow_redirects=True
                    )
                
                print(f"✅ 请求成功: {response.status_code} - {target_url}")
                
                # 返回响应给客户端
                status_line = f"HTTP/1.1 {response.status_code} OK\r\n"
                
                # 构建响应头
                response_headers = []
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'connection']:
                        response_headers.append(f"{key}: {value}")
                
                response_headers.append("Via: EnhancedProxy/1.0")
                response_headers.append("Connection: close")
                
                full_response = status_line + "\r\n".join(response_headers) + "\r\n\r\n"
                client_socket.send(full_response.encode())
                client_socket.send(response.content)
                
            except Exception as e:
                print(f"❌ 请求失败: {target_url} - {e}")
                
                # 如果是代理失败，标记代理不可用
                if proxy_config:
                    proxy_name = proxy_config['name']
                    self.proxy_failures[proxy_name] = self.proxy_failures.get(proxy_name, 0) + 1
                    print(f"⚠️  代理 {proxy_name} 失败次数: {self.proxy_failures[proxy_name]}")
                
                # 返回错误响应
                error_response = f"""HTTP/1.1 502 Bad Gateway
Content-Type: text/html

<html><body><h1>502 Bad Gateway</h1><p>代理服务器无法连接到目标服务器: {e}</p></body></html>"""
                client_socket.send(error_response.encode())
                
        except Exception as e:
            print(f"❌ 处理客户端请求错误: {e}")
        finally:
            client_socket.close()
    
    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 增强版翻墙代理服务器已停止")

def main():
    """主函数"""
    print("🌐 增强版翻墙代理服务器")
    print("=" * 50)
    
    proxy = EnhancedProxyServer(port=8080)
    
    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n👋 收到停止信号，正在关闭服务器...")
        proxy.stop()

if __name__ == "__main__":
    main()
