#!/usr/bin/env python3
"""
最终翻墙系统测试 - 验证完整功能
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

def test_web_proxy_api():
    """测试Web代理API"""
    print("\n🌍 测试Web代理API...")
    
    base_url = "http://localhost:8001"
    test_urls = [
        'google.com',
        'youtube.com',
        'github.com'
    ]
    
    results = {}
    for url in test_urls:
        try:
            print(f"\n📡 API测试: {url}")
            
            api_url = f"{base_url}/tools/api/proxy/web-browse/"
            data = {'url': url}
            
            response = requests.post(
                api_url,
                json=data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📊 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success'):
                        print(f"   ✅ 访问成功")
                        print(f"   📡 使用代理: {result['data'].get('proxy_used', 'N/A')}")
                        content_length = len(result['data'].get('content', ''))
                        print(f"   📄 内容长度: {content_length} 字符")
                        
                        if content_length > 1000:
                            print("   🎉 翻墙成功！获取到完整网页内容")
                        else:
                            print("   ⚠️  内容较少，翻墙可能不完整")
                            
                        results[url] = {
                            'success': True,
                            'proxy_used': result['data'].get('proxy_used', 'N/A'),
                            'content_length': content_length
                        }
                    else:
                        error_msg = result.get('error', '未知错误')
                        print(f"   ❌ 访问失败: {error_msg}")
                        results[url] = {'success': False, 'error': error_msg}
                except Exception as e:
                    print(f"   ⚠️  JSON解析失败: {e}")
                    results[url] = {'success': False, 'error': f'JSON解析失败: {e}'}
            elif response.status_code == 302:
                print(f"   🔐 需要登录认证")
                results[url] = {'success': False, 'error': '需要登录认证'}
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                results[url] = {'success': False, 'error': f'HTTP错误: {response.status_code}'}
                
        except Exception as e:
            print(f"   ❌ API测试异常: {e}")
            results[url] = {'success': False, 'error': f'API异常: {e}'}
    
    return results

def analyze_results(direct_results, proxy_results):
    """分析测试结果"""
    print("\n" + "=" * 50)
    print("📊 测试结果分析")
    print("=" * 50)
    
    for site in ['google.com', 'youtube.com', 'github.com']:
        print(f"\n🌐 {site}:")
        
        direct = direct_results.get(f'https://{site}', {})
        proxy = proxy_results.get(site, {})
        
        if direct.get('success'):
            print(f"   🌍 直接访问: ✅ 成功 (状态码: {direct.get('status')})")
        else:
            print(f"   🌍 直接访问: ❌ 失败 ({direct.get('error', '未知错误')})")
            
        if proxy.get('success'):
            print(f"   🔧 代理访问: ✅ 成功 (代理: {proxy.get('proxy_used')}, 内容: {proxy.get('content_length')} 字符)")
            
            if proxy.get('content_length', 0) > 1000:
                print("   🎉 翻墙效果: 优秀 - 获取到完整内容")
            elif proxy.get('content_length', 0) > 100:
                print("   ⚠️  翻墙效果: 一般 - 内容不完整")
            else:
                print("   ❌ 翻墙效果: 较差 - 内容很少")
        else:
            print(f"   🔧 代理访问: ❌ 失败 ({proxy.get('error', '未知错误')})")
    
    # 总体评估
    print("\n" + "=" * 50)
    print("🎯 总体评估")
    print("=" * 50)
    
    direct_success = sum(1 for r in direct_results.values() if r.get('success'))
    proxy_success = sum(1 for r in proxy_results.values() if r.get('success'))
    
    print(f"直接访问成功率: {direct_success}/{len(direct_results)} ({direct_success/len(direct_results)*100:.1f}%)")
    print(f"代理访问成功率: {proxy_success}/{len(proxy_results)} ({proxy_success/len(proxy_results)*100:.1f}%)")
    
    if proxy_success > direct_success:
        print("🎉 翻墙系统工作正常！")
        print("💡 建议: 现在可以在Web界面中使用翻墙功能")
    elif proxy_success == direct_success:
        print("⚠️  翻墙效果不明显")
        print("💡 建议: 检查代理配置或网络环境")
    else:
        print("❌ 翻墙系统存在问题")
        print("💡 建议: 检查代理服务器和网络配置")

def main():
    """主函数"""
    print("🚀 最终翻墙系统测试")
    print("=" * 50)
    
    # 测试直接访问
    direct_results = test_direct_access()
    
    # 测试Web代理API
    proxy_results = test_web_proxy_api()
    
    # 分析结果
    analyze_results(direct_results, proxy_results)
    
    print("\n" + "=" * 50)
    print("💡 使用说明:")
    print("1. 访问: http://localhost:8001/tools/proxy-dashboard/")
    print("2. 登录系统")
    print("3. 使用Web翻墙浏览器访问外网")
    print("4. 享受无障碍的全球网络访问!")

if __name__ == "__main__":
    main()
