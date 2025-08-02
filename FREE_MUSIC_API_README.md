# 免费音乐API系统

## 概述

QAToolBox现在使用全新的免费音乐API系统，支持多种免费音乐源，为用户提供丰富的音乐体验。

## 功能特性

### 🎵 多模式音乐支持
- **工作模式 (work)**: 专注工作模式 - 轻音乐、环境音乐，帮助提高专注力
- **生活模式 (life)**: 生活模式 - 轻松愉快的音乐，适合日常放松
- **训练模式 (training)**: 训练模式 - 充满活力的音乐，适合运动健身
- **情感模式 (emo)**: 情感模式 - 情感丰富的音乐，适合情绪表达

### 🌐 多源音乐支持
系统支持多个免费音乐API源，按优先级顺序尝试：

1. **Jamendo API** - 免费音乐平台
2. **Free Music Archive** - 免费音乐档案
3. **ccMixter** - 创意共享音乐平台
4. **Incompetech** - Kevin MacLeod的免费音乐
5. **本地音乐文件** - 备用方案

### 🔄 智能降级机制
- 当在线API不可用时，自动切换到本地音乐文件
- 确保音乐播放功能始终可用
- 支持缓存机制，提高响应速度

## API接口

### 获取随机音乐
```
GET /tools/api/music/?mode={mode}&action=random
```

### 获取模式音乐列表
```
GET /tools/api/music/?mode={mode}&action=playlist
```

### 搜索音乐
```
GET /tools/api/music/?action=search&keyword={keyword}&mode={mode}
```

### 获取所有模式信息
```
GET /tools/api/music/?action=modes
```

### 下一首音乐
```
POST /tools/api/music/next/
Content-Type: application/json

{
    "mode": "work"
}
```

## 使用示例

### Python代码示例
```python
from apps.tools.utils.music_api import free_music_api

# 获取工作模式的随机音乐
song = free_music_api.get_random_song('work')
print(f"当前播放: {song['name']} - {song['artist']}")

# 获取所有可用模式
modes = free_music_api.get_available_modes()
print(f"可用模式: {modes}")

# 搜索音乐
results = free_music_api.search_song('piano', 'work')
for song in results:
    print(f"找到: {song['name']} - {song['artist']}")
```

### JavaScript代码示例
```javascript
// 获取随机音乐
fetch('/tools/api/music/?mode=work&action=random')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const song = data.data;
            console.log(`播放: ${song.name} - ${song.artist}`);
        }
    });

// 获取模式信息
fetch('/tools/api/music/?action=modes')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            data.data.forEach(mode => {
                console.log(`${mode.mode}: ${mode.description}`);
            });
        }
    });
```

## 配置说明

### Jamendo API配置
如需使用Jamendo API，请在 `music_api.py` 中配置：
```python
self.jamendo_client_id = "your_jamendo_client_id"  # 从 https://developer.jamendo.com/ 获取
```

### 本地音乐文件
本地音乐文件存储在 `src/static/audio/` 目录下：
- `friday.mp3` - 工作模式音乐
- `monday.mp3` - 工作模式音乐
- `saturday.mp3` - 生活模式音乐
- `sunday.mp3` - 生活模式音乐
- `tuesday.mp3` - 训练模式音乐
- `thursday.mp3` - 训练模式音乐
- `Eternxlkz - SLAY!.flac` - 情感模式音乐
- `keshi - 2 soon.flac` - 情感模式音乐

## 测试

运行测试脚本验证功能：
```bash
python test_music_api.py
```

## 故障排除

### 常见问题

1. **API请求失败**
   - 检查网络连接
   - 确认API密钥配置正确
   - 系统会自动降级到本地音乐

2. **音乐无法播放**
   - 检查音频文件是否存在
   - 确认浏览器支持音频格式
   - 检查音频文件路径

3. **搜索无结果**
   - 尝试不同的关键词
   - 检查搜索模式设置
   - 确认音乐源可用

### 日志查看
音乐API的详细日志会输出到控制台，包括：
- API请求状态
- 错误信息
- 降级操作记录

## 更新日志

### v2.0.0 (当前版本)
- ✅ 替换网易云音乐API为免费音乐API
- ✅ 支持多种免费音乐源
- ✅ 添加智能降级机制
- ✅ 优化缓存系统
- ✅ 增加模式信息API
- ✅ 改进搜索功能

### v1.0.0 (历史版本)
- 基于网易云音乐API
- 支持本地音乐备用

## 贡献

欢迎提交Issue和Pull Request来改进音乐系统！

## 许可证

本项目使用MIT许可证。音乐文件遵循各自平台的许可协议。 