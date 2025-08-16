#!/usr/bin/env python3
"""
专门调试指定NCM文件的脚本
处理 MISTERK,Tphunk,89DX - Sakana~_副本.ncm 文件
"""

import os
import sys
import django
import subprocess
import time
import shutil

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import (
    decrypt_ncm_file, 
    convert_ncm_file_native,
    convert_audio_file,
    repair_audio_file_with_offset
)

def debug_specific_ncm():
    """调试指定的NCM文件"""
    # 指定文件路径
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    print("🔧 开始调试指定的NCM文件")
    print("=" * 80)
    print(f"📁 目标文件: {ncm_file}")
    
    if not os.path.exists(ncm_file):
        print(f"❌ 文件不存在: {ncm_file}")
        return False
    
    file_size = os.path.getsize(ncm_file)
    print(f"📁 文件大小: {file_size:,} bytes")
    
    # 创建临时目录
    temp_dir = "media/temp_audio"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 复制文件到临时目录
    temp_ncm = os.path.join(temp_dir, "debug_target.ncm")
    shutil.copy2(ncm_file, temp_ncm)
    print(f"📁 已复制到临时目录: {temp_ncm}")
    
    # 步骤1: 解密测试
    print("\n🔓 步骤1: NCM解密测试...")
    start_time = time.time()
    try:
        decrypted_path = decrypt_ncm_file(temp_ncm)
        decrypt_time = time.time() - start_time
        
        if decrypted_path and os.path.exists(decrypted_path):
            decrypted_size = os.path.getsize(decrypted_path)
            print(f"✅ 解密成功! 耗时: {decrypt_time:.2f}秒")
            print(f"📁 解密后文件: {decrypted_path}")
            print(f"📁 解密后大小: {decrypted_size:,} bytes")
            
            # 检查解密后的文件头
            with open(decrypted_path, 'rb') as f:
                header = f.read(32)
                print(f"🔍 解密后文件头: {header.hex()}")
                
                # 检查文件格式
                if header.startswith(b'ID3'):
                    print("✅ 检测到ID3标签")
                elif header.startswith(b'\xff\xe0') or header.startswith(b'\xff\xe1') or header.startswith(b'\xff\xe2') or header.startswith(b'\xff\xe3'):
                    print("✅ 检测到MP3帧头")
                elif header.startswith(b'RIFF'):
                    print("✅ 检测到WAV文件头")
                elif header.startswith(b'fLaC'):
                    print("✅ 检测到FLAC文件头")
                elif header.startswith(b'ftyp'):
                    print("✅ 检测到M4A文件头")
                else:
                    print("❌ 无法识别的文件格式")
        else:
            print("❌ 解密失败")
            return False
    except Exception as e:
        print(f"❌ 解密异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 步骤2: 原生转换测试
    print("\n🔧 步骤2: 原生转换测试...")
    output_dir = os.path.dirname(decrypted_path)
    base_name = os.path.splitext(os.path.basename(decrypted_path))[0]
    
    # 测试MP3转换
    mp3_output = os.path.join(output_dir, f"{base_name}_debug.mp3")
    start_time = time.time()
    try:
        success, message, result_path = convert_ncm_file_native(decrypted_path, mp3_output, 'mp3')
        native_time = time.time() - start_time
        
        if success and result_path and os.path.exists(result_path):
            mp3_size = os.path.getsize(result_path)
            print(f"✅ 原生MP3转换成功! 耗时: {native_time:.2f}秒")
            print(f"📁 输出文件: {result_path}")
            print(f"📁 文件大小: {mp3_size:,} bytes")
            
            # 验证输出文件
            with open(result_path, 'rb') as f:
                output_header = f.read(16)
                print(f"🔍 输出文件头: {output_header.hex()}")
            
            # 测试ffmpeg兼容性
            print("\n🔍 测试ffmpeg兼容性...")
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', result_path, '-f', 'null', '-'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✅ ffmpeg可以正常处理原生转换的文件")
                else:
                    print(f"⚠️ ffmpeg处理原生转换文件时出现问题:")
                    print(f"错误信息: {result.stderr}")
            except Exception as e:
                print(f"⚠️ ffmpeg测试异常: {e}")
            
            # 复制到静态目录用于播放测试
            static_audio_dir = "src/static/audio/meditation"
            os.makedirs(static_audio_dir, exist_ok=True)
            playable_mp3 = os.path.join(static_audio_dir, "MISTERK_Tphunk_89DX_Sakana_debug.mp3")
            shutil.copy2(result_path, playable_mp3)
            print(f"📁 已复制到播放目录: {playable_mp3}")
            
            native_success = True
        else:
            print(f"❌ 原生MP3转换失败: {message}")
            native_success = False
    except Exception as e:
        print(f"❌ 原生MP3转换异常: {e}")
        import traceback
        traceback.print_exc()
        native_success = False
    
    # 步骤3: 标准转换测试
    print("\n🔧 步骤3: 标准转换测试...")
    standard_mp3_output = os.path.join(output_dir, f"{base_name}_standard_debug.mp3")
    start_time = time.time()
    try:
        success, message, result_path = convert_audio_file(decrypted_path, standard_mp3_output, 'mp3')
        standard_time = time.time() - start_time
        
        if success and result_path and os.path.exists(result_path):
            standard_size = os.path.getsize(result_path)
            print(f"✅ 标准MP3转换成功! 耗时: {standard_time:.2f}秒")
            print(f"📁 输出文件: {result_path}")
            print(f"📁 文件大小: {standard_size:,} bytes")
            
            # 验证输出文件
            with open(result_path, 'rb') as f:
                output_header = f.read(16)
                print(f"🔍 输出文件头: {output_header.hex()}")
            
            # 测试ffmpeg兼容性
            print("\n🔍 测试ffmpeg兼容性...")
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', result_path, '-f', 'null', '-'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("✅ ffmpeg可以正常处理标准转换的文件")
                else:
                    print(f"⚠️ ffmpeg处理标准转换文件时出现问题:")
                    print(f"错误信息: {result.stderr}")
            except Exception as e:
                print(f"⚠️ ffmpeg测试异常: {e}")
            
            standard_success = True
        else:
            print(f"❌ 标准MP3转换失败: {message}")
            standard_success = False
    except Exception as e:
        print(f"❌ 标准MP3转换异常: {e}")
        import traceback
        traceback.print_exc()
        standard_success = False
    
    # 步骤4: 其他格式转换测试
    print("\n🔧 步骤4: 其他格式转换测试...")
    formats_to_test = ['wav', 'flac', 'm4a']
    
    for format_name in formats_to_test:
        format_output = os.path.join(output_dir, f"{base_name}_debug.{format_name}")
        start_time = time.time()
        try:
            success, message, result_path = convert_ncm_file_native(decrypted_path, format_output, format_name)
            format_time = time.time() - start_time
            
            if success and result_path and os.path.exists(result_path):
                format_size = os.path.getsize(result_path)
                print(f"✅ {format_name.upper()}转换成功! 耗时: {format_time:.2f}秒")
                print(f"📁 文件大小: {format_size:,} bytes")
                
                # 复制到静态目录
                playable_format = os.path.join(static_audio_dir, f"MISTERK_Tphunk_89DX_Sakana_debug.{format_name}")
                shutil.copy2(result_path, playable_format)
                print(f"📁 已复制到播放目录: {playable_format}")
            else:
                print(f"❌ {format_name.upper()}转换失败: {message}")
        except Exception as e:
            print(f"❌ {format_name.upper()}转换异常: {e}")
    
    # 总结
    print(f"\n📊 调试总结:")
    print("=" * 50)
    print(f"解密: {'✅' if decrypted_path else '❌'}")
    print(f"原生MP3转换: {'✅' if native_success else '❌'}")
    print(f"标准MP3转换: {'✅' if standard_success else '❌'}")
    
    if native_success or standard_success:
        print(f"\n🎉 转换成功! 可以播放的文件:")
        print(f"📁 原生MP3: src/static/audio/meditation/MISTERK_Tphunk_89DX_Sakana_debug.mp3")
        print(f"📁 其他格式: src/static/audio/meditation/MISTERK_Tphunk_89DX_Sakana_debug.*")
        print(f"\n💡 建议:")
        print(f"  - 使用原生转换的MP3文件进行播放测试")
        print(f"  - 如果MP3播放有问题，尝试WAV或FLAC格式")
        print(f"  - 检查浏览器是否支持相应的音频格式")
    
    return decrypted_path is not None

def main():
    """主函数"""
    print("🚀 指定NCM文件调试脚本启动")
    print("=" * 80)
    
    success = debug_specific_ncm()
    
    if success:
        print("\n🎉 调试完成，请检查转换后的文件!")
        sys.exit(0)
    else:
        print("\n❌ 调试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
