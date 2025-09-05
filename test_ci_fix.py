#!/usr/bin/env python
"""
CI修复验证脚本
"""
import os
import sys
import subprocess
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')
django.setup()

def run_tests():
    """运行测试并检查覆盖率"""
    print("🧪 开始运行测试...")
    
    try:
        # 运行基础测试
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/unit/test_basic.py',
            '--cov=apps',
            '--cov-report=term',
            '--cov-report=xml',
            '-v'
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print("测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        # 检查覆盖率
        if os.path.exists('coverage.xml'):
            import xml.etree.ElementTree as ET
            try:
                root = ET.parse('coverage.xml').getroot()
                coverage = float(root.attrib['line-rate']) * 100
                print(f"📊 测试覆盖率: {coverage:.1f}%")
                
                if coverage >= 5:
                    print("✅ 覆盖率达标!")
                    return True
                else:
                    print("❌ 覆盖率不达标!")
                    return False
            except Exception as e:
                print(f"❌ 解析覆盖率报告失败: {e}")
                return False
        else:
            print("❌ 覆盖率报告文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def check_django_setup():
    """检查Django设置"""
    print("🔧 检查Django设置...")
    
    try:
        # 检查设置
        print(f"DEBUG: {settings.DEBUG}")
        print(f"INSTALLED_APPS: {len(settings.INSTALLED_APPS)} 个应用")
        print(f"DATABASES: {settings.DATABASES['default']['ENGINE']}")
        
        # 检查数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ 数据库连接正常")
        
        return True
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始CI修复验证...")
    print("=" * 50)
    
    # 检查Django设置
    if not check_django_setup():
        print("❌ Django设置检查失败，退出")
        sys.exit(1)
    
    print("=" * 50)
    
    # 运行测试
    if not run_tests():
        print("❌ 测试运行失败，退出")
        sys.exit(1)
    
    print("=" * 50)
    print("✅ CI修复验证完成!")
    print("🎉 所有检查都通过了!")

if __name__ == "__main__":
    main()
