#!/usr/bin/env python3
"""
测试Clash代理连接 - 验证翻墙功能
"""

import requests
import time
import json

def test_clash_proxies():
    """测试Clash代理"""
    print("🧪 测试Clash代理连接...")
    print("=" * 50)
    
    # Clash代理配置
    clash_proxies = [
        {
            'name': 'Clash-HTTP',
            'type': 'http',
            'server': '127.0.0.1',
            'port': 7890
        },
        {
            'name': 'Clash-SOCKS5',
            'type': 'socks5',
            'server': '127.0.0.1',
            'port': 7891
        }
    ]
    
    # 测试网站
    test_sites = [
        'https://google.com',
        'https://youtube.com',
        'https://github.com',
        'https://httpbin.org/ip'
    ]
    
    results = {}
    
    for proxy in clash_proxies:
        print(f"\n🔧 测试代理: {proxy['name']} ({proxy['server']}:{proxy['port']})")
        
        # 构建代理配置
        if proxy['type'] == 'http':
            proxy_url = f"http://{proxy['server']}:{proxy['port']}"
            proxies = {'http': proxy_url, 'https': proxy_url}
        elif proxy['type'] == 'socks5':
            proxy_url = f"socks5://{proxy['server']}:{proxy['port']}"
            proxies = {'http': proxy_url, 'https': proxy_url}
        
        # 测试代理连接
        try:
            print("   📡 测试代理连接...")
            test_response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                timeout=10,
                verify=False
            )
            
            if test_response.status_code == 200:
                try:
                    ip_data = test_response.json()
                    print(f"   ✅ 代理连接成功! IP: {ip_data.get('origin', 'N/A')}")
                    
                    # 测试外网访问
                    for site in test_sites:
                        try:
                            print(f"   🌐 测试访问: {site}")
                            response = requests.get(
                                site,
                                proxies=proxies,
                                timeout=15,
                                verify=False
                            )
                            
                            if response.status_code == 200:
                                content_length = len(response.text)
                                print(f"   ✅ 访问成功: {response.status_code} (内容: {content_length} 字符)")
                                
                                if content_length > 1000:
                                    print("   🎉 翻墙成功！获取到完整内容")
                                else:
                                    print("   ⚠️  内容较少，可能翻墙不完整")
                                    
                                results[f"{proxy['name']}_{site}"] = {
                                    'success': True,
                                    'status': response.status_code,
                                    'content_length': content_length
                                }
                            else:
                                print(f"   ❌ 访问失败: {response.status_code}")
                                results[f"{proxy['name']}_{site}"] = {
                                    'success': False,
                                    'status': response.status_code
                                }
                                
                        except Exception as e:
                            print(f"   ❌ 访问异常: {e}")
                            results[f"{proxy['name']}_{site}"] = {
                                'success': False,
                                'error': str(e)
                            }
                            
                except Exception as e:
                    print(f"   ❌ IP解析失败: {e}")
                    
            else:
                print(f"   ❌ 代理连接失败: {test_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 代理测试失败: {e}")
    
    return results

def test_direct_access():
    """测试直接访问"""
    print("\n🌐 测试直接访问外网...")
    print("=" * 50)
    
    test_sites = [
        'https://google.com',
        'https://youtube.com',
        'https://github.com'
    ]
    
    results = {}
    
    for site in test_sites:
        try:
            print(f"\n📡 直接访问: {site}")
            response = requests.get(site, timeout=10, verify=False)
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📄 内容长度: {len(response.text)} 字符")
            results[site] = {'success': True, 'status': response.status_code, 'length': len(response.text)}
        except Exception as e:
            print(f"   ❌ 访问失败: {e}")
            results[site] = {'success': False, 'error': str(e)}
    
    return results

def analyze_results(direct_results, proxy_results):
    """分析测试结果"""
    print("\n" + "=" * 50)
    print("📊 翻墙效果分析")
    print("=" * 50)
    
    # 统计成功率
    direct_success = sum(1 for r in direct_results.values() if r.get('success'))
    proxy_success = sum(1 for r in proxy_results.values() if r.get('success'))
    
    print(f"直接访问成功率: {direct_success}/{len(direct_results)} ({direct_success/len(direct_results)*100:.1f}%)")
    
    if len(proxy_results) > 0:
        print(f"代理访问成功率: {proxy_success}/{len(proxy_results)} ({proxy_success/len(proxy_results)*100:.1f}%)")
    else:
        print("代理访问成功率: 0/0 (0.0%)")
    
    if proxy_success > direct_success:
        print("🎉 翻墙系统工作正常！")
        print("💡 建议: 现在可以在Web界面中使用翻墙功能")
        
        # 显示成功的代理
        successful_proxies = set()
        for key, result in proxy_results.items():
            if result.get('success'):
                proxy_name = key.split('_')[0]
                successful_proxies.add(proxy_name)
        
        print(f"✅ 可用的代理: {', '.join(successful_proxies)}")
        
    elif proxy_success == direct_success:
        print("⚠️  翻墙效果不明显")
        print("💡 建议: 检查Clash是否正在运行")
    else:
        print("❌ 翻墙系统存在问题")
        print("💡 建议: 启动Clash客户端")

def main():
    """主函数"""
    print("🚀 Clash代理翻墙测试")
    print("=" * 50)
    print("💡 请确保Clash客户端正在运行")
    print("🔧 默认端口: HTTP 7890, SOCKS5 7891")
    print("=" * 50)
    
    # 测试直接访问
    direct_results = test_direct_access()
    
    # 测试Clash代理
    proxy_results = test_clash_proxies()
    
    # 分析结果
    analyze_results(direct_results, proxy_results)
    
    print("\n" + "=" * 50)
    print("💡 使用说明:")
    print("1. 启动Clash客户端")
    print("2. 确保代理端口7890和7891可用")
    print("3. 访问: http://localhost:8001/tools/proxy-dashboard/")
    print("4. 使用Web翻墙浏览器访问外网")

if __name__ == "__main__":
    main()
