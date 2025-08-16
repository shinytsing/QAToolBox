#!/usr/bin/env python3
"""
简单的NCM转换测试 - 先解密再转换
"""

import os
import subprocess
import sys

# 添加Django路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from apps.tools.legacy_views import decrypt_ncm_file

def main():
    print("🚀 开始NCM转换测试")
    
    # 检查文件是否存在
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    if not os.path.exists(ncm_file):
        print(f"❌ 文件不存在: {ncm_file}")
        return
    
    print(f"✅ 找到NCM文件: {ncm_file}")
    print(f"📁 文件大小: {os.path.getsize(ncm_file):,} bytes")
    
    # 步骤1: 解密NCM文件
    print("\n🔓 步骤1: 解密NCM文件...")
    try:
        decrypted_path = decrypt_ncm_file(ncm_file)
        if not decrypted_path or not os.path.exists(decrypted_path):
            print("❌ NCM解密失败")
            return
        
        print(f"✅ 解密成功: {decrypted_path}")
        print(f"📁 解密文件大小: {os.path.getsize(decrypted_path):,} bytes")
        
    except Exception as e:
        print(f"❌ 解密异常: {e}")
        return
    
    # 步骤2: 使用ffmpeg转换
    print("\n🔄 步骤2: 使用ffmpeg转换...")
    output_dir = "src/static/audio/meditation"
    
    formats = {
        'mp3': {'ext': '.mp3', 'codec': 'libmp3lame', 'options': ['-q:a', '2']},
        'wav': {'ext': '.wav', 'codec': 'pcm_s16le', 'options': ['-ar', '44100', '-ac', '2']},
        'flac': {'ext': '.flac', 'codec': 'flac', 'options': ['-compression_level', '8']},
        'm4a': {'ext': '.m4a', 'codec': 'aac', 'options': ['-b:a', '192k']}
    }
    
    results = {}
    
    for format_name, config in formats.items():
        print(f"\n🎵 转换 {format_name.upper()} 格式...")
        
        output_path = os.path.join(output_dir, f"MISTERK_fixed{config['ext']}")
        
        try:
            cmd = [
                'ffmpeg', '-i', decrypted_path,
                '-acodec', config['codec']
            ] + config['options'] + [
                '-y',
                output_path
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ {format_name.upper()} 转换成功")
                print(f"📁 文件大小: {file_size:,} bytes")
                results[format_name] = output_path
            else:
                print(f"❌ {format_name.upper()} 转换失败")
                print(f"错误信息: {result.stderr}")
                results[format_name] = None
                
        except Exception as e:
            print(f"❌ {format_name.upper()} 转换异常: {e}")
            results[format_name] = None
    
    # 步骤3: 验证结果
    print("\n🔍 步骤3: 验证转换结果...")
    for format_name, output_path in results.items():
        if output_path and os.path.exists(output_path):
            try:
                probe_cmd = [
                    'ffprobe', '-v', 'quiet', '-print_format', 'json',
                    '-show_format', '-show_streams', output_path
                ]
                
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
                
                if probe_result.returncode == 0:
                    print(f"✅ {format_name.upper()}: 文件格式正确")
                else:
                    print(f"❌ {format_name.upper()}: 文件格式有问题")
                    
            except Exception as e:
                print(f"❌ {format_name.upper()}: 验证异常 - {e}")
    
    # 步骤4: 清理临时文件
    print("\n🧹 步骤4: 清理临时文件...")
    try:
        if os.path.exists(decrypted_path):
            os.remove(decrypted_path)
            print("✅ 清理临时解密文件")
    except Exception as e:
        print(f"⚠️ 清理异常: {e}")
    
    # 总结
    print("\n📊 转换总结:")
    print("=" * 50)
    success_count = sum(1 for path in results.values() if path and os.path.exists(path))
    print(f"成功转换: {success_count}/{len(formats)} 个格式")
    
    for format_name, output_path in results.items():
        status = "✅ 成功" if output_path and os.path.exists(output_path) else "❌ 失败"
        print(f"{format_name.upper()}: {status}")
        if output_path and os.path.exists(output_path):
            print(f"  路径: {output_path}")
    
    if success_count > 0:
        print(f"\n🎉 转换完成！")
        print(f"🌐 访问测试页面: http://localhost:8000/tools/audio_playback_test/")

if __name__ == "__main__":
    main()
