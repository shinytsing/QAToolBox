#!/usr/bin/env python3
"""
测试外网访问功能 - 验证翻墙服务
"""

import requests
import time
import json

def test_direct_access():
    """测试直接访问"""
    print("🌐 测试直接访问外网...")
    
    test_sites = [
        'https://google.com',
        'https://youtube.com', 
        'https://github.com',
        'https://httpbin.org/ip'
    ]
    
    for site in test_sites:
        try:
            print(f"\n📡 直接访问: {site}")
            response = requests.get(site, timeout=10, verify=False)
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📄 内容长度: {len(response.text)} 字符")
            
            if 'httpbin.org' in site:
                try:
                    data = response.json()
                    print(f"   🌍 IP地址: {data.get('origin', 'N/A')}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ 访问失败: {e}")

def test_proxy_access():
    """测试代理访问"""
    print("\n🔧 测试代理访问外网...")
    
    proxy_config = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    
    test_sites = [
        'https://google.com',
        'https://youtube.com',
        'https://github.com',
        'https://httpbin.org/ip'
    ]
    
    for site in test_sites:
        try:
            print(f"\n📡 代理访问: {site}")
            response = requests.get(
                site, 
                proxies=proxy_config,
                timeout=15, 
                verify=False
            )
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📄 内容长度: {len(response.text)} 字符")
            
            if 'httpbin.org' in site:
                try:
                    data = response.json()
                    print(f"   🌍 IP地址: {data.get('origin', 'N/A')}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ 代理访问失败: {e}")

def test_web_proxy_api():
    """测试Web代理API"""
    print("\n🌍 测试Web代理API...")
    
    base_url = "http://localhost:8001"
    test_urls = [
        'google.com',
        'youtube.com',
        'github.com',
        'httpbin.org/ip'
    ]
    
    for url in test_urls:
        try:
            print(f"\n📡 API测试: {url}")
            
            # 模拟POST请求到Web代理API
            api_url = f"{base_url}/tools/api/proxy/web-browse/"
            data = {'url': url}
            
            response = requests.post(
                api_url,
                json=data,
                timeout=20,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ 访问成功")
                        print(f"   📡 使用代理: {result['data'].get('proxy_used', 'N/A')}")
                        print(f"   📄 内容长度: {len(result['data'].get('content', ''))} 字符")
                    else:
                        print(f"   ❌ 访问失败: {result.get('error', '未知错误')}")
                except:
                    print(f"   ⚠️  JSON解析失败")
            elif response.status_code == 302:
                print(f"   🔐 需要登录认证")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ API测试异常: {e}")

def main():
    """主函数"""
    print("🚀 外网访问测试工具")
    print("=" * 50)
    
    # 测试直接访问
    test_direct_access()
    
    # 测试代理访问
    test_proxy_access()
    
    # 测试Web代理API
    test_web_proxy_api()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    print("\n💡 结果分析:")
    print("1. 如果直接访问失败但代理访问成功，说明翻墙有效")
    print("2. 如果Web代理API返回302，需要先登录系统")
    print("3. 如果所有测试都失败，检查网络和代理配置")

if __name__ == "__main__":
    main()
