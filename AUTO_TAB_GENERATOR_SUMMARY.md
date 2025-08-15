# 自动扒谱系统 - 吉他训练系统扩展功能

## 功能概述

自动扒谱系统是吉他训练系统的重要扩展功能，允许用户上传音频文件，系统自动分析并生成吉他谱。该功能使用先进的音频处理技术，能够准确识别调性、速度、和弦进行、旋律和低音线。

## 核心功能

### 1. 🎵 音频上传与分析
- **支持格式**: MP3, WAV, M4A, FLAC
- **文件大小限制**: 最大50MB
- **拖拽上传**: 支持拖拽文件到上传区域
- **实时进度**: 显示上传和分析进度

### 2. 🎼 智能音频分析
- **速度检测**: 使用librosa库检测BPM
- **调性识别**: 自动识别歌曲的调性
- **拍号检测**: 分析节拍间隔确定拍号
- **和弦检测**: 使用色度图分析识别和弦进行
- **旋律提取**: 提取主旋律音符
- **低音线分析**: 分离并分析低音部分

### 3. 🎸 吉他谱生成
- **和弦谱**: 显示和弦进行和指法图
- **旋律谱**: 生成主旋律的指法谱
- **完整谱**: 包含和弦和旋律的完整谱
- **自动排版**: 生成格式化的吉他谱

### 4. 📊 扒谱历史与统计
- **历史记录**: 保存所有扒谱记录
- **统计分析**: 显示扒谱成功率和类型分布
- **下载功能**: 支持谱子下载和分享

## 技术实现

### 音频处理库
```python
# 主要依赖
import librosa  # 音频分析
import numpy as np  # 数值计算
import scipy.signal  # 信号处理
import wave  # WAV文件处理
```

### 核心分析函数

#### 1. 音频分析主函数
```python
def analyze_audio(file_path):
    """分析音频文件"""
    # 加载音频
    y, sr = librosa.load(file_path, sr=None)
    
    # 检测速度
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # 检测调性
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key_raw = librosa.feature.key_mode(chroma)[0]
    key = librosa.key_to_notes(key_raw)[0]
    
    # 检测和弦、旋律、低音线
    chords_detected = detect_chords(y, sr, tempo)
    melody_notes = detect_melody(y, sr)
    bass_line = detect_bass_line(y, sr)
    
    return analysis_result
```

#### 2. 和弦检测
```python
def detect_chords(y, sr, tempo):
    """检测和弦"""
    # 使用色度图检测和弦
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # 和弦模板匹配
    chord_templates = {
        'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # C-E-G
        'G': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],  # G-B-D
        'Am': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # A-C-E
        # ... 更多和弦模板
    }
    
    # 模板匹配算法
    return chords_detected
```

#### 3. 旋律检测
```python
def detect_melody(y, sr):
    """检测旋律"""
    # 提取音高
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
    
    # 找到最强音高
    for i in range(pitches.shape[1]):
        max_idx = np.argmax(magnitudes[:, i])
        pitch = pitches[max_idx, i]
        
        if pitch > 0:
            note = librosa.hz_to_note(pitch)
            melody_notes.append({
                'note': note,
                'time': i * 512 / sr,
                'duration': time_step
            })
    
    return melody_notes
```

#### 4. 低音线检测
```python
def detect_bass_line(y, sr):
    """检测低音线"""
    # 分离和声与打击乐
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    
    # 低通滤波
    b, a = signal.butter(4, 200/(sr/2), btype='low')
    y_bass = signal.filtfilt(b, a, y_harmonic)
    
    # 检测低音音符
    pitches, magnitudes = librosa.piptrack(y=y_bass, sr=sr)
    
    return bass_line
```

### 备用分析方案
当librosa库不可用时，系统会使用基础音频分析：
```python
def basic_audio_analysis(file_path):
    """基础音频分析"""
    # 使用wave库读取WAV文件
    # 使用FFT进行频率分析
    # 基于主要频率估算调性和速度
    # 生成相对和弦和音符
```

## 前端实现

### 主要页面组件
1. **上传区域**: 拖拽上传和文件选择
2. **分析进度**: 实时显示分析进度
3. **分析结果**: 显示检测到的音乐信息
4. **谱子类型选择**: 和弦谱、旋律谱、完整谱
5. **结果展示**: 格式化的吉他谱显示
6. **操作按钮**: 下载、保存、分享功能

### 交互功能
```javascript
// 文件上传处理
function uploadFile(file) {
    const formData = new FormData();
    formData.append('audio_file', file);
    
    fetch('/tools/api/guitar/upload-audio/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAnalysisResults(data.analysis_result);
            showTabGenerationOptions();
        }
    });
}

// 生成吉他谱
function generateTab() {
    const requestData = {
        task_id: currentTaskId,
        analysis_data: analysisData,
        tab_type: selectedTabType
    };
    
    fetch('/tools/api/guitar/generate-tab/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showTabResult(data.tab_result);
        }
    });
}
```

## API接口

### 1. 音频上传API
```
POST /tools/api/guitar/upload-audio/
Content-Type: multipart/form-data

参数:
- audio_file: 音频文件

返回:
{
    "success": true,
    "message": "音频文件上传成功，开始分析...",
    "task_id": "task_1234567890",
    "analysis_result": {...}
}
```

### 2. 生成吉他谱API
```
POST /tools/api/guitar/generate-tab/
Content-Type: application/json

参数:
{
    "task_id": "task_1234567890",
    "analysis_data": {...},
    "tab_type": "chords|melody|full"
}

返回:
{
    "success": true,
    "message": "吉他谱生成成功",
    "tab_result": {...}
}
```

### 3. 扒谱历史API
```
GET /tools/api/guitar/tab-history/

返回:
{
    "success": true,
    "tabs": [...]
}
```

### 4. 下载谱子API
```
GET /tools/api/guitar/download-tab/<tab_id>/

返回:
Content-Type: text/plain
Content-Disposition: attachment; filename="guitar_tab_xxx.txt"
```

## 生成的吉他谱格式

### 和弦谱示例
```
歌曲信息:
调性: C
速度: 120 BPM
拍号: 4/4

和弦进行:
C (4拍)
G (4拍)
Am (4拍)
F (4拍)

和弦指法图:
C和弦:
e|---0---|
B|---1---|
G|---0---|
D|---2---|
A|---3---|
E|-------|

G和弦:
e|---3---|
B|---3---|
G|---0---|
D|---0---|
A|---2---|
E|---3---|
```

### 旋律谱示例
```
旋律谱:
速度: 120 BPM

e|--8-8-8-8--|
B|--1-1-1-1--|
G|--0-0-0-0--|
D|--2-2-2-2--|
A|--3-3-3-3--|
E|------------|
```

### 完整谱示例
```
完整吉他谱:
[和弦谱内容]

[旋律谱内容]

演奏说明:
1. 先练习和弦进行
2. 再练习旋律部分
3. 最后和弦和旋律结合
```

## 技术特色

### 1. 智能音频分析
- **多维度分析**: 速度、调性、和弦、旋律、低音
- **模板匹配**: 使用和弦模板进行准确识别
- **频率分析**: 基于FFT的频谱分析
- **音高跟踪**: 实时音高检测和音符转换

### 2. 容错机制
- **备用方案**: 当librosa不可用时使用基础分析
- **错误处理**: 完善的异常处理机制
- **降级策略**: 分析失败时提供默认结果

### 3. 用户体验
- **拖拽上传**: 直观的文件上传方式
- **实时反馈**: 进度条和状态提示
- **多种格式**: 支持多种吉他谱格式
- **一键下载**: 快速保存和分享

### 4. 扩展性
- **模块化设计**: 各分析功能独立
- **插件架构**: 易于添加新的分析算法
- **配置灵活**: 可调整分析参数

## 部署要求

### 系统依赖
```bash
# Python包依赖
pip install librosa
pip install numpy
pip install scipy
pip install soundfile
```

### 环境要求
- Python 3.8+
- 足够的内存处理音频文件
- 支持音频处理的系统库

### 性能优化
- 音频文件大小限制
- 分析结果缓存
- 异步处理支持

## 使用场景

### 1. 学习辅助
- 快速获取歌曲的和弦进行
- 学习新歌的旋律部分
- 理解音乐结构

### 2. 创作参考
- 分析流行歌曲的和声进行
- 学习不同风格的音乐特点
- 获取创作灵感

### 3. 教学工具
- 教师快速生成教学材料
- 学生自主学习和练习
- 音乐理论实践

## 未来扩展

### 1. 高级功能
- **多轨分离**: 分离吉他、贝斯、鼓等不同乐器
- **风格识别**: 自动识别音乐风格
- **难度评估**: 评估歌曲的演奏难度
- **个性化推荐**: 基于用户水平推荐歌曲

### 2. 社交功能
- **谱子分享**: 用户间分享扒谱结果
- **协作编辑**: 多人协作完善谱子
- **评论系统**: 对谱子进行评价和建议

### 3. 移动端支持
- **移动应用**: 原生移动端应用
- **离线处理**: 本地音频分析
- **云端同步**: 多设备数据同步

## 总结

自动扒谱系统为吉他学习者提供了一个强大的工具，通过先进的音频处理技术，能够快速准确地分析音乐并生成吉他谱。系统设计注重用户体验和技术可靠性，提供了完整的扒谱解决方案。该功能不仅能够帮助学习者快速获取歌曲信息，也为音乐创作和教学提供了有力支持。
