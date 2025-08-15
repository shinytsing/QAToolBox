#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理连接测试脚本
用于测试Trojan代理服务器的TCP连接状态
"""

import socket
import time
import sys

# 代理服务器配置
PROXY_SERVERS = [
    {
        'name': 'HongKong-IPLC-HK-1',
        'type': 'trojan',
        'server': 'iplc-hk-1.trojanwheel.com',
        'port': 465,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Hong Kong',
        'category': 'IPLC'
    },
    {
        'name': 'HongKong-IPLC-HK-2',
        'type': 'trojan',
        'server': 'iplc-hk-2.trojanwheel.com',
        'port': 465,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Hong Kong',
        'category': 'IPLC'
    },
    {
        'name': 'Japan-TY-1',
        'type': 'trojan',
        'server': 'ty-1.rise-fuji.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Japan',
        'category': 'Premium'
    },
    {
        'name': 'UnitedStates-US-1',
        'type': 'trojan',
        'server': 'us-1.regentgrandvalley.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'United States',
        'category': 'Premium'
    },
    {
        'name': 'Singapore-SG-1',
        'type': 'trojan',
        'server': 'sg-1.victoriamitrepeak.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Singapore',
        'category': 'Premium'
    },
    {
        'name': 'Australia-AU-1',
        'type': 'trojan',
        'server': 'au-1.australiastudio.com',
        'port': 443,
        'password': 'GUGm7DHtpSx7SuPyUD',
        'country': 'Australia',
        'category': 'Premium'
    }
]

def test_trojan_connection(proxy_config):
    """测试Trojan代理连接"""
    try:
        print(f"🔍 测试 {proxy_config['name']} ({proxy_config['server']}:{proxy_config['port']})...")
        
        # 测试TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        start_time = time.time()
        result = sock.connect_ex((proxy_config['server'], proxy_config['port']))
        response_time = time.time() - start_time
        sock.close()
        
        if result == 0:
            print(f"✅ {proxy_config['name']} - 连接成功 ({response_time:.2f}s)")
            return True
        else:
            print(f"❌ {proxy_config['name']} - 连接失败 (错误码: {result})")
            return False
            
    except socket.timeout:
        print(f"⏰ {proxy_config['name']} - 连接超时")
        return False
    except Exception as e:
        print(f"💥 {proxy_config['name']} - 连接错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试Trojan代理服务器连接...")
    print("=" * 60)
    
    successful_connections = 0
    total_proxies = len(PROXY_SERVERS)
    
    for proxy in PROXY_SERVERS:
        if test_trojan_connection(proxy):
            successful_connections += 1
        print("-" * 40)
        time.sleep(1)  # 避免请求过快
    
    print("=" * 60)
    print(f"📊 测试结果统计:")
    print(f"   总计代理: {total_proxies}")
    print(f"   连接成功: {successful_connections}")
    print(f"   连接失败: {total_proxies - successful_connections}")
    print(f"   成功率: {(successful_connections / total_proxies * 100):.1f}%")
    
    if successful_connections > 0:
        print("\n✅ 有可用的代理服务器！")
        print("💡 建议使用Clash、V2Ray等客户端配置这些代理")
    else:
        print("\n❌ 所有代理服务器都无法连接")
        print("💡 可能的原因:")
        print("   - 代理服务器暂时不可用")
        print("   - 网络环境限制")
        print("   - 需要配置专门的代理客户端")

if __name__ == "__main__":
    main()
