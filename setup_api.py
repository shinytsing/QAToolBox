#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API 配置脚本
交互式帮助用户配置API密钥
"""

import os
import re
from pathlib import Path

def validate_api_key(api_key):
    """验证API密钥格式"""
    if not api_key:
        return False, "API密钥不能为空"
    
    if not api_key.startswith('sk-'):
        return False, "API密钥必须以'sk-'开头"
    
    if len(api_key) < 20:
        return False, "API密钥长度不足"
    
    # 检查是否包含特殊字符
    if not re.match(r'^sk-[a-zA-Z0-9_-]+$', api_key):
        return False, "API密钥包含无效字符"
    
    return True, "API密钥格式正确"

def update_env_file(api_key):
    """更新.env文件中的API密钥"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env文件不存在，正在创建...")
        # 复制env.example
        example_file = Path('env.example')
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = """# 环境变量配置文件
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
DJANGO_SECRET_KEY=django-insecure-1^6^nfbpnl$vpi=o05c8n+%7#b@ldjegoj6u0-3*!t3a3m#*54
DJANGO_DEBUG=True
API_RATE_LIMIT=10/minute
"""
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # 读取现有内容
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新API密钥
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DEEPSEEK_API_KEY='):
            lines[i] = f'DEEPSEEK_API_KEY={api_key}\n'
            updated = True
            break
    
    if not updated:
        # 如果没有找到，添加到文件末尾
        lines.append(f'DEEPSEEK_API_KEY={api_key}\n')
    
    # 写回文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def main():
    """主函数"""
    print("🔧 DeepSeek API 配置工具")
    print("=" * 50)
    
    # 检查当前配置
    print("📋 当前配置状态：")
    
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env文件存在")
        
        # 读取当前API密钥
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找API密钥
        match = re.search(r'DEEPSEEK_API_KEY=(.+)', content)
        if match:
            current_key = match.group(1).strip()
            if current_key == 'sk-your-actual-api-key-here':
                print("❌ 当前使用示例API密钥")
            else:
                print(f"✅ 当前API密钥: {current_key[:10]}...")
                is_valid, message = validate_api_key(current_key)
                if is_valid:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
        else:
            print("❌ 未找到API密钥配置")
    else:
        print("❌ .env文件不存在")
    
    print("\n" + "=" * 50)
    
    # 获取用户输入
    print("🔑 请输入您的DeepSeek API密钥：")
    print("提示：API密钥格式为 sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    print("您可以从 https://platform.deepseek.com/ 获取API密钥")
    
    while True:
        api_key = input("\n请输入API密钥: ").strip()
        
        # 验证API密钥
        is_valid, message = validate_api_key(api_key)
        
        if is_valid:
            print(f"✅ {message}")
            break
        else:
            print(f"❌ {message}")
            print("请重新输入正确的API密钥")
    
    # 确认更新
    print(f"\n📝 即将更新API密钥为: {api_key[:10]}...")
    confirm = input("确认更新？(y/N): ").strip().lower()
    
    if confirm in ['y', 'yes', '是']:
        try:
            update_env_file(api_key)
            print("✅ API密钥更新成功！")
            
            # 测试配置
            print("\n🧪 正在测试API配置...")
            os.system('python test_deepseek_api.py')
            
        except Exception as e:
            print(f"❌ 更新失败: {str(e)}")
    else:
        print("❌ 取消更新")

if __name__ == "__main__":
    main() 