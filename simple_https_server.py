#!/usr/bin/env python3
"""
简单的HTTPS反向代理服务器
将HTTPS请求转发到Django HTTP服务器
"""

import ssl
import socket
import threading
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HTTPSProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def do_HEAD(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # 构建目标URL
            target_url = f"http://127.0.0.1:8000{self.path}"
            
            # 准备请求数据
            content_length = self.headers.get('Content-Length')
            post_data = None
            if content_length:
                post_data = self.rfile.read(int(content_length))
            
            # 创建请求
            req = urllib.request.Request(target_url, data=post_data, method=self.command)
            
            # 复制头部（除了Host）
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'content-length']:
                    req.add_header(header, value)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                # 发送响应状态
                self.send_response(response.getcode())
                
                # 发送响应头
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                
                # 发送响应体
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"HTTP Error: {e.code} {e.reason}".encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Proxy Error: {str(e)}".encode())

def start_https_proxy():
    """启动HTTPS代理服务器"""
    
    # 检查HTTP服务器是否运行
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=5) as response:
            if response.getcode() != 200:
                print("❌ Django HTTP服务器未正常响应")
                return False
    except Exception as e:
        print(f"❌ 无法连接到Django HTTP服务器: {e}")
        print("请先启动HTTP服务器: python3 manage.py runserver 0.0.0.0:8000")
        return False
    
    print("🔐 启动HTTPS代理服务器...")
    print("📍 HTTPS地址: https://192.168.0.118:8443")
    print("📍 本地访问: https://localhost:8443")
    print("⚠️  浏览器会提示证书不安全，请点击'继续访问'")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        # 创建HTTP服务器
        server = HTTPServer(('0.0.0.0', 8443), HTTPSProxyHandler)
        
        # 配置SSL
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain('ssl/cert.pem', 'ssl/key.pem')
        server.socket = context.wrap_socket(server.socket, server_side=True)
        
        print("✅ HTTPS代理服务器启动成功!")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 HTTPS代理服务器已停止")
        server.shutdown()
    except Exception as e:
        print(f"❌ 启动HTTPS代理服务器失败: {e}")
        return False
    
    return True

if __name__ == '__main__':
    start_https_proxy()
