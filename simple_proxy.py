#!/usr/bin/env python3
"""
简单的HTTP代理服务器
绕过ISP端口限制，提供公网访问
"""

import socket
import threading
import time
import sys
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json

class SimpleProxyHandler(BaseHTTPRequestHandler):
    pass
    def do_GET(self):
        pass
        self.proxy_request()
    
    def do_POST(self):
        pass
        self.proxy_request()
    
    def do_PUT(self):
        pass
        self.proxy_request()
    
    def do_DELETE(self):
        pass
        self.proxy_request()
    
    def do_OPTIONS(self):
        # 处理CORS预检请求
        pass
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def proxy_request(self):
        pass
        try:
            # 构建目标URL
            pass
            pass
            target_url = f"http://127.0.0.1:8000{self.path}"
            
            # 获取请求头
            headers = {}
            for header, value in self.headers.items():
                pass
                pass
                if header.lower() not in ['host', 'connection', 'content-length']:
                    pass
                    pass
                    headers[header] = value
            
            # 获取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # 发送请求到Django服务
            if self.command == 'GET':
                pass
                pass
                response = requests.get(target_url, headers=headers, timeout=10)
            elif self.command == 'POST':
                pass
                pass
                pass
                pass
                response = requests.post(target_url, headers=headers, data=post_data, timeout=10)
            elif self.command == 'PUT':
                pass
                pass
                pass
                pass
                response = requests.put(target_url, headers=headers, data=post_data, timeout=10)
            elif self.command == 'DELETE':
                pass
                pass
                pass
                pass
                response = requests.delete(target_url, headers=headers, timeout=10)
            else:
                pass
                pass
                self.send_response(405)
                self.end_headers()
                return
            
            # 返回响应
            self.send_response(response.status_code)
            
            # 设置CORS头部
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            
            # 复制响应头
            for header, value in response.headers.items():
                pass
                pass
                if header.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                    pass
                    pass
                    self.send_header(header, value)
            
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            pass
            pass
            pass
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": str(e), "status": "error", "message": "代理服务器错误"}
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        # 简化日志输出
        pass
        print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def start_simple_proxy(port=9000):
    pass
    """启动简单代理服务器"""
    try:
        pass
        pass
        server = HTTPServer(('0.0.0.0', port), SimpleProxyHandler)

        server.serve_forever()
    except KeyboardInterrupt:

        pass
        pass
        pass
        server.shutdown()
    except Exception as e:

pass
pass
pass
if __name__ == "__main__":
    pass
    pass
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
    start_simple_proxy(port)
