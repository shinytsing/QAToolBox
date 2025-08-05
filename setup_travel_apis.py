#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能旅游攻略生成引擎 - API配置脚本
"""

import os
import re
from pathlib import Path

def validate_api_key(api_key, key_type):
    """验证API密钥格式"""
    if not api_key:
        return False, "API密钥不能为空"
    
    if key_type == "deepseek" and not api_key.startswith('sk-'):
        return False, "DeepSeek API密钥必须以'sk-'开头"
    
    if len(api_key) < 20:
        return False, "API密钥长度不足"
    
    return True, f"{key_type} API密钥格式正确"

def update_env_file(api_configs):
    """更新.env文件中的API配置"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env文件不存在，正在创建...")
        example_file = Path('env.example')
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = """# 环境变量配置文件
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CSE_ID=your-google-cse-id-here
OPENWEATHER_API_KEY=your-openweather-api-key-here
DJANGO_SECRET_KEY=django-insecure-1^6^nfbpnl$vpi=o05c8n+%7#b@ldjegoj6u0-3*!t3a3m#*54
DJANGO_DEBUG=True
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新API配置
    updated_keys = set()
    for i, line in enumerate(lines):
        for key, value in api_configs.items():
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                updated_keys.add(key)
                break
    
    # 添加未找到的配置
    for key, value in api_configs.items():
        if key not in updated_keys:
            lines.append(f'{key}={value}\n')
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def main():
    """主函数"""
    print("🎯 智能旅游攻略生成引擎 - API配置工具")
    print("=" * 50)
    
    # 检查当前配置
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env文件存在")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        apis = {
            'DEEPSEEK_API_KEY': 'DeepSeek API',
            'GOOGLE_API_KEY': 'Google API', 
            'GOOGLE_CSE_ID': 'Google Custom Search Engine ID',
            'OPENWEATHER_API_KEY': 'OpenWeatherMap API'
        }
        
        for key, name in apis.items():
            match = re.search(f'{key}=(.+)', content)
            if match:
                current_value = match.group(1).strip()
                if 'your-' in current_value:
                    print(f"❌ {name}: 使用示例配置")
                else:
                    print(f"✅ {name}: 已配置")
            else:
                print(f"❌ {name}: 未配置")
    else:
        print("❌ .env文件不存在")
    
    print("\n" + "=" * 50)
    
    # 获取用户输入
    api_configs = {}
    
    print("\n🔑 1. DeepSeek API配置")
    print("用途：搜索小红书最新攻略")
    print("获取地址：https://platform.deepseek.com/")
    
    while True:
        deepseek_key = input("\n请输入DeepSeek API密钥: ").strip()
        is_valid, message = validate_api_key(deepseek_key, "deepseek")
        
        if is_valid:
            print(f"✅ {message}")
            api_configs['DEEPSEEK_API_KEY'] = deepseek_key
            break
        else:
            print(f"❌ {message}")
    
    print("\n🔑 2. Google API配置")
    print("用途：搜索马蜂窝2024旅行指南")
    print("获取地址：https://console.cloud.google.com/")
    
    while True:
        google_key = input("\n请输入Google API密钥: ").strip()
        is_valid, message = validate_api_key(google_key, "google")
        
        if is_valid:
            print(f"✅ {message}")
            api_configs['GOOGLE_API_KEY'] = google_key
            break
        else:
            print(f"❌ {message}")
    
    print("\n🔑 3. Google Custom Search Engine ID配置")
    print("用途：自定义搜索马蜂窝网站")
    print("获取地址：https://cse.google.com/")
    
    while True:
        cse_id = input("\n请输入Google Custom Search Engine ID: ").strip()
        if len(cse_id) >= 10:
            print("✅ Custom Search Engine ID格式正确")
            api_configs['GOOGLE_CSE_ID'] = cse_id
            break
        else:
            print("❌ Custom Search Engine ID长度不足")
    
    print("\n🔑 4. OpenWeatherMap API配置")
    print("用途：获取目的地天气数据")
    print("获取地址：https://openweathermap.org/api")
    
    while True:
        weather_key = input("\n请输入OpenWeatherMap API密钥: ").strip()
        is_valid, message = validate_api_key(weather_key, "openweather")
        
        if is_valid:
            print(f"✅ {message}")
            api_configs['OPENWEATHER_API_KEY'] = weather_key
            break
        else:
            print(f"❌ {message}")
    
    # 确认更新
    print(f"\n📝 即将更新以下配置：")
    for key, value in api_configs.items():
        print(f"  {key}: {value[:10]}...")
    
    confirm = input("\n确认更新？(y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', '是']:
        try:
            update_env_file(api_configs)
            print("✅ API配置更新成功！")
            
            # 测试配置
            print("\n🧪 正在测试API配置...")
            os.system('python test_travel_apis.py')
            
        except Exception as e:
            print(f"❌ 更新失败: {str(e)}")
    else:
        print("❌ 取消更新")

if __name__ == "__main__":
    main() 