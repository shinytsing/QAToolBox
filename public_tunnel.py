#!/usr/bin/env python3
"""
公共访问隧道服务器
使用Python实现简单的HTTP代理，绕过ISP端口限制
"""

import socket
import threading
import time
import sys
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

class PublicTunnelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.forward_request()
    
    def do_POST(self):
        self.forward_request()
    
    def do_PUT(self):
        self.forward_request()
    
    def do_DELETE(self):
        self.forward_request()
    
    def forward_request(self):
        try:
            # 构建目标URL
            target_url = f"http://localhost:8000{self.path}"
            
            # 获取请求头
            headers = dict(self.headers)
            # 移除可能导致问题的头部
            headers.pop('Host', None)
            headers.pop('Connection', None)
            
            # 获取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # 发送请求到本地Django服务
            if self.command == 'GET':
                response = requests.get(target_url, headers=headers, timeout=10)
            elif self.command == 'POST':
                response = requests.post(target_url, headers=headers, data=post_data, timeout=10)
            elif self.command == 'PUT':
                response = requests.put(target_url, headers=headers, data=post_data, timeout=10)
            elif self.command == 'DELETE':
                response = requests.delete(target_url, headers=headers, timeout=10)
            
            # 返回响应
            self.send_response(response.status_code)
            
            # 设置CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            
            # 复制响应头
            for header, value in response.headers.items():
                if header.lower() not in ['content-encoding', 'transfer-encoding']:
                    self.send_header(header, value)
            
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"请求转发失败: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": str(e), "status": "error"}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def log_message(self, format, *args):
        # 简化日志输出
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def start_public_tunnel(port=9000):
    """启动公共隧道服务器"""
    try:
        print(f"🚀 启动公网隧道服务器，端口: {port}")
        server = HTTPServer(('0.0.0.0', port), PublicTunnelHandler)
        print(f"✅ 隧道服务器启动成功！")
        print(f"📡 外网访问地址: http://您的公网IP:{port}")
        print(f"🔄 转发到本地: http://localhost:8000")
        print("按 Ctrl+C 停止服务")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 隧道服务器已停止")
        server.shutdown()
    except Exception as e:
        print(f"隧道服务器启动失败: {e}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    start_public_tunnel(port)