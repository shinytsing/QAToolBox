#!/usr/bin/env python3
"""
测试新的DeepSeek API密钥
"""

import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 设置新的API密钥
os.environ['DEEPSEEK_API_KEY'] = 'sk-08dc86c4bce14049bb4e21f4e6c013f2'

def test_deepseek_api():
    """测试DeepSeek API连接"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    print(f"🔑 使用API密钥: {api_key[:10]}...")
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'user',
                'content': '你好，请简单回复"API测试成功"'
            }
        ],
        'max_tokens': 100,
        'temperature': 0.7
    }
    
    try:
        print("🔄 正在测试DeepSeek API连接...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API测试成功！")
            print(f"🤖 AI回复: {content}")
            return True
        elif response.status_code == 401:
            print("❌ API认证失败 - 请检查API密钥是否正确")
            try:
                error_response = response.json()
                print(f"错误详情: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
        elif response.status_code == 429:
            print("❌ API请求频率超限 - 请稍后重试")
            return False
        elif response.status_code == 500:
            print("❌ DeepSeek服务器内部错误 - 可能是API密钥问题或服务器故障")
            try:
                error_response = response.json()
                print(f"错误详情: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            try:
                error_response = response.json()
                print(f"错误详情: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
            except:
                print(f"错误内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ API请求超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_overview_service():
    """测试OverviewDataService"""
    try:
        print("\n🔄 测试OverviewDataService...")
        
        # 导入服务
        from apps.tools.services.overview_data_service import OverviewDataService
        
        # 创建服务实例
        service = OverviewDataService()
        
        # 测试获取北京信息
        print("📍 测试获取北京信息...")
        result = service.get_overview_data('北京')
        
        if result:
            print("✅ OverviewDataService测试成功！")
            print(f"📊 数据源: {result.get('data_source', 'unknown')}")
            print(f"🕐 最后更新: {result.get('last_updated', 'unknown')}")
            
            # 显示目的地信息
            dest_info = result.get('destination_info', {})
            if dest_info:
                print(f"🏛️ 国家: {dest_info.get('country', 'unknown')}")
                print(f"🗣️ 语言: {', '.join(dest_info.get('languages', []))}")
                print(f"👥 人口: {dest_info.get('population', 'unknown')}")
                print(f"🏙️ 特色: {dest_info.get('famous_for', 'unknown')}")
            
            return True
        else:
            print("❌ OverviewDataService返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ OverviewDataService测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_key_format():
    """测试API密钥格式"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    print(f"🔍 检查API密钥格式...")
    print(f"📏 密钥长度: {len(api_key) if api_key else 0}")
    print(f"🔤 密钥前缀: {api_key[:7] if api_key else 'None'}")
    
    if not api_key:
        print("❌ API密钥为空")
        return False
    elif not api_key.startswith('sk-'):
        print("❌ API密钥格式错误 - 应该以'sk-'开头")
        return False
    elif len(api_key) < 20:
        print("❌ API密钥长度过短")
        return False
    else:
        print("✅ API密钥格式正确")
        return True

if __name__ == "__main__":
    print("🚀 开始测试新的DeepSeek API密钥...")
    print("=" * 50)
    
    # 测试0: API密钥格式
    format_success = test_api_key_format()
    
    # 测试1: 直接API调用
    api_success = test_deepseek_api()
    
    # 测试2: 服务集成测试
    service_success = test_overview_service()
    
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"🔑 API密钥格式: {'✅ 正确' if format_success else '❌ 错误'}")
    print(f"🔑 API直接调用: {'✅ 成功' if api_success else '❌ 失败'}")
    print(f"🔧 服务集成: {'✅ 成功' if service_success else '❌ 失败'}")
    
    if format_success and api_success and service_success:
        print("\n🎉 所有测试通过！新的API密钥工作正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查API密钥配置。")
        
        if not format_success:
            print("💡 建议: 检查API密钥格式是否正确")
        if not api_success:
            print("💡 建议: 检查API密钥是否有效，或联系DeepSeek支持")
        if not service_success:
            print("💡 建议: 检查Django配置和环境变量设置")
