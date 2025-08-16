#!/usr/bin/env python3
"""
增强的NCM音频转换测试脚本
用于测试修复后的NCM解密和转换功能
"""

import os
import sys
import django
import logging

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import (
    decrypt_ncm_file, 
    convert_audio_file, 
    convert_ncm_file_native,
    repair_audio_file_with_offset
)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ncm_conversion_enhanced(ncm_file_path):
    """增强的NCM文件转换测试"""
    print(f"🎵 开始增强NCM文件转换测试: {ncm_file_path}")
    print("=" * 80)
    
    if not os.path.exists(ncm_file_path):
        print(f"❌ 错误: 文件 {ncm_file_path} 不存在")
        return False
    
    # 生成输出文件路径
    base_name = os.path.splitext(os.path.basename(ncm_file_path))[0]
    output_dir = os.path.dirname(ncm_file_path)
    
    test_results = {}
    
    # 测试1: 直接解密
    print("🔓 测试1: NCM文件解密...")
    try:
        decrypted_path = decrypt_ncm_file(ncm_file_path)
        if decrypted_path and os.path.exists(decrypted_path):
            file_size = os.path.getsize(decrypted_path)
            print(f"✅ 解密成功! 输出文件: {decrypted_path}")
            print(f"📁 文件大小: {file_size} bytes")
            test_results['decryption'] = True
            
            # 检查文件头
            with open(decrypted_path, 'rb') as f:
                header = f.read(32)
                print(f"🔍 文件头32字节: {header.hex()}")
                
                # 分析文件头
                if header.startswith(b'ID3'):
                    print("✅ 检测到ID3标签")
                elif header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xfa':
                    print("✅ 检测到MP3帧头")
                elif header.startswith(b'RIFF'):
                    print("✅ 检测到WAV文件")
                elif header.startswith(b'fLaC'):
                    print("✅ 检测到FLAC文件")
                elif b'ftyp' in header[4:8]:
                    print("✅ 检测到M4A/MP4文件")
                else:
                    print("⚠️ 文件头不匹配已知音频格式，尝试深度扫描...")
                    
                    # 深度扫描查找音频格式
                    f.seek(0)
                    full_data = f.read(min(file_size, 8192))
                    
                    # 查找MP3帧头
                    mp3_found = False
                    for i in range(len(full_data) - 4):
                        if full_data[i] == 0xFF and (full_data[i + 1] & 0xE0) == 0xE0:
                            if i + 3 < len(full_data):
                                frame_header = (full_data[i] << 24) | (full_data[i + 1] << 16) | (full_data[i + 2] << 8) | full_data[i + 3]
                                mpeg_version = (frame_header >> 19) & 0x3
                                layer = (frame_header >> 17) & 0x3
                                if mpeg_version != 1 and layer != 1:
                                    continue
                                
                                print(f"✅ 深度扫描找到MP3帧头位置: {i}")
                                print(f"MP3帧头: {full_data[i:i+4].hex()}")
                                mp3_found = True
                                
                                # 测试修复功能
                                print(f"🔧 测试修复功能，偏移量: {i}")
                                repaired_path = repair_audio_file_with_offset(decrypted_path, i)
                                if repaired_path:
                                    print(f"✅ 修复成功: {repaired_path}")
                                    test_results['repair'] = True
                                    
                                    # 验证修复后的文件
                                    with open(repaired_path, 'rb') as check_file:
                                        repaired_header = check_file.read(16)
                                        print(f"修复后文件头: {repaired_header.hex()}")
                                else:
                                    print("❌ 修复失败")
                                    test_results['repair'] = False
                                break
                    
                    if not mp3_found:
                        print("❌ 深度扫描未找到有效MP3帧头")
                        test_results['deep_scan'] = False
                    else:
                        test_results['deep_scan'] = True
        else:
            print("❌ 解密失败")
            test_results['decryption'] = False
            return False
    except Exception as e:
        print(f"❌ 解密异常: {e}")
        import traceback
        traceback.print_exc()
        test_results['decryption'] = False
        return False
    
    # 测试2: 原生转换方法
    print("\n🔧 测试2: 原生转换方法...")
    formats_to_test = ['mp3', 'wav']
    
    for fmt in formats_to_test:
        output_path = os.path.join(output_dir, f"{base_name}_native_enhanced.{fmt}")
        print(f"\n转换为 {fmt.upper()} 格式...")
        
        try:
            success, message, result_path = convert_ncm_file_native(decrypted_path, output_path, fmt)
            if success and result_path and os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"✅ 原生{fmt.upper()}转换成功!")
                print(f"📁 输出文件: {result_path}")
                print(f"📁 文件大小: {file_size} bytes")
                test_results[f'native_{fmt}'] = True
                
                # 验证输出文件
                with open(result_path, 'rb') as f:
                    output_header = f.read(16)
                    print(f"输出文件头: {output_header.hex()}")
            else:
                print(f"❌ 原生{fmt.upper()}转换失败: {message}")
                test_results[f'native_{fmt}'] = False
        except Exception as e:
            print(f"❌ 原生{fmt.upper()}转换异常: {e}")
            test_results[f'native_{fmt}'] = False
    
    # 测试3: 标准转换方法
    print("\n🎵 测试3: 标准转换方法...")
    
    for fmt in formats_to_test:
        output_path = os.path.join(output_dir, f"{base_name}_standard_enhanced.{fmt}")
        print(f"\n转换为 {fmt.upper()} 格式...")
        
        try:
            success, message, result_path = convert_audio_file(ncm_file_path, output_path, fmt)
            if success and result_path and os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"✅ 标准{fmt.upper()}转换成功!")
                print(f"📁 输出文件: {result_path}")
                print(f"📁 文件大小: {file_size} bytes")
                test_results[f'standard_{fmt}'] = True
                
                # 验证输出文件
                with open(result_path, 'rb') as f:
                    output_header = f.read(16)
                    print(f"输出文件头: {output_header.hex()}")
            else:
                print(f"❌ 标准{fmt.upper()}转换失败: {message}")
                test_results[f'standard_{fmt}'] = False
        except Exception as e:
            print(f"❌ 标准{fmt.upper()}转换异常: {e}")
            test_results[f'standard_{fmt}'] = False
    
    # 输出测试总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结:")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了！NCM转换功能工作正常。")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步调试。")
        return False

def find_latest_ncm_file():
    """查找最新的NCM文件"""
    temp_dir = "media/temp_audio"
    if not os.path.exists(temp_dir):
        print(f"❌ 临时目录不存在: {temp_dir}")
        return None
    
    ncm_files = []
    for file in os.listdir(temp_dir):
        if file.endswith('.ncm'):
            file_path = os.path.join(temp_dir, file)
            ncm_files.append((file_path, os.path.getmtime(file_path)))
    
    if not ncm_files:
        print("❌ 没有找到NCM文件")
        return None
    
    # 使用最新的NCM文件
    ncm_files.sort(key=lambda x: x[1], reverse=True)
    latest_ncm = ncm_files[0][0]
    
    print(f"📁 使用最新的NCM文件: {latest_ncm}")
    return latest_ncm

if __name__ == "__main__":
    print("🚀 增强NCM转换测试脚本启动")
    print("=" * 80)
    
    # 查找NCM文件
    ncm_file = find_latest_ncm_file()
    if not ncm_file:
        print("❌ 无法找到NCM文件进行测试")
        sys.exit(1)
    
    # 运行测试
    success = test_ncm_conversion_enhanced(ncm_file)
    
    if success:
        print("\n🎉 测试完成，NCM转换功能正常！")
        sys.exit(0)
    else:
        print("\n❌ 测试完成，发现问题需要修复。")
        sys.exit(1)
