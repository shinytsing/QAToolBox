#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试DeepSeek API问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from apps.tools.utils import DeepSeekClient
import requests
import json

def test_simple_api_call():
    """测试简单的API调用"""
    print("=== 测试简单API调用 ===")
    
    try:
        client = DeepSeekClient()
        print(f"API Key: {client.api_key[:10]}...")
        
        # 简单的测试请求
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            "temperature": 0.3,
            "max_tokens": 100,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client.api_key}"
        }
        
        print("发送请求...")
        response = requests.post(
            client.API_BASE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {result}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

def test_with_different_models():
    """测试不同的模型"""
    print("\n=== 测试不同模型 ===")
    
    models = ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]
    
    for model in models:
        print(f"\n测试模型: {model}")
        try:
            client = DeepSeekClient()
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "temperature": 0.3,
                "max_tokens": 100,
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {client.api_key}"
            }
            
            response = requests.post(
                client.API_BASE_URL,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✓ 成功: {result['choices'][0]['message']['content']}")
            else:
                print(f"✗ 失败: {response.text}")
                
        except Exception as e:
            print(f"✗ 错误: {str(e)}")

if __name__ == "__main__":
    test_simple_api_call()
    test_with_different_models() 