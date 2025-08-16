#!/usr/bin/env python3
"""
分析MP3帧结构的脚本
用于诊断为什么ffmpeg无法找到连续的MPEG音频帧
"""

import os
import struct

def analyze_mp3_frames(file_path):
    """分析MP3文件的帧结构"""
    print(f"🔍 分析MP3文件: {file_path}")
    print("=" * 80)
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    file_size = os.path.getsize(file_path)
    print(f"📁 文件大小: {file_size:,} bytes")
    
    with open(file_path, 'rb') as f:
        data = f.read()
    
    # 查找所有MP3帧头
    mp3_frames = []
    for i in range(len(data) - 4):
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            if i + 3 < len(data):
                frame_header = (data[i] << 24) | (data[i + 1] << 16) | (data[i + 2] << 8) | data[i + 3]
                
                # 解析MP3帧头
                mpeg_version = (frame_header >> 19) & 0x3
                layer = (frame_header >> 17) & 0x3
                bitrate_index = (frame_header >> 12) & 0xF
                sample_rate_index = (frame_header >> 10) & 0x3
                padding = (frame_header >> 9) & 0x1
                private = (frame_header >> 8) & 0x1
                channel_mode = (frame_header >> 6) & 0x3
                mode_extension = (frame_header >> 4) & 0x3
                copyright = (frame_header >> 3) & 0x1
                original = (frame_header >> 2) & 0x1
                emphasis = frame_header & 0x3
                
                # 验证帧头的合理性
                is_valid = True
                if mpeg_version == 1:  # 保留值
                    is_valid = False
                if layer == 0:  # 保留值
                    is_valid = False
                if bitrate_index == 0 or bitrate_index == 15:  # 无效值
                    is_valid = False
                if sample_rate_index == 3:  # 保留值
                    is_valid = False
                
                mp3_frames.append({
                    'position': i,
                    'header': frame_header,
                    'header_bytes': data[i:i+4],
                    'mpeg_version': mpeg_version,
                    'layer': layer,
                    'bitrate_index': bitrate_index,
                    'sample_rate_index': sample_rate_index,
                    'padding': padding,
                    'channel_mode': channel_mode,
                    'is_valid': is_valid
                })
    
    print(f"🔍 找到 {len(mp3_frames)} 个MP3帧头")
    
    if len(mp3_frames) == 0:
        print("❌ 没有找到任何MP3帧头")
        return
    
    # 分析前10个帧
    print("\n📊 前10个MP3帧分析:")
    print("-" * 80)
    for i, frame in enumerate(mp3_frames[:10]):
        print(f"帧 {i+1}:")
        print(f"  位置: {frame['position']}")
        print(f"  帧头: {frame['header_bytes'].hex()}")
        print(f"  MPEG版本: {frame['mpeg_version']}")
        print(f"  层: {frame['layer']}")
        print(f"  比特率索引: {frame['bitrate_index']}")
        print(f"  采样率索引: {frame['sample_rate_index']}")
        print(f"  填充: {frame['padding']}")
        print(f"  声道模式: {frame['channel_mode']}")
        print(f"  有效: {'✅' if frame['is_valid'] else '❌'}")
        print()
    
    # 检查帧的连续性
    print("🔍 检查帧的连续性:")
    print("-" * 80)
    
    valid_frames = [f for f in mp3_frames if f['is_valid']]
    print(f"有效帧数量: {len(valid_frames)}")
    
    if len(valid_frames) < 2:
        print("❌ 有效帧数量少于2个，无法形成连续的MPEG音频帧")
        return
    
    # 分析帧间距
    consecutive_pairs = []
    for i in range(len(valid_frames) - 1):
        frame1 = valid_frames[i]
        frame2 = valid_frames[i + 1]
        
        # 计算帧间距
        distance = frame2['position'] - frame1['position']
        
        # 估算帧大小（基于比特率和采样率）
        # 这里使用简化的计算
        estimated_frame_size = 144 * (320 if frame1['bitrate_index'] == 14 else 128) // 32
        
        consecutive_pairs.append({
            'frame1_pos': frame1['position'],
            'frame2_pos': frame2['position'],
            'distance': distance,
            'estimated_size': estimated_frame_size,
            'is_reasonable': abs(distance - estimated_frame_size) < 100
        })
    
    print(f"连续帧对数量: {len(consecutive_pairs)}")
    
    # 显示前5个连续帧对
    for i, pair in enumerate(consecutive_pairs[:5]):
        print(f"连续帧对 {i+1}:")
        print(f"  帧1位置: {pair['frame1_pos']}")
        print(f"  帧2位置: {pair['frame2_pos']}")
        print(f"  间距: {pair['distance']} bytes")
        print(f"  估算帧大小: {pair['estimated_size']} bytes")
        print(f"  间距合理: {'✅' if pair['is_reasonable'] else '❌'}")
        print()
    
    # 检查是否有合理的连续帧
    reasonable_pairs = [p for p in consecutive_pairs if p['is_reasonable']]
    print(f"合理的连续帧对数量: {len(reasonable_pairs)}")
    
    if len(reasonable_pairs) == 0:
        print("❌ 没有找到合理的连续MPEG音频帧")
        print("这可能是因为:")
        print("1. MP3帧头被错误识别")
        print("2. 帧大小计算错误")
        print("3. 音频数据损坏")
        print("4. 文件格式不是标准MP3")
    else:
        print("✅ 找到合理的连续MPEG音频帧")
    
    # 检查ID3标签
    print("\n🔍 检查ID3标签:")
    print("-" * 80)
    
    if data.startswith(b'ID3'):
        print("✅ 检测到ID3标签")
        if len(data) >= 10:
            # 读取ID3标签大小
            size = ((data[6] & 0x7f) << 21) | ((data[7] & 0x7f) << 14) | ((data[8] & 0x7f) << 7) | (data[9] & 0x7f)
            print(f"ID3标签大小: {size} bytes")
            print(f"音频数据开始位置: {10 + size}")
            
            # 检查音频数据开始位置是否有MP3帧头
            audio_start = 10 + size
            if audio_start < len(data) and data[audio_start] == 0xFF and (data[audio_start + 1] & 0xE0) == 0xE0:
                print("✅ 音频数据开始位置有有效的MP3帧头")
            else:
                print("❌ 音频数据开始位置没有有效的MP3帧头")
    else:
        print("❌ 没有检测到ID3标签")

def main():
    """主函数"""
    # 分析有问题的文件
    problem_file = "media/temp_audio/repaired_offset_c64ba207.mp3"
    
    if os.path.exists(problem_file):
        analyze_mp3_frames(problem_file)
    else:
        print(f"❌ 问题文件不存在: {problem_file}")
        
        # 查找其他MP3文件进行分析
        temp_dir = "media/temp_audio"
        mp3_files = []
        for file in os.listdir(temp_dir):
            if file.endswith('.mp3'):
                file_path = os.path.join(temp_dir, file)
                mp3_files.append((file_path, os.path.getmtime(file_path)))
        
        if mp3_files:
            # 使用最新的MP3文件
            mp3_files.sort(key=lambda x: x[1], reverse=True)
            latest_mp3 = mp3_files[0][0]
            print(f"📁 使用最新的MP3文件进行分析: {latest_mp3}")
            analyze_mp3_frames(latest_mp3)
        else:
            print("❌ 没有找到MP3文件进行分析")

if __name__ == "__main__":
    main()
