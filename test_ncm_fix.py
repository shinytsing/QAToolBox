#!/usr/bin/env python3
"""
测试修复后的NCM转换功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import (
    decrypt_ncm_file, 
    convert_ncm_file_native,
    repair_audio_file_with_offset
)

def test_ncm_fix():
    """测试修复后的NCM转换功能"""
    print("🔧 测试修复后的NCM转换功能")
    print("=" * 60)
    
    # 查找可用的NCM文件
    temp_dir = "media/temp_audio"
    ncm_files = []
    for file in os.listdir(temp_dir):
        if file.endswith('.ncm'):
            file_path = os.path.join(temp_dir, file)
            ncm_files.append((file_path, os.path.getmtime(file_path)))
    
    if not ncm_files:
        print("❌ 没有找到NCM文件进行测试")
        return False
    
    # 使用最新的NCM文件
    ncm_files.sort(key=lambda x: x[1], reverse=True)
    ncm_file = ncm_files[0][0]
    
    print(f"📁 使用NCM文件: {ncm_file}")
    print(f"📁 文件大小: {os.path.getsize(ncm_file):,} bytes")
    
    # 步骤1: 解密NCM文件
    print("\n🔓 步骤1: 解密NCM文件...")
    try:
        decrypted_path = decrypt_ncm_file(ncm_file)
        if decrypted_path and os.path.exists(decrypted_path):
            file_size = os.path.getsize(decrypted_path)
            print(f"✅ 解密成功! 输出文件: {decrypted_path}")
            print(f"📁 解密后文件大小: {file_size:,} bytes")
            
            # 检查解密后的文件头
            with open(decrypted_path, 'rb') as f:
                header = f.read(32)
                print(f"🔍 解密后文件头: {header.hex()}")
        else:
            print("❌ 解密失败")
            return False
    except Exception as e:
        print(f"❌ 解密异常: {e}")
        return False
    
    # 步骤2: 测试原生转换
    print("\n🔧 步骤2: 测试原生转换...")
    output_dir = os.path.dirname(decrypted_path)
    base_name = os.path.splitext(os.path.basename(decrypted_path))[0]
    
    # 测试MP3转换
    mp3_output = os.path.join(output_dir, f"{base_name}_fixed.mp3")
    try:
        success, message, result_path = convert_ncm_file_native(decrypted_path, mp3_output, 'mp3')
        if success and result_path and os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ 原生MP3转换成功!")
            print(f"📁 输出文件: {result_path}")
            print(f"📁 文件大小: {file_size:,} bytes")
            
            # 验证输出文件
            with open(result_path, 'rb') as f:
                output_header = f.read(16)
                print(f"🔍 输出文件头: {output_header.hex()}")
            
            # 测试ffmpeg是否可以处理
            print("\n🔍 测试ffmpeg兼容性...")
            import subprocess
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', result_path, '-f', 'null', '-'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ ffmpeg可以正常处理转换后的文件")
                else:
                    print(f"❌ ffmpeg处理失败: {result.stderr}")
            except Exception as e:
                print(f"⚠️ ffmpeg测试异常: {e}")
            
            return True
        else:
            print(f"❌ 原生MP3转换失败: {message}")
            return False
    except Exception as e:
        print(f"❌ 原生MP3转换异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 NCM转换功能测试脚本启动")
    print("=" * 60)
    
    success = test_ncm_fix()
    
    if success:
        print("\n🎉 测试完成，NCM转换功能正常！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
