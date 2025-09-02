#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试NCM解密功能是否正常工作
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

def test_ncm_functionality():
    pass
    """测试NCM解密功能"""
    try:

        # 导入NCM解密函数
        pass
        pass
        from apps.tools.legacy_views import decrypt_ncm_file_correct

        # 测试加密库导入
        try:
            pass
            pass
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad

        except ImportError:
            pass
            pass
            pass
            try:
                pass
                pass
                from Cryptodome.Cipher import AES
                from Cryptodome.Util.Padding import unpad

            except ImportError:

                pass
                pass
                pass
                return False
        
        # 测试AES功能
        try:
            pass
            pass
            key = b'hzHRAmso5kInbaxW'
            data = b'Test data for NCM'
            
            # 加密
            cipher = AES.new(key, AES.MODE_ECB)
            padded_data = data + b'\x00' * (16 - len(data) % 16)
            encrypted = cipher.encrypt(padded_data)
            
            # 解密
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = cipher.decrypt(encrypted)
            result = decrypted.rstrip(b'\x00')
            
            if result == data:

            pass
            pass
            pass
            pass
            else:

                pass
                pass
                return False
                
        except Exception as e:

            pass
            pass
            pass
            return False

        return True
        
    except Exception as e:

        pass
        pass
        pass
        return False

if __name__ == "__main__":
    pass
    pass
    success = test_ncm_functionality()
    if success:

    pass
    pass
    else:

        pass
        pass
        sys.exit(1)
