#!/usr/bin/env python3
"""
测试增强版翻墙代理服务器
"""

import requests
import time

def test_enhanced_proxy():
    """测试增强版代理服务器"""
    print("🧪 测试增强版翻墙代理服务器...")
    print("=" * 50)
    
    proxy_config = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080'
    }
    
    # 测试网站列表
    test_sites = [
        {
            'url': 'http://httpbin.org/ip',
            'name': 'HTTP测试',
            'need_proxy': False
        },
        {
            'url': 'https://httpbin.org/ip', 
            'name': 'HTTPS测试',
            'need_proxy': False
        },
        {
            'url': 'https://google.com',
            'name': 'Google',
            'need_proxy': True
        },
        {
            'url': 'https://youtube.com',
            'name': 'YouTube',
            'need_proxy': True
        },
        {
            'url': 'https://github.com',
            'name': 'GitHub',
            'need_proxy': True
        }
    ]
    
    for site in test_sites:
        try:
            print(f"\n📡 测试: {site['name']} ({site['url']})")
            
            # 直接访问测试
            try:
                print("   🌍 直接访问...")
                direct_response = requests.get(
                    site['url'],
                    timeout=10,
                    verify=False
                )
                print(f"   ✅ 直接访问成功: {direct_response.status_code}")
                if 'httpbin.org' in site['url']:
                    try:
                        data = direct_response.json()
                        print(f"   🌍 IP地址: {data.get('origin', 'N/A')}")
                    except:
                        pass
            except Exception as e:
                print(f"   ❌ 直接访问失败: {e}")
            
            # 代理访问测试
            try:
                print("   🔧 代理访问...")
                proxy_response = requests.get(
                    site['url'],
                    proxies=proxy_config,
                    timeout=20,
                    verify=False
                )
                print(f"   ✅ 代理访问成功: {proxy_response.status_code}")
                print(f"   📄 内容长度: {len(proxy_response.text)} 字符")
                
                if 'httpbin.org' in site['url']:
                    try:
                        data = proxy_response.json()
                        print(f"   🌍 IP地址: {data.get('origin', 'N/A')}")
                    except:
                        pass
                        
                # 检查是否真的翻墙成功
                if site['need_proxy'] and len(proxy_response.text) > 1000:
                    print("   🎉 翻墙成功！获取到完整网页内容")
                elif site['need_proxy']:
                    print("   ⚠️  翻墙可能不完整，内容较少")
                    
            except Exception as e:
                print(f"   ❌ 代理访问失败: {e}")
                
        except Exception as e:
            print(f"   ❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    print("\n💡 结果分析:")
    print("1. 如果直接访问失败但代理访问成功，说明翻墙有效")
    print("2. 如果代理访问也失败，可能是代理节点不可用")
    print("3. 如果内容长度很少，可能是翻墙不完整")

if __name__ == "__main__":
    test_enhanced_proxy()
