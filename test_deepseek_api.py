#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 测试脚本
用于验证API配置和调用是否正常
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_api():
    """测试DeepSeek API调用"""
    
    # 获取API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    print("=== DeepSeek API 测试 ===")
    print(f"API密钥: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        print("❌ 错误: API密钥未配置")
        print("请在.env文件中设置DEEPSEEK_API_KEY")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ 错误: API密钥格式不正确，应以sk-开头")
        return False
    
    # 测试请求
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
        "max_tokens": 100,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stream": False
    }
    
    print(f"请求URL: {url}")
    print(f"请求头: {headers}")
    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if 'choices' in result and result['choices']:
                content = result['choices'][0]['message']['content']
                print(f"✅ API调用成功！")
                print(f"AI回复: {content}")
                return True
            else:
                print("❌ 响应格式错误：缺少choices字段")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            try:
                error_response = response.json()
                print(f"错误详情: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
        return False

def test_environment():
    """测试环境配置"""
    print("\n=== 环境配置测试 ===")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print("✅ .env文件存在")
    else:
        print("❌ .env文件不存在")
    
    # 检查API密钥
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        print("✅ API密钥已配置")
        if api_key.startswith('sk-'):
            print("✅ API密钥格式正确")
        else:
            print("❌ API密钥格式不正确")
    else:
        print("❌ API密钥未配置")
    
    # 检查其他环境变量
    django_secret = os.getenv('DJANGO_SECRET_KEY')
    if django_secret:
        print("✅ Django密钥已配置")
    else:
        print("❌ Django密钥未配置")

if __name__ == "__main__":
    print("开始测试DeepSeek API...")
    
    # 测试环境配置
    test_environment()
    
    # 测试API调用
    success = test_deepseek_api()
    
    if success:
        print("\n🎉 所有测试通过！API配置正确。")
    else:
        print("\n💡 测试失败，请检查以下问题：")
        print("1. 确保.env文件存在并包含正确的API密钥")
        print("2. 确保API密钥格式正确（以sk-开头）")
        print("3. 确保网络连接正常")
        print("4. 检查API密钥是否有效") 