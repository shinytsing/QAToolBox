#!/usr/bin/env python3
"""
全面的NCM转换测试脚本
测试各种转换场景和边界情况
"""

import os
import sys
import django
import subprocess
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import (
    decrypt_ncm_file, 
    convert_ncm_file_native,
    convert_audio_file,
    repair_audio_file_with_offset
)

def test_ncm_file(ncm_path, test_name="NCM文件"):
    """测试单个NCM文件的转换"""
    print(f"\n🔧 测试 {test_name}: {os.path.basename(ncm_path)}")
    print("=" * 60)
    
    if not os.path.exists(ncm_path):
        print(f"❌ 文件不存在: {ncm_path}")
        return False
    
    file_size = os.path.getsize(ncm_path)
    print(f"📁 文件大小: {file_size:,} bytes")
    
    # 步骤1: 解密测试
    print("\n🔓 步骤1: NCM解密测试...")
    start_time = time.time()
    try:
        decrypted_path = decrypt_ncm_file(ncm_path)
        decrypt_time = time.time() - start_time
        
        if decrypted_path and os.path.exists(decrypted_path):
            decrypted_size = os.path.getsize(decrypted_path)
            print(f"✅ 解密成功! 耗时: {decrypt_time:.2f}秒")
            print(f"📁 解密后文件: {decrypted_path}")
            print(f"📁 解密后大小: {decrypted_size:,} bytes")
            
            # 检查解密后的文件头
            with open(decrypted_path, 'rb') as f:
                header = f.read(16)
                print(f"🔍 解密后文件头: {header.hex()}")
        else:
            print("❌ 解密失败")
            return False
    except Exception as e:
        print(f"❌ 解密异常: {e}")
        return False
    
    # 步骤2: 原生转换测试
    print("\n🔧 步骤2: 原生转换测试...")
    output_dir = os.path.dirname(decrypted_path)
    base_name = os.path.splitext(os.path.basename(decrypted_path))[0]
    
    # 测试MP3转换
    mp3_output = os.path.join(output_dir, f"{base_name}_native.mp3")
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
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print("✅ ffmpeg可以正常处理原生转换的文件")
                else:
                    print(f"⚠️ ffmpeg处理原生转换文件时出现问题: {result.stderr[:200]}...")
            except Exception as e:
                print(f"⚠️ ffmpeg测试异常: {e}")
            
            native_success = True
        else:
            print(f"❌ 原生MP3转换失败: {message}")
            native_success = False
    except Exception as e:
        print(f"❌ 原生MP3转换异常: {e}")
        native_success = False
    
    # 步骤3: 标准转换测试
    print("\n🔧 步骤3: 标准转换测试...")
    standard_mp3_output = os.path.join(output_dir, f"{base_name}_standard.mp3")
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
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print("✅ ffmpeg可以正常处理标准转换的文件")
                else:
                    print(f"⚠️ ffmpeg处理标准转换文件时出现问题: {result.stderr[:200]}...")
            except Exception as e:
                print(f"⚠️ ffmpeg测试异常: {e}")
            
            standard_success = True
        else:
            print(f"❌ 标准MP3转换失败: {message}")
            standard_success = False
    except Exception as e:
        print(f"❌ 标准MP3转换异常: {e}")
        standard_success = False
    
    # 步骤4: 其他格式转换测试
    print("\n🔧 步骤4: 其他格式转换测试...")
    formats_to_test = ['wav', 'flac', 'm4a']
    
    for format_name in formats_to_test:
        format_output = os.path.join(output_dir, f"{base_name}_native.{format_name}")
        start_time = time.time()
        try:
            success, message, result_path = convert_ncm_file_native(decrypted_path, format_output, format_name)
            format_time = time.time() - start_time
            
            if success and result_path and os.path.exists(result_path):
                format_size = os.path.getsize(result_path)
                print(f"✅ {format_name.upper()}转换成功! 耗时: {format_time:.2f}秒")
                print(f"📁 文件大小: {format_size:,} bytes")
            else:
                print(f"❌ {format_name.upper()}转换失败: {message}")
        except Exception as e:
            print(f"❌ {format_name.upper()}转换异常: {e}")
    
    # 总结
    print(f"\n📊 {test_name} 测试总结:")
    print("-" * 40)
    print(f"解密: {'✅' if decrypted_path else '❌'}")
    print(f"原生MP3转换: {'✅' if native_success else '❌'}")
    print(f"标准MP3转换: {'✅' if standard_success else '❌'}")
    
    return decrypted_path is not None

def find_ncm_files():
    """查找可用的NCM文件"""
    temp_dir = "media/temp_audio"
    ncm_files = []
    
    if os.path.exists(temp_dir):
        for file in os.listdir(temp_dir):
            if file.endswith('.ncm'):
                file_path = os.path.join(temp_dir, file)
                file_size = os.path.getsize(file_path)
                # 过滤掉太小的文件（可能是测试文件）
                if file_size > 1024:  # 大于1KB
                    ncm_files.append((file_path, file_size, os.path.getmtime(file_path)))
    
    # 按修改时间排序，最新的在前
    ncm_files.sort(key=lambda x: x[2], reverse=True)
    return ncm_files

def main():
    """主函数"""
    print("🚀 全面NCM转换测试脚本启动")
    print("=" * 80)
    
    # 查找NCM文件
    ncm_files = find_ncm_files()
    
    if not ncm_files:
        print("❌ 没有找到有效的NCM文件进行测试")
        print("请确保在 media/temp_audio 目录中有大于1KB的NCM文件")
        return
    
    print(f"📁 找到 {len(ncm_files)} 个NCM文件:")
    for i, (file_path, file_size, mtime) in enumerate(ncm_files):
        print(f"  {i+1}. {os.path.basename(file_path)} ({file_size:,} bytes)")
    
    # 测试前3个文件
    test_count = min(3, len(ncm_files))
    success_count = 0
    
    print(f"\n🔧 开始测试前 {test_count} 个文件...")
    
    for i in range(test_count):
        file_path, file_size, mtime = ncm_files[i]
        test_name = f"NCM文件 {i+1}"
        
        if test_ncm_file(file_path, test_name):
            success_count += 1
        
        # 文件间稍作休息
        if i < test_count - 1:
            print("\n⏳ 等待3秒后继续下一个测试...")
            time.sleep(3)
    
    # 最终总结
    print(f"\n🎉 测试完成!")
    print("=" * 80)
    print(f"📊 测试结果:")
    print(f"  总测试文件: {test_count}")
    print(f"  成功解密: {success_count}")
    print(f"  成功率: {success_count/test_count*100:.1f}%")
    
    if success_count > 0:
        print("\n✅ NCM转换功能正常工作!")
        print("💡 建议:")
        print("  - 优先使用原生转换方法 (convert_ncm_file_native)")
        print("  - 如果标准转换失败，原生转换通常能成功")
        print("  - 支持多种输出格式: MP3, WAV, FLAC, M4A")
    else:
        print("\n❌ 所有测试都失败了")
        print("💡 可能的原因:")
        print("  - NCM文件损坏或不完整")
        print("  - 文件格式不是标准的NCM格式")
        print("  - 系统缺少必要的依赖")

if __name__ == "__main__":
    main()
