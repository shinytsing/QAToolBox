#!/usr/bin/env python3
"""
测试MP3转换修复
"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.legacy_views import convert_audio_file

def test_mp3_fix():
    """测试MP3转换修复"""
    
    print("🎵 测试MP3转换修复")
    print("=" * 50)
    
    # 使用WAV文件作为输入源
    input_path = "src/static/audio/meditation/MISTERK_final_test.wav"
    output_path = "src/static/audio/meditation/MISTERK_fixed_test.mp3"
    
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return
    
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    
    # 测试转换
    success, message, final_path = convert_audio_file(input_path, output_path, 'mp3')
    
    if success and final_path and os.path.exists(final_path):
        file_size = os.path.getsize(final_path)
        print(f"✅ MP3转换成功!")
        print(f"📁 输出文件: {final_path}")
        print(f"📁 文件大小: {file_size:,} bytes")
        
        # 检查文件头
        with open(final_path, 'rb') as f:
            header = f.read(16)
            print(f"📊 文件头: {header.hex()}")
            
            if header.startswith(b'ID3'):
                print("⚠️ 仍然有ID3标签")
            elif header.startswith(b'\xff\xfb') or header.startswith(b'\xff\xfa'):
                print("✅ 无ID3标签，直接MP3帧头")
            else:
                print("❓ 未知文件头格式")
        
        # 使用ffprobe验证
        import subprocess
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', final_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ffprobe验证通过")
            
            # 解析JSON输出
            import json
            try:
                info = json.loads(result.stdout)
                format_info = info.get('format', {})
                start_time = format_info.get('start_time', '未知')
                duration = format_info.get('duration', '未知')
                size = format_info.get('size', '未知')
                print(f"📊 音频信息:")
                print(f"   - 开始时间: {start_time}")
                print(f"   - 时长: {duration}秒")
                print(f"   - 大小: {size}字节")
                
                if start_time == "0.000000":
                    print("✅ 无延迟，应该可以在浏览器中播放")
                else:
                    print("⚠️ 有延迟，可能影响浏览器播放")
                    
            except:
                print("⚠️ 无法解析音频信息")
        else:
            print("❌ ffprobe验证失败")
            print(f"错误信息: {result.stderr}")
    else:
        print(f"❌ MP3转换失败: {message}")

if __name__ == "__main__":
    test_mp3_fix()
