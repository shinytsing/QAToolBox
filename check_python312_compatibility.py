#!/usr/bin/env python3
"""
Python 3.12 兼容性检查脚本
检查 QAToolBox 项目与 Python 3.12 的兼容性
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 Python版本检查:")
    print(f"   当前版本: {sys.version}")
    print(f"   版本号: {sys.version_info}")
    
    if sys.version_info >= (3, 12):
        print("   ✅ 完全兼容 Python 3.12")
    elif sys.version_info >= (3, 11):
        print("   ✅ 兼容 Python 3.11+")
    else:
        print("   ❌ 需要 Python 3.11 或更高版本")
        return False
    
    return True

def check_django_compatibility():
    """检查Django兼容性"""
    print("\n🚀 Django兼容性检查:")
    
    try:
        import django
        print(f"   Django版本: {django.get_version()}")
        
        # 检查Django版本是否支持Python 3.12
        django_version = tuple(map(int, django.get_version().split('.')[:2]))
        if django_version >= (4, 2):
            print("   ✅ Django 4.2+ 完全支持 Python 3.12")
        else:
            print("   ⚠️ 建议升级到 Django 4.2+ 以获得最佳 Python 3.12 支持")
            
    except ImportError:
        print("   ❌ Django 未安装")
        return False
    
    return True

def check_key_dependencies():
    """检查关键依赖包"""
    print("\n📦 关键依赖包检查:")
    
    dependencies = [
        ('djangorestframework', 'DRF'),
        ('celery', 'Celery'),
        ('redis', 'Redis'),
        ('psycopg2', 'PostgreSQL'),
        ('PIL', 'Pillow'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
    ]
    
    for module_name, display_name in dependencies:
        try:
            if module_name == 'PIL':
                import PIL
                version = PIL.__version__
            else:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', '未知版本')
            
            print(f"   ✅ {display_name}: {version}")
        except ImportError:
            print(f"   ❌ {display_name}: 未安装")
        except Exception as e:
            print(f"   ⚠️ {display_name}: 检查失败 ({e})")

def check_python312_features():
    """检查Python 3.12新特性支持"""
    print("\n✨ Python 3.12 特性支持:")
    
    features = [
        ('f-string语法增强', lambda: eval('f"Hello {x=}"', {'x': 'World'})),
        ('类型注解改进', lambda: eval('x: str = "test"', {})),
        ('match语句', lambda: eval('match 1:\n    case 1: pass', {})),
        ('类型联合语法', lambda: eval('x: str | None = None', {})),
    ]
    
    for feature_name, test_func in features:
        try:
            test_func()
            print(f"   ✅ {feature_name}")
        except Exception as e:
            print(f"   ❌ {feature_name}: {e}")

def check_requirements_files():
    """检查requirements文件"""
    print("\n📋 Requirements文件检查:")
    
    req_files = [
        'requirements/base.txt',
        'requirements/development.txt',
        'requirements/production.txt',
        'requirements.txt'
    ]
    
    for req_file in req_files:
        if Path(req_file).exists():
            print(f"   ✅ {req_file}")
        else:
            print(f"   ❌ {req_file} (不存在)")

def run_compatibility_tests():
    """运行兼容性测试"""
    print("\n🧪 运行兼容性测试:")
    
    try:
        # 尝试运行Django检查
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', '--deploy'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ Django 部署检查通过")
        else:
            print(f"   ⚠️ Django 部署检查发现问题:")
            print(f"      {result.stderr}")
            
    except FileNotFoundError:
        print("   ⚠️ manage.py 未找到，跳过Django检查")
    except subprocess.TimeoutExpired:
        print("   ⚠️ Django 检查超时")
    except Exception as e:
        print(f"   ❌ Django 检查失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 QAToolBox Python 3.12 兼容性检查")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        print("\n❌ Python版本不兼容，请升级到Python 3.11+")
        sys.exit(1)
    
    # 检查Django兼容性
    check_django_compatibility()
    
    # 检查关键依赖
    check_key_dependencies()
    
    # 检查Python 3.12特性
    check_python312_features()
    
    # 检查requirements文件
    check_requirements_files()
    
    # 运行兼容性测试
    run_compatibility_tests()
    
    print("\n" + "=" * 60)
    print("🎉 兼容性检查完成！")
    print("=" * 60)
    
    print("\n💡 建议:")
    print("   • 如果发现兼容性问题，请更新相关依赖包")
    print("   • 使用 requirements/ 目录中的最新依赖文件")
    print("   • 定期检查依赖包的更新")
    print("   • 在生产环境部署前进行完整测试")

if __name__ == "__main__":
    main()
