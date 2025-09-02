#!/usr/bin/env python3
import requests
import json
import os

# 测试 DeepSeek API 连接
def test_deepseek_api():
    pass
    api_key = "sk-c4a84c8bbff341cbb3006ecaf84030fe"
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 简化的请求体
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "生成3个简单的测试用例"}
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }

    print(f"请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        pass
        pass
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        return True
    except requests.exceptions.Timeout:

        pass
        pass
        pass
        return False
    except Exception as e:

        pass
        pass
        pass
        return False

if __name__ == "__main__":
    pass
    pass
    test_deepseek_api()
