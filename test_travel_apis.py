#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能旅游攻略生成引擎 - API测试脚本
用于验证所有API配置和调用是否正常
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_api():
    """测试DeepSeek API调用"""
    print("\n=== DeepSeek API 测试 ===")
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ 错误: DeepSeek API密钥未配置")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ 错误: DeepSeek API密钥格式不正确")
        return False
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": "请简单回复'测试成功'"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and result['choices']:
                content = result['choices'][0]['message']['content']
                print(f"✅ DeepSeek API调用成功！")
                print(f"AI回复: {content}")
                return True
            else:
                print("❌ 响应格式错误")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_google_api():
    """测试Google Custom Search API调用"""
    print("\n=== Google Custom Search API 测试 ===")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    cse_id = os.getenv('GOOGLE_CSE_ID')
    
    if not api_key:
        print("❌ 错误: Google API密钥未配置")
        return False
    
    if not cse_id:
        print("❌ 错误: Google Custom Search Engine ID未配置")
        return False
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': '北京旅游',
        'num': 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and data['items']:
                print(f"✅ Google Custom Search API调用成功！")
                print(f"搜索结果数量: {len(data['items'])}")
                return True
            else:
                print("❌ 未找到搜索结果")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_openweather_api():
    """测试OpenWeatherMap API调用"""
    print("\n=== OpenWeatherMap API 测试 ===")
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("❌ 错误: OpenWeatherMap API密钥未配置")
        return False
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': 'Beijing',
        'appid': api_key,
        'units': 'metric',
        'lang': 'zh_cn'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'main' in data and 'weather' in data:
                temp = data['main']['temp']
                weather = data['weather'][0]['description']
                print(f"✅ OpenWeatherMap API调用成功！")
                print(f"北京天气: {temp}°C, {weather}")
                return True
            else:
                print("❌ 响应格式错误")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_travel_data_service():
    """测试旅游数据服务"""
    print("\n=== 旅游数据服务测试 ===")
    
    try:
        from apps.tools.services.travel_data_service import TravelDataService
        
        service = TravelDataService()
        
        # 测试基本信息提取
        test_text = "推荐景点：故宫博物院、天安门广场 必吃：北京烤鸭、炸酱面 注意：避开节假日高峰"
        result = service.提取核心信息(test_text)
        
        print(f"✅ 信息提取功能正常")
        print(f"提取结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 服务测试失败: {str(e)}")
        return False

def check_environment():
    """检查环境配置"""
    print("=== 环境配置检查 ===")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
    else:
        print("❌ .env文件不存在")
    
    # 检查各个API密钥
    apis = {
        'DEEPSEEK_API_KEY': 'DeepSeek API',
        'GOOGLE_API_KEY': 'Google API',
        'GOOGLE_CSE_ID': 'Google Custom Search Engine ID',
        'OPENWEATHER_API_KEY': 'OpenWeatherMap API'
    }
    
    for key, name in apis.items():
        value = os.getenv(key)
        if value:
            if 'your-' in value:
                print(f"❌ {name}: 使用示例配置")
            else:
                print(f"✅ {name}: 已配置")
        else:
            print(f"❌ {name}: 未配置")

def main():
    """主函数"""
    print("🎯 智能旅游攻略生成引擎 - API测试")
    print("=" * 50)
    
    # 检查环境配置
    check_environment()
    
    # 测试各个API
    results = []
    
    results.append(test_deepseek_api())
    results.append(test_google_api())
    results.append(test_openweather_api())
    results.append(test_travel_data_service())
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结")
    print("=" * 50)
    
    test_names = [
        "DeepSeek API",
        "Google Custom Search API", 
        "OpenWeatherMap API",
        "旅游数据服务"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i+1}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n总体结果: {success_count}/{total_count} 项测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试通过！API配置正确，可以开始使用智能旅游攻略生成引擎。")
    else:
        print("\n💡 部分测试失败，请检查以下问题：")
        print("1. 确保.env文件存在并包含正确的API密钥")
        print("2. 确保所有API密钥格式正确")
        print("3. 确保网络连接正常")
        print("4. 检查API密钥是否有效且已启用相应服务")

if __name__ == "__main__":
    main() 