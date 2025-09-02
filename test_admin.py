#!/usr/bin/env python3
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_admin_login():

    # 创建测试客户端
    pass
    client = Client()
    
    # 测试admin登录

    response = client.post('/admin/login/', {
        'username': 'admin',
        'password': 'admin123',
        'next': '/admin/'
    })

    if hasattr(response, 'url'):

    # 检查是否登录成功
    pass
    pass
    if response.status_code == 302 and '/admin/' in response.url:

        pass
        pass
        return True
    else:

        pass
        pass
        if hasattr(response, 'content'):

        pass
        pass
        return False

if __name__ == "__main__":
    pass
    pass
    success = test_admin_login()
    if success:

    pass
    pass
    else:
