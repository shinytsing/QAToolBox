#!/usr/bin/env python3
"""
音频转换器测试脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.views import convert_audio_file, decrypt_ncm_file

def test_audio_conversion():
    """测试音频转换功能"""
    print("🎵 音频转换器功能测试")
    print("=" * 50)
    
    # 测试目录
    test_dir = "test_audio"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 创建一个简单的测试音频文件（如果不存在）
    test_mp3 = os.path.join(test_dir, "test.mp3")
    if not os.path.exists(test_mp3):
        print("⚠️  请将测试音频文件放在 test_audio/test.mp3")
        print("   或者将NCM文件放在 test_audio/test.ncm")
        return
    
    # 测试MP3到WAV转换
    print("📁 测试MP3到WAV转换...")
    output_wav = os.path.join(test_dir, "converted_test.wav")
    
    success, message, output_path = convert_audio_file(test_mp3, output_wav, 'wav')
    
    if success:
        print(f"✅ 转换成功: {output_path}")
        print(f"📊 文件大小: {os.path.getsize(output_path)} bytes")
    else:
        print(f"❌ 转换失败: {message}")
    
    # 测试MP3到FLAC转换
    print("\n📁 测试MP3到FLAC转换...")
    output_flac = os.path.join(test_dir, "converted_test.flac")
    
    success, message, output_path = convert_audio_file(test_mp3, output_flac, 'flac')
    
    if success:
        print(f"✅ 转换成功: {output_path}")
        print(f"📊 文件大小: {os.path.getsize(output_path)} bytes")
    else:
        print(f"❌ 转换失败: {message}")
    
    print("\n🎉 测试完成！")

def test_ncm_decryption():
    """测试NCM文件解密功能"""
    print("\n🔐 NCM文件解密测试")
    print("=" * 50)
    
    test_dir = "test_audio"
    test_ncm = os.path.join(test_dir, "test.ncm")
    
    if not os.path.exists(test_ncm):
        print("⚠️  请将NCM测试文件放在 test_audio/test.ncm")
        return
    
    print("📁 测试NCM文件解密...")
    decrypted_path = decrypt_ncm_file(test_ncm)
    
    if decrypted_path and os.path.exists(decrypted_path):
        print(f"✅ 解密成功: {decrypted_path}")
        print(f"📊 文件大小: {os.path.getsize(decrypted_path)} bytes")
        
        # 测试解密后的文件转换
        print("\n📁 测试解密后的文件转换...")
        output_mp3 = os.path.join(test_dir, "decrypted_converted.mp3")
        
        success, message, output_path = convert_audio_file(decrypted_path, output_mp3, 'mp3')
        
        if success:
            print(f"✅ 转换成功: {output_path}")
            print(f"📊 文件大小: {os.path.getsize(output_path)} bytes")
        else:
            print(f"❌ 转换失败: {message}")
    else:
        print("❌ 解密失败")

if __name__ == "__main__":
    print("🚀 开始音频转换器测试...")
    
    # 测试基本转换功能
    test_audio_conversion()
    
    # 测试NCM解密功能
    test_ncm_decryption()
    
    print("\n✨ 所有测试完成！")
