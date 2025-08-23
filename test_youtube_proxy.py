#!/usr/bin/env python3
"""
测试YouTube代理访问脚本
测试修改后的代理系统是否能正常访问YouTube
"""

import requests
import json
import time
from urllib.parse import urlparse

def test_youtube_proxy():
    """测试YouTube代理访问"""
    print("🔍 开始测试YouTube代理访问...")
    
    # 测试代理配置
    proxy_configs = [
        {
            'name': 'Local-Clash-HTTP',
            'type': 'http',
            'server': '127.0.0.1',
            'port': 7890
        },
        {
            'name': 'Local-Clash-SOCKS',
            'type': 'socks5', 
            'server': '127.0.0.1',
            'port': 7891
        }
    ]
    
    test_urls = [
        'https://www.youtube.com/favicon.ico',  # YouTube图标
        'https://www.youtube.com',             # YouTube主页
        'https://www.google.com'               # Google（作为对比）
    ]
    
    results = []
    
    for config in proxy_configs:
        print(f"\n📡 测试代理: {config['name']} ({config['server']}:{config['port']})")
        
        # 设置代理
        if config['type'] == 'http':
            proxy_url = f"http://{config['server']}:{config['port']}"
            proxies = {'http': proxy_url, 'https': proxy_url}
        elif config['type'] == 'socks5':
            proxy_url = f"socks5://{config['server']}:{config['port']}"
            proxies = {'http': proxy_url, 'https': proxy_url}
        
        for url in test_urls:
            try:
                print(f"  🔗 访问: {url}")
                start_time = time.time()
                
                response = requests.get(
                    url,
                    proxies=proxies,
                    timeout=10,
                    verify=False,
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    print(f"    ✅ 成功 - 状态码: {response.status_code}, 响应时间: {response_time:.2f}秒")
                    results.append({
                        'proxy': config['name'],
                        'url': url,
                        'status': 'success',
                        'status_code': response.status_code,
                        'response_time': response_time
                    })
                else:
                    print(f"    ⚠️  警告 - 状态码: {response.status_code}, 响应时间: {response_time:.2f}秒")
                    results.append({
                        'proxy': config['name'],
                        'url': url,
                        'status': 'warning',
                        'status_code': response.status_code,
                        'response_time': response_time
                    })
                
            except requests.exceptions.Timeout:
                print(f"    ❌ 超时 - 超过10秒无响应")
                results.append({
                    'proxy': config['name'],
                    'url': url,
                    'status': 'timeout',
                    'error': 'Timeout'
                })
            except requests.exceptions.ConnectionError as e:
                print(f"    ❌ 连接错误 - {str(e)}")
                results.append({
                    'proxy': config['name'],
                    'url': url,
                    'status': 'connection_error',
                    'error': str(e)
                })
            except Exception as e:
                print(f"    ❌ 未知错误 - {str(e)}")
                results.append({
                    'proxy': config['name'],
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
            
            time.sleep(1)  # 避免请求过于频繁
    
    # 测试直接访问（无代理）
    print(f"\n🔗 测试直接访问（无代理）:")
    for url in test_urls:
        try:
            print(f"  🔗 访问: {url}")
            start_time = time.time()
            
            response = requests.get(
                url,
                timeout=10,
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"    ✅ 成功 - 状态码: {response.status_code}, 响应时间: {response_time:.2f}秒")
                results.append({
                    'proxy': 'Direct',
                    'url': url,
                    'status': 'success',
                    'status_code': response.status_code,
                    'response_time': response_time
                })
            else:
                print(f"    ⚠️  警告 - 状态码: {response.status_code}, 响应时间: {response_time:.2f}秒")
                results.append({
                    'proxy': 'Direct',
                    'url': url,
                    'status': 'warning',
                    'status_code': response.status_code,
                    'response_time': response_time
                })
            
        except Exception as e:
            print(f"    ❌ 错误 - {str(e)}")
            results.append({
                'proxy': 'Direct',
                'url': url,
                'status': 'error',
                'error': str(e)
            })
        
        time.sleep(1)
    
    # 输出总结
    print(f"\n📊 测试总结:")
    success_count = len([r for r in results if r['status'] == 'success'])
    total_count = len(results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 按代理分组显示结果
    proxy_results = {}
    for result in results:
        proxy = result['proxy']
        if proxy not in proxy_results:
            proxy_results[proxy] = {'success': 0, 'total': 0}
        proxy_results[proxy]['total'] += 1
        if result['status'] == 'success':
            proxy_results[proxy]['success'] += 1
    
    print(f"\n📈 按代理统计:")
    for proxy, stats in proxy_results.items():
        success_rate = stats['success']/stats['total']*100
        print(f"  {proxy}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # YouTube访问测试特别说明
    youtube_results = [r for r in results if 'youtube.com' in r['url']]
    youtube_success = len([r for r in youtube_results if r['status'] == 'success'])
    
    if youtube_success > 0:
        print(f"\n🎉 YouTube访问测试: 成功 ({youtube_success}/{len(youtube_results)})")
        print("✅ 代理系统已成功配置为使用YouTube作为测试网站")
    else:
        print(f"\n❌ YouTube访问测试: 失败 (0/{len(youtube_results)})")
        print("⚠️  建议检查：")
        print("   1. Clash客户端是否正在运行")
        print("   2. 代理配置是否正确")
        print("   3. 网络连接是否正常")
    
    return results

if __name__ == "__main__":
    results = test_youtube_proxy()
    
    # 保存结果到JSON文件
    with open('youtube_proxy_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 测试结果已保存到 youtube_proxy_test_results.json")
