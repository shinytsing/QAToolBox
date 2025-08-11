#!/usr/bin/env python3
"""
测试免费API功能
验证DuckDuckGo和wttr.in API是否正常工作
"""

import requests
import json
import time

def test_duckduckgo_api():
    """测试DuckDuckGo API"""
    print("🔍 测试DuckDuckGo API...")
    
    try:
        # 测试DuckDuckGo Instant Answer API
        url = "https://api.duckduckgo.com/"
        params = {
            'q': '上海 马蜂窝2024旅行指南',
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ DuckDuckGo API连接正常")
            
            # 显示返回的数据结构
            print(f"  AbstractText: {data.get('AbstractText', '无')[:100]}...")
            print(f"  RelatedTopics数量: {len(data.get('RelatedTopics', []))}")
            
            return True
        else:
            print(f"❌ DuckDuckGo API连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ DuckDuckGo API连接异常: {e}")
        return False

def test_wttr_api():
    """测试wttr.in API"""
    print("\n🌤️ 测试wttr.in API...")
    
    try:
        # 测试wttr.in天气API
        url = "https://wttr.in/上海?format=j1"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ wttr.in API连接正常")
            
            # 显示天气数据
            if 'current_condition' in data and data['current_condition']:
                current = data['current_condition'][0]
                print(f"  温度: {current.get('temp_C', 'N/A')}°C")
                print(f"  天气: {current.get('weatherDesc', [{}])[0].get('value', 'N/A')}")
                print(f"  湿度: {current.get('humidity', 'N/A')}%")
                print(f"  风速: {current.get('windspeedKmph', 'N/A')} km/h")
            
            return True
        else:
            print(f"❌ wttr.in API连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ wttr.in API连接异常: {e}")
        return False

def test_deepseek_api():
    """测试DeepSeek API"""
    print("\n🤖 测试DeepSeek API...")
    
    import os
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DeepSeek API密钥未配置")
        return False
    
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": "Hello, this is a test message."}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ DeepSeek API连接正常")
            return True
        else:
            print(f"❌ DeepSeek API连接失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek API连接异常: {e}")
        return False

def test_network_connectivity():
    """测试网络连接"""
    print("\n🌐 测试网络连接...")
    
    test_urls = [
        "https://api.duckduckgo.com",
        "https://wttr.in",
        "https://api.deepseek.com",
        "https://www.baidu.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - 连接正常 ({response.status_code})")
        except Exception as e:
            print(f"❌ {url} - 连接失败: {e}")

def test_travel_service():
    """测试旅游服务"""
    print("\n🚀 测试旅游服务...")
    
    import os
    import sys
    import django
    
    # 设置Django环境
    sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    django.setup()
    
    from apps.tools.services.travel_data_service import TravelDataService
    
    try:
        travel_service = TravelDataService()
        
        # 测试数据抓取
        print("  测试数据抓取...")
        raw_data = travel_service._数据抓取阶段("上海")
        
        # 显示抓取结果
        for source, data in raw_data.items():
            if isinstance(data, dict) and 'error' in data:
                print(f"    ❌ {source}: {data['error']}")
            else:
                print(f"    ✅ {source}: 数据获取成功")
        
        # 测试数据验证
        print("  测试数据验证...")
        is_valid = travel_service._has_valid_data(raw_data)
        print(f"    数据有效性: {'✅ 有效' if is_valid else '❌ 无效'}")
        
        if is_valid:
            # 测试信息结构化
            print("  测试信息结构化...")
            structured_data = travel_service._信息结构化(raw_data, "上海")
            print(f"    景点数量: {len(structured_data['景点'])}")
            print(f"    美食数量: {len(structured_data['美食'])}")
            print(f"    贴士数量: {len(structured_data['贴士'])}")
            
            return True
        else:
            print("    ❌ 数据验证失败")
            return False
            
    except Exception as e:
        print(f"    ❌ 旅游服务测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 免费API功能测试")
    print("=" * 50)
    
    # 测试网络连接
    test_network_connectivity()
    
    # 测试各个API
    duckduckgo_ok = test_duckduckgo_api()
    wttr_ok = test_wttr_api()
    deepseek_ok = test_deepseek_api()
    
    # 测试旅游服务
    travel_ok = test_travel_service()
    
    # 总结
    print("\n📊 测试结果:")
    print(f"DuckDuckGo API: {'✅ 正常' if duckduckgo_ok else '❌ 异常'}")
    print(f"wttr.in API: {'✅ 正常' if wttr_ok else '❌ 异常'}")
    print(f"DeepSeek API: {'✅ 正常' if deepseek_ok else '❌ 异常'}")
    print(f"旅游服务: {'✅ 正常' if travel_ok else '❌ 异常'}")
    
    if duckduckgo_ok and wttr_ok and deepseek_ok:
        print("\n🎉 所有免费API测试通过！")
    else:
        print("\n⚠️ 部分API测试失败，但系统仍可正常工作")

if __name__ == "__main__":
    main() 