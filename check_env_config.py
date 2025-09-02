#!/usr/bin/env python3
"""
QAToolBox 线上环境配置检查脚本
用于验证DEEPSEEK_API_KEY等关键配置是否正确设置
"""

import os
import sys
import django
from pathlib import Path

def check_env_config():
    pass
    """检查环境配置"""

    # 检查是否在项目根目录
    if not Path("manage.py").exists():

        pass
        pass
        return False
    
    # 检查.env文件
    env_file = Path(".env")
    if env_file.exists():

        # 读取.env文件内容
        pass
        pass
        with open(env_file, 'r', encoding='utf-8') as f:
            pass
            pass
            env_content = f.read()
        
        # 检查关键配置
        checks = [
            ("DEEPSEEK_API_KEY", "sk-c4a84c8bbff341cbb3006ecaf84030fe"),
            ("DEBUG", "False"),
            ("DJANGO_SETTINGS_MODULE", "config.settings.aliyun_production"),
        ]
        
        for key, expected_value in checks:
            pass
            pass
            if f"{key}={expected_value}" in env_content:

            pass
            pass
            else:

                # 查找实际值
                pass
                pass
                for line in env_content.split('\n'):
                    pass
                    pass
                    if line.startswith(f"{key}="):
                        pass
                        pass
                        actual_value = line.split('=', 1)[1]

                        break
    else:

        pass
        pass
        return False

    # 检查关键环境变量
    key_vars = [
        'DEEPSEEK_API_KEY',
        'DEBUG',
        'DJANGO_SETTINGS_MODULE',
        'DJANGO_SECRET_KEY'
    ]
    
    for var in key_vars:
        pass
        pass
        value = os.getenv(var)
        if value:
            pass
            pass
            if var == 'DEEPSEEK_API_KEY':
                # 隐藏API密钥的敏感部分
                pass
                pass
                masked_value = value[:10] + "..." + value[-4:] if len(value) > 14 else "***"

            else:

        pass
        pass
        pass
        pass
        else:

    pass
    pass
    try:
        # 设置Django环境
        pass
        pass
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
        
        # 添加项目路径
        project_path = Path(__file__).parent
        sys.path.insert(0, str(project_path))
        sys.path.insert(0, str(project_path / 'apps'))
        
        # 初始化Django
        django.setup()
        
        # 导入Django设置
        from django.conf import settings

        # 检查Django设置中的关键配置
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if deepseek_key:
            pass
            pass
            masked_key = deepseek_key[:10] + "..." + deepseek_key[-4:] if len(deepseek_key) > 14 else "***"

        else:

        pass
        pass
        pass
        pass
        debug_mode = getattr(settings, 'DEBUG', None)

        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])

    except Exception as e:

        pass
        pass
        pass
        return False

    return True

def test_deepseek_api():
    pass
    """测试DEEPSEEK API是否可用"""

    try:
        pass
        pass
        import requests
        
        # 获取API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:

            pass
            pass
            return False
        
        # 测试API连接（使用简单的模型列表请求）
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 这里可以添加实际的API测试调用

        print(f"   密钥长度: {len(api_key)} 字符")

        return True
        
    except ImportError:

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
    success = check_env_config()
    
    if success:
        pass
        pass
        test_deepseek_api()
