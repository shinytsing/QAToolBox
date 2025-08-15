#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代理系统功能测试脚本
测试IP对比和真实代理功能
"""

import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_ENDPOINTS = [
    "/tools/api/proxy/ip-comparison/",
    "/tools/api/proxy/connection-test/",
    "/tools/api/proxy/list/"
]

def test_endpoint(endpoint, method="GET", data=None):
    """测试API端点"""
    try:
        url = BASE_URL + endpoint
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'ProxySystemTest/1.0'
        }
        
        print(f"🔍 测试端点: {endpoint}")
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功: {endpoint}")
                return result
            else:
                print(f"❌ 失败: {endpoint} - {result.get('error', '未知错误')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code} - {endpoint}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: 无法连接到 {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ 异常: {str(e)} - {endpoint}")
        return None

def test_ip_comparison():
    """测试IP对比功能"""
    print("\n" + "="*50)
    print("🌐 测试IP对比功能")
    print("="*50)
    
    result = test_endpoint("/tools/api/proxy/ip-comparison/")
    if result:
        data = result.get('data', {})
        print(f"📊 IP对比结果:")
        
        # 直连IP
        direct_ip = data.get('direct_ip', {})
        if direct_ip.get('success'):
            print(f"   🌐 直连IP: {direct_ip.get('ip', 'N/A')}")
        else:
            print(f"   🌐 直连IP: 获取失败 - {direct_ip.get('error', '未知错误')}")
        
        # 代理IP
        proxy_ip = data.get('proxy_ip', {})
        if proxy_ip and proxy_ip.get('success'):
            print(f"   🔗 代理IP: {proxy_ip.get('ip', 'N/A')} (通过: {proxy_ip.get('proxy_used', 'N/A')})")
        else:
            print(f"   🔗 代理IP: 获取失败 - {proxy_ip.get('error', '无可用代理') if proxy_ip else '无可用代理'}")

def test_connection_status():
    """测试连接状态"""
    print("\n" + "="*50)
    print("🔗 测试代理连接状态")
    print("="*50)
    
    result = test_endpoint("/tools/api/proxy/connection-test/")
    if result:
        data = result.get('data', {})
        stats = data.get('statistics', {})
        
        print(f"📊 连接统计:")
        print(f"   总计代理: {stats.get('total_proxies', 0)}")
        print(f"   连接成功: {stats.get('connected_proxies', 0)}")
        print(f"   成功率: {stats.get('connection_rate', 0)}%")
        
        # 显示详细结果
        results = data.get('proxy_results', [])
        for proxy_result in results:
            status = "✅" if proxy_result.get('success') else "❌"
            print(f"   {status} {proxy_result.get('proxy', 'N/A')}: {proxy_result.get('status', 'unknown')}")

def test_proxy_list():
    """测试代理列表"""
    print("\n" + "="*50)
    print("📋 测试代理列表")
    print("="*50)
    
    result = test_endpoint("/tools/api/proxy/list/")
    if result:
        data = result.get('data', {})
        proxies = data.get('proxies_by_country', {})
        
        print(f"📊 代理列表:")
        for country, proxy_list in proxies.items():
            print(f"   🌍 {country}: {len(proxy_list)} 个代理")
            for proxy in proxy_list:
                print(f"      - {proxy.get('name', 'N/A')} ({proxy.get('category', 'N/A')})")

def main():
    """主函数"""
    print("🚀 代理系统功能测试")
    print("="*50)
    print(f"目标服务器: {BASE_URL}")
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试各个功能
    test_ip_comparison()
    test_connection_status()
    test_proxy_list()
    
    print("\n" + "="*50)
    print("✅ 测试完成")
    print("="*50)

if __name__ == "__main__":
    main()
