#!/usr/bin/env python3
"""
最终NCM转换测试
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import decrypt_ncm_file_correct, convert_audio_file

def test_ncm_conversion_final():
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    if not os.path.exists(ncm_file):
        print(f"❌ NCM文件不存在: {ncm_file}")
        return
    
    print(f"🎵 最终NCM转换测试")
    print("=" * 50)
    
    # 测试1: 解密NCM文件
    print("🔓 步骤1: 解密NCM文件...")
    try:
        decrypted_audio = decrypt_ncm_file_correct(ncm_file)
        print(f"✅ NCM解密成功，数据大小: {len(decrypted_audio):,} bytes")
        
        # 保存解密后的文件
        decrypted_path = "src/static/audio/meditation/MISTERK_final_test.mp3"
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_audio)
        print(f"💾 解密文件已保存到: {decrypted_path}")
        
        # 检查文件头部
        with open(decrypted_path, 'rb') as f:
            header = f.read(32)
        print(f"📊 文件头32字节: {header.hex()}")
        
        if header.startswith(b'ID3'):
            print("✅ 检测到正确的MP3格式（ID3标签）")
        elif header[0] == 0xFF and (header[1] & 0xE0) == 0xE0:
            print("✅ 检测到正确的MP3格式（帧头）")
        else:
            print("⚠️ 文件头不是标准MP3格式")
        
        # 测试2: 使用ffmpeg验证
        print("\n🔧 步骤2: 使用ffmpeg验证...")
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', decrypted_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ffprobe验证通过")
            
            # 解析JSON输出
            import json
            try:
                info = json.loads(result.stdout)
                format_info = info.get('format', {})
                duration = format_info.get('duration', '未知')
                size = format_info.get('size', '未知')
                print(f"📊 音频信息: 时长={duration}秒, 大小={size}字节")
            except:
                print("⚠️ 无法解析音频信息")
        else:
            print("❌ ffprobe验证失败")
            print(f"错误信息: {result.stderr}")
        
        # 测试3: 转换为其他格式
        print("\n🔄 步骤3: 转换为其他格式...")
        formats_to_test = ['wav', 'flac', 'm4a']
        
        for fmt in formats_to_test:
            output_path = f"src/static/audio/meditation/MISTERK_final_test.{fmt}"
            print(f"\n转换为 {fmt.upper()} 格式...")
            
            success, message, final_path = convert_audio_file(decrypted_path, output_path, fmt)
            
            if success and final_path and os.path.exists(final_path):
                file_size = os.path.getsize(final_path)
                print(f"✅ {fmt.upper()}转换成功!")
                print(f"📁 输出文件: {final_path}")
                print(f"📁 文件大小: {file_size:,} bytes")
                
                # 验证转换后的文件
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', '-show_streams', final_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ {fmt.upper()}文件验证通过")
                else:
                    print(f"❌ {fmt.upper()}文件验证失败")
            else:
                print(f"❌ {fmt.upper()}转换失败: {message}")
        
        print("\n" + "=" * 50)
        print("🎉 NCM转换测试完成!")
        print("\n📋 生成的文件:")
        print("- MISTERK_final_test.mp3 (解密后的MP3)")
        print("- MISTERK_final_test.wav (WAV格式)")
        print("- MISTERK_final_test.flac (FLAC格式)")
        print("- MISTERK_final_test.m4a (M4A格式)")
        print("\n🌐 测试地址:")
        print("http://localhost:8000/tools/audio_converter/")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ncm_conversion_final()
