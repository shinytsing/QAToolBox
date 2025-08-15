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
2. **Incompetech** - Kevin MacLeod的免费音乐
3. **本地音乐文件** - 备用方案

> **注意**: Free Music Archive和ccMixter API由于稳定性问题已被暂时禁用

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

## 配置说明

### 1. Jamendo API配置
- 访问 https://www.jamendo.com/ 注册免费账户
- 获取 `client_id`
- 在 `apps/tools/utils/music_api.py` 中配置

### 2. 本地音乐文件
备用本地音乐文件位于 `src/static/audio/`:
- `friday.mp3`, `monday.mp3` - 工作模式
- `saturday.mp3`, `sunday.mp3` - 生活模式  
- `tuesday.mp3`, `thursday.mp3` - 训练模式
- `Eternxlkz - SLAY!.flac`, `keshi - 2 soon.flac` - 情感模式

## 故障排除

### 常见问题
1. **API连接失败**: 系统会自动降级到本地音乐文件
2. **音乐无法播放**: 检查网络连接和API配置
3. **缓存问题**: 清除浏览器缓存或等待1小时缓存过期

### 禁用API说明
- **Free Music Archive**: 由于API服务不稳定，已暂时禁用
- **ccMixter**: 由于网络连接问题，已暂时禁用

## 技术特性

### 智能降级机制
```python
# 当在线API不可用时，自动切换到本地音乐
if not all_tracks:
    print(f"所有免费API都失败，使用本地音乐数据")
    all_tracks = self.local_music.get(mode, [])
```

### 缓存系统
```python
# 1小时缓存，提高响应速度
self.cache_expire = 3600
```

### 多源支持
```python
# 按优先级尝试不同API
self.free_apis = [
    self._try_jamendo_api,
    self._try_incompetech_api
]
```

## 更新日志

### v2.1.0 (最新)
- ✅ 禁用不稳定的Free Music Archive API
- ✅ 禁用不稳定的ccMixter API
- ✅ 优化错误处理机制
- ✅ 改进降级逻辑

### v2.0.0
- ✅ 重构为免费音乐API系统
- ✅ 支持多种音乐源
- ✅ 添加智能降级机制
- ✅ 完善缓存系统 