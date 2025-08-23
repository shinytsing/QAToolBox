#!/usr/bin/env python3
"""
测试代理连接功能
"""

import requests
import time

def test_local_proxy():
    """测试本地代理服务器"""
    print("🧪 测试本地代理服务器...")
    
    # 测试本地代理是否运行
    try:
        response = requests.get('http://127.0.0.1:8080', timeout=5)
        print(f"✅ 本地代理服务器运行正常 (端口8080)")
        return True
    except:
        print("❌ 本地代理服务器未运行")
        return False

def test_web_access():
    """测试Web访问功能"""
    print("\n🌐 测试Web访问功能...")
    
    test_urls = [
        'http://httpbin.org/ip',  # 测试IP获取
        'http://httpbin.org/user-agent',  # 测试User-Agent
        'http://httpbin.org/headers'  # 测试请求头
    ]
    
    for url in test_urls:
        try:
            print(f"\n📡 测试访问: {url}")
            
            # 直接访问
            direct_response = requests.get(url, timeout=10)
            print(f"   ✅ 直接访问成功: {direct_response.status_code}")
            
            # 通过本地代理访问
            try:
                proxy_response = requests.get(
                    url, 
                    proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'},
                    timeout=10
                )
                print(f"   ✅ 代理访问成功: {proxy_response.status_code}")
                
                # 比较内容
                if direct_response.text == proxy_response.text:
                    print("   ✅ 内容一致")
                else:
                    print("   ⚠️  内容不一致")
                    
            except Exception as e:
                print(f"   ❌ 代理访问失败: {e}")
                
        except Exception as e:
            print(f"   ❌ 访问失败: {e}")

def test_foreign_sites():
    """测试外网站点访问"""
    print("\n🌍 测试外网站点访问...")
    
    # 这些网站可能需要代理才能访问
    foreign_sites = [
        'https://google.com',
        'https://youtube.com',
        'https://github.com'
    ]
    
    for site in foreign_sites:
        try:
            print(f"\n📡 测试访问: {site}")
            
            # 尝试直接访问
            try:
                response = requests.get(site, timeout=15, verify=False)
                print(f"   ✅ 直接访问成功: {response.status_code}")
                print(f"   📄 内容长度: {len(response.text)} 字符")
            except Exception as e:
                print(f"   ❌ 直接访问失败: {e}")
                
                # 尝试通过代理访问
                try:
                    proxy_response = requests.get(
                        site,
                        proxies={'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'},
                        timeout=15,
                        verify=False
                    )
                    print(f"   ✅ 代理访问成功: {proxy_response.status_code}")
                    print(f"   📄 内容长度: {len(proxy_response.text)} 字符")
                except Exception as proxy_e:
                    print(f"   ❌ 代理访问也失败: {proxy_e}")
                    
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")

def main():
    """主函数"""
    print("🚀 代理连接测试工具")
    print("=" * 50)
    
    # 测试本地代理
    if not test_local_proxy():
        print("\n💡 建议:")
        print("1. 运行: python local_proxy_server.py")
        print("2. 或者运行: ./start_proxy_service.sh")
        return
    
    # 测试Web访问
    test_web_access()
    
    # 测试外网站点
    test_foreign_sites()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    print("💡 如果代理工作正常，现在可以:")
    print("1. 访问: http://localhost:8001/tools/proxy-dashboard/")
    print("2. 使用Web翻墙浏览器访问外网")
    print("3. 享受无障碍的全球网络访问!")

if __name__ == "__main__":
    main()
