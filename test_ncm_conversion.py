#!/usr/bin/env python3
"""
测试新的NCM转换功能
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import decrypt_ncm_file_correct, convert_audio_file

def test_ncm_conversion():
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    if not os.path.exists(ncm_file):
        print(f"❌ NCM文件不存在: {ncm_file}")
        return
    
    print(f"🔍 测试NCM文件转换: {ncm_file}")
    
    # 测试解密函数
    try:
        print("🔓 测试NCM解密...")
        decrypted_audio = decrypt_ncm_file_correct(ncm_file)
        print(f"✅ NCM解密成功，数据大小: {len(decrypted_audio):,} bytes")
        
        # 保存解密后的文件
        decrypted_path = "src/static/audio/meditation/MISTERK_new_decrypted.mp3"
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_audio)
        print(f"💾 解密文件已保存到: {decrypted_path}")
        
        # 检查文件头部
        with open(decrypted_path, 'rb') as f:
            header = f.read(32)
        print(f"📊 文件头32字节: {header.hex()}")
        
        # 测试转换函数
        print("\n🔄 测试音频转换...")
        output_path = "src/static/audio/meditation/MISTERK_new_converted.mp3"
        success, message, final_path = convert_audio_file(decrypted_path, output_path, 'mp3')
        
        if success:
            print(f"✅ 音频转换成功: {final_path}")
            
            # 测试ffprobe
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', '-show_streams', final_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ ffprobe可以读取转换后的文件")
            else:
                print("❌ ffprobe无法读取转换后的文件")
        else:
            print(f"❌ 音频转换失败: {message}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_ncm_conversion()
