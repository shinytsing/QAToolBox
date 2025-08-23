#!/usr/bin/env python3
"""
测试简单日记页面的修复
"""

import requests
import json

def test_simple_diary_page():
    """测试简单日记页面"""
    try:
        # 测试页面访问
        response = requests.get('http://localhost:8000/tools/simple-diary/')
        print(f"页面访问状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 页面访问成功")
            
            # 检查页面内容
            content = response.text
            if '简单生活日记' in content:
                print("✅ 页面标题正确")
            else:
                print("❌ 页面标题不正确")
                
            # 检查CSS变量定义
            if '--text-color: #2c3e50' in content:
                print("✅ 文字颜色变量已定义")
            else:
                print("❌ 文字颜色变量未定义")
                
            # 检查JavaScript函数
            if 'displayDefaultTemplates' in content:
                print("✅ 默认模板函数已添加")
            else:
                print("❌ 默认模板函数未添加")
                
        else:
            print(f"❌ 页面访问失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_diary_templates_api():
    """测试日记模板API"""
    try:
        response = requests.get('http://localhost:8000/tools/api/diary/templates/')
        print(f"\nAPI访问状态: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API访问成功")
            
            try:
                data = response.json()
                if data.get('success'):
                    print(f"✅ API返回成功，模板数量: {len(data.get('templates', []))}")
                else:
                    print(f"❌ API返回失败: {data.get('error', '未知错误')}")
            except json.JSONDecodeError:
                print("❌ API返回的不是有效JSON")
                
        elif response.status_code == 302:
            print("⚠️ API重定向，可能需要登录")
        else:
            print(f"❌ API访问失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except Exception as e:
        print(f"❌ API测试失败: {e}")

if __name__ == '__main__':
    print("🧪 开始测试简单日记页面修复...")
    test_simple_diary_page()
    test_diary_templates_api()
    print("\n🎯 测试完成！")
