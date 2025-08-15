#!/usr/bin/env python3
"""
测试DeepSeek Vision API格式
"""

import os
import sys
import django
from pathlib import Path
import base64
import requests
import json

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_deepseek_vision_api():
    """测试DeepSeek Vision API"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY 未配置")
        return False
    
    print("🧪 测试DeepSeek Vision API格式...")
    
    # 测试图像路径
    test_image_path = "static/img/food/beef-4805622_1280.jpg"
    if not os.path.exists(test_image_path):
        print(f"❌ 测试图像不存在: {test_image_path}")
        return False
    
    # 编码图像
    with open(test_image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 测试不同的API格式
    test_formats = [
        {
            "name": "deepseek-chat with image",
            "payload": {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "这是什么食品？"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
        },
        {
            "name": "deepseek-vision",
            "payload": {
                "model": "deepseek-vision",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "这是什么食品？"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
        },
        {
            "name": "deepseek-chat with detail",
            "payload": {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "这是什么食品？"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "low"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 100
            }
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    for i, test_format in enumerate(test_formats, 1):
        print(f"\n🔍 测试格式 {i}: {test_format['name']}")
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=test_format['payload'],
                timeout=30
            )
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"  ✅ 成功: {content[:100]}...")
                return test_format['name']
            else:
                error_text = response.text[:200]
                print(f"  ❌ 失败: {error_text}")
                
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    return None

def test_simple_text_api():
    """测试简单的文本API"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY 未配置")
        return False
    
    print("\n🧪 测试简单文本API...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单回复一下"
            }
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"  ✅ 文本API成功: {content}")
            return True
        else:
            error_text = response.text[:200]
            print(f"  ❌ 文本API失败: {error_text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 文本API异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 DeepSeek API格式测试")
    print("=" * 50)
    
    # 测试文本API
    text_api_works = test_simple_text_api()
    
    # 测试Vision API
    working_format = test_deepseek_vision_api()
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"  文本API: {'✅ 正常' if text_api_works else '❌ 失败'}")
    print(f"  Vision API: {'✅ 正常' if working_format else '❌ 失败'}")
    
    if working_format:
        print(f"  工作格式: {working_format}")
    
    return text_api_works and working_format is not None

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
