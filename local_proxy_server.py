#!/usr/bin/env python3
"""
本地HTTP代理服务器 - 用于测试Web翻墙功能
"""

import socket
import threading
import time
from urllib.parse import urlparse

import requests


class LocalProxyServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None

    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"🚀 本地代理服务器已启动: http://{self.host}:{self.port}")
            print("💡 现在可以在Web翻墙浏览器中使用此代理")
            print("🔧 代理地址: 127.0.0.1:8080")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    if self.running:
                        print(f"❌ 客户端连接错误: {e}")

        except Exception as e:
            print(f"❌ 代理服务器启动失败: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket, address):
        """处理客户端请求"""
        try:
            # 接收HTTP请求
            request = client_socket.recv(4096).decode("utf-8")
            if not request:
                return

            # 解析请求行
            lines = request.split("\n")
            if not lines:
                return

            request_line = lines[0].strip()
            method, url, version = request_line.split(" ")

            # 解析URL和协议
            protocol = "http"
            if url.startswith("http://"):
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                path = parsed_url.path
                protocol = "http"
            elif url.startswith("https://"):
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                path = parsed_url.path
                protocol = "https"
            else:
                # 相对URL，从Host头获取主机
                host = None
                for line in lines:
                    if line.startswith("Host:"):
                        host = line.split(":")[1].strip()
                        break
                path = url

            if not host:
                client_socket.close()
                return

            # 构建目标URL
            target_url = f"{protocol}://{host}{path}"

            print(f"🌐 代理请求: {method} {target_url}")

            # 转发请求到目标服务器
            try:
                # 构建请求头
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }

                # 发送请求
                if method.upper() == "GET":
                    response = requests.get(target_url, headers=headers, timeout=15, verify=False, allow_redirects=True)
                else:
                    response = requests.get(target_url, headers=headers, timeout=15, verify=False, allow_redirects=True)

                print(f"✅ 代理成功: {response.status_code} - {target_url}")

                # 返回响应给客户端
                status_line = f"HTTP/1.1 {response.status_code} OK\r\n"

                # 构建响应头
                response_headers = []
                for key, value in response.headers.items():
                    if key.lower() not in ["transfer-encoding", "connection"]:
                        response_headers.append(f"{key}: {value}")

                response_headers.append("Via: LocalProxy/1.0")
                response_headers.append("Connection: close")

                full_response = status_line + "\r\n".join(response_headers) + "\r\n\r\n"
                client_socket.send(full_response.encode())
                client_socket.send(response.content)

            except Exception as e:
                print(f"❌ 代理失败: {target_url} - {e}")
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
        print("🛑 本地代理服务器已停止")


def main():
    """主函数"""
    print("🌐 本地HTTP代理服务器")
    print("=" * 40)

    proxy = LocalProxyServer(port=8080)

    try:
        proxy.start()
    except KeyboardInterrupt:
        print("\n👋 收到停止信号，正在关闭服务器...")
        proxy.stop()


if __name__ == "__main__":
    main()
