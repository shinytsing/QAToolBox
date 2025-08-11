#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能旅游攻略生成引擎 - 免费API配置脚本
"""

import os
import re
from pathlib import Path

def update_env_file():
    """更新.env文件中的免费API配置"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env文件不存在，正在创建...")
        example_file = Path('env.example')
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = """# 环境变量配置文件
# 免费API配置 - 无需密钥
# 使用DuckDuckGo API (免费)
# 使用wttr.in API (免费)
# 使用维基百科API (免费)

DJANGO_SECRET_KEY=django-insecure-1^6^nfbpnl$vpi=o05c8n+%7#b@ldjegoj6u0-3*!t3a3m#*54
DJANGO_DEBUG=True
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 移除需要密钥的API配置
    lines_to_remove = []
    for i, line in enumerate(lines):
        if any(key in line for key in ['DEEPSEEK_API_KEY', 'GOOGLE_API_KEY', 'GOOGLE_CSE_ID', 'OPENWEATHER_API_KEY']):
            lines_to_remove.append(i)
    
    # 从后往前删除，避免索引变化
    for i in reversed(lines_to_remove):
        del lines[i]
    
    # 添加免费API说明
    free_api_comment = """# 免费API配置 - 无需密钥
# 使用DuckDuckGo API (免费) - 搜索旅游信息
# 使用wttr.in API (免费) - 获取天气数据
# 使用维基百科API (免费) - 获取目的地信息

"""
    
    # 在文件开头添加说明
    lines.insert(0, free_api_comment)
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def test_free_apis():
    """测试免费API连接"""
    import requests
    
    print("\n🧪 测试免费API连接...")
    
    # 测试DuckDuckGo API
    try:
        response = requests.get("https://api.duckduckgo.com/?q=北京旅游&format=json&no_html=1", timeout=10)
        if response.status_code == 200:
            print("✅ DuckDuckGo API: 连接正常")
        else:
            print(f"❌ DuckDuckGo API: 连接失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ DuckDuckGo API: 连接失败 ({str(e)})")
    
    # 测试wttr.in API
    try:
        response = requests.get("https://wttr.in/北京?format=j1", timeout=10)
        if response.status_code == 200:
            print("✅ wttr.in API: 连接正常")
        else:
            print(f"❌ wttr.in API: 连接失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ wttr.in API: 连接失败 ({str(e)})")
    
    # 测试维基百科API
    try:
        response = requests.get("https://zh.wikipedia.org/api/rest_v1/page/summary/北京", timeout=10)
        if response.status_code == 200:
            print("✅ 维基百科API: 连接正常")
        else:
            print(f"❌ 维基百科API: 连接失败 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 维基百科API: 连接失败 ({str(e)})")

def main():
    """主函数"""
    print("🎯 智能旅游攻略生成引擎 - 免费API配置工具")
    print("=" * 50)
    
    print("\n📋 当前使用的免费API:")
    print("✅ DuckDuckGo API - 搜索旅游信息")
    print("✅ wttr.in API - 获取天气数据")
    print("✅ 维基百科API - 获取目的地信息")
    
    print("\n💡 优势:")
    print("• 完全免费，无需API密钥")
    print("• 无需注册账号")
    print("• 无使用限制")
    print("• 数据来源可靠")
    
    print("\n" + "=" * 50)
    
    # 检查当前配置
    env_file = Path('.env')
    if env_file.exists():
        print("\n✅ .env文件存在")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有需要密钥的API配置
        paid_apis = {
            'DEEPSEEK_API_KEY': 'DeepSeek API',
            'GOOGLE_API_KEY': 'Google API', 
            'GOOGLE_CSE_ID': 'Google Custom Search Engine ID',
            'OPENWEATHER_API_KEY': 'OpenWeatherMap API'
        }
        
        found_paid_apis = []
        for key, name in paid_apis.items():
            if key in content:
                found_paid_apis.append(name)
        
        if found_paid_apis:
            print(f"⚠️ 发现付费API配置: {', '.join(found_paid_apis)}")
            print("这些API将被移除，改用免费API")
        else:
            print("✅ 已使用免费API配置")
    else:
        print("❌ .env文件不存在，将创建新文件")
    
    print("\n" + "=" * 50)
    
    # 确认更新
    print("\n📝 即将更新配置为免费API：")
    print("• 移除所有需要密钥的API配置")
    print("• 使用DuckDuckGo API进行搜索")
    print("• 使用wttr.in API获取天气")
    print("• 使用维基百科API获取信息")
    
    confirm = input("\n确认更新？(y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', '是']:
        try:
            update_env_file()
            print("✅ 免费API配置更新成功！")
            
            # 测试API连接
            test_free_apis()
            
            print("\n🎉 配置完成！")
            print("现在可以使用完全免费的旅游攻略生成功能了。")
            
        except Exception as e:
            print(f"❌ 更新失败: {str(e)}")
    else:
        print("❌ 取消更新")

if __name__ == "__main__":
    main() 