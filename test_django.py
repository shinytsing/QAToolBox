#!/usr/bin/env python
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    print("✅ Django设置成功")
    
    from django.conf import settings
    print(f"✅ 设置模块: {settings.SETTINGS_MODULE}")
    
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ 数据库连接正常")
    
    print("🎉 基本功能正常！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
