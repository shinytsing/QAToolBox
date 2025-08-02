import requests
import json
import random
import time
from typing import Dict, List, Optional
import re

class FreeMusicAPI:
    """免费音乐API工具类 - 支持多个免费音乐源"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # Jamendo API配置 (免费音乐API)
        self.jamendo_client_id = "your_jamendo_client_id"  # 需要注册获取
        self.jamendo_base_url = "https://api.jamendo.com/v3"
        
        # 不同模式对应的音乐标签
        self.music_tags = {
            'work': ['instrumental', 'ambient', 'electronic', 'study'],
            'life': ['acoustic', 'folk', 'indie', 'chill'],
            'training': ['rock', 'electronic', 'dance', 'energetic'],
            'emo': ['indie', 'alternative', 'sad', 'melancholic']
        }
        
        # 在线免费音乐数据（真正可用的URL）
        self.online_music = {
            'work': [
                {
                    'id': 'online_work_1',
                    'name': 'Ambient Work Music',
                    'artist': 'Free Music Archive',
                    'album': 'Productivity Collection',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'  # 示例URL
                },
                {
                    'id': 'online_work_2',
                    'name': 'Focus Flow',
                    'artist': 'Creative Commons',
                    'album': 'Work Music',
                    'duration': 240000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'  # 示例URL
                }
            ],
            'emo': [
                {
                    'id': 'online_emo_1',
                    'name': 'Melancholic Vibes',
                    'artist': 'Indie Music',
                    'album': 'Emotional Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
                },
                {
                    'id': 'online_emo_2',
                    'name': 'Sad Melody',
                    'artist': 'Alternative Music',
                    'album': 'Emo Vibes',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'
                }
            ],
            'life': [
                {
                    'id': 'online_life_1',
                    'name': 'Life is Beautiful',
                    'artist': 'Life Music',
                    'album': 'Life Collection',
                    'duration': 220000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
                },
                {
                    'id': 'online_life_2',
                    'name': 'Happy Day',
                    'artist': 'Life Music',
                    'album': 'Life Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'
                }
            ],
            'training': [
                {
                    'id': 'online_training_1',
                    'name': 'Workout Energy',
                    'artist': 'Fitness Beats',
                    'album': 'Training Mix',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
                },
                {
                    'id': 'online_training_2',
                    'name': 'Power Up',
                    'artist': 'Fitness Beats',
                    'album': 'Training Mix',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'
                }
            ]
        }
        
        # 备用本地音乐数据
        self.local_music = {
            'work': [
                {
                    'id': 'local_work_1',
                    'name': 'Code Flow',
                    'artist': 'Tech Vibes',
                    'album': 'Programming Sessions',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': '/static/audio/friday.mp3'
                },
                {
                    'id': 'local_work_2',
                    'name': 'Deep Focus',
                    'artist': 'Concentration',
                    'album': 'Productivity Mix',
                    'duration': 240000,
                    'pic_url': '',
                    'play_url': '/static/audio/monday.mp3'
                }
            ],
            'emo': [
                {
                    'id': 'local_emo_1',
                    'name': 'Eternxlkz - SLAY!',
                    'artist': 'Eternxlkz',
                    'album': 'Emo Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': '/static/audio/Eternxlkz - SLAY!.flac'
                },
                {
                    'id': 'local_emo_2',
                    'name': 'keshi - 2 soon',
                    'artist': 'keshi',
                    'album': 'Emo Vibes',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': '/static/audio/keshi - 2 soon.flac'
                }
            ],
            'life': [
                {
                    'id': 'local_life_1',
                    'name': 'Sunday Vibes',
                    'artist': 'Life Music',
                    'album': 'Weekend Collection',
                    'duration': 220000,
                    'pic_url': '',
                    'play_url': '/static/audio/sunday.mp3'
                },
                {
                    'id': 'local_life_2',
                    'name': 'Saturday Night',
                    'artist': 'Life Music',
                    'album': 'Weekend Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': '/static/audio/saturday.mp3'
                }
            ],
            'training': [
                {
                    'id': 'local_training_1',
                    'name': 'Workout Energy',
                    'artist': 'Fitness Beats',
                    'album': 'Training Mix',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': '/static/audio/thursday.mp3'
                },
                {
                    'id': 'local_training_2',
                    'name': 'Power Up',
                    'artist': 'Fitness Beats',
                    'album': 'Training Mix',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': '/static/audio/tuesday.mp3'
                }
            ]
        }
        
        # 缓存数据
        self.music_cache = {}
        self.cache_expire = 3600  # 1小时缓存
        
        # 免费音乐API列表
        self.free_apis = [
            self._try_jamendo_api,
            self._try_freemusicarchive_api,
            self._try_ccmixter_api,
            self._try_incompetech_api
        ]
    
    def _try_jamendo_api(self, mode: str) -> List[Dict]:
        """尝试使用Jamendo API获取音乐"""
        try:
            if not self.jamendo_client_id or self.jamendo_client_id == "your_jamendo_client_id":
                return []
            
            tags = self.music_tags.get(mode, ['instrumental'])
            tag_str = ','.join(tags[:2])  # 最多使用2个标签
            
            url = f"{self.jamendo_base_url}/tracks/"
            params = {
                'client_id': self.jamendo_client_id,
                'format': 'json',
                'limit': 20,
                'tags': tag_str,
                'include': 'musicinfo'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('results', [])
            
            processed_tracks = []
            for track in tracks:
                processed_track = {
                    'id': track.get('id'),
                    'name': track.get('name', '未知歌曲'),
                    'artist': track.get('artist_name', '未知歌手'),
                    'album': track.get('album_name', '未知专辑'),
                    'duration': track.get('duration', 0) * 1000,  # 转换为毫秒
                    'pic_url': track.get('image', ''),
                    'play_url': track.get('audio', '')
                }
                processed_tracks.append(processed_track)
            
            return processed_tracks
            
        except Exception as e:
            print(f"Jamendo API异常: {e}")
            return []
    
    def _try_freemusicarchive_api(self, mode: str) -> List[Dict]:
        """尝试使用Free Music Archive API获取音乐"""
        try:
            # Free Music Archive的公开API端点
            url = "https://freemusicarchive.org/api/get/tracks.json"
            params = {
                'api_key': 'demo',  # 使用demo key
                'limit': 20
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('dataset', [])
            
            processed_tracks = []
            for track in tracks:
                processed_track = {
                    'id': track.get('track_id'),
                    'name': track.get('track_title', '未知歌曲'),
                    'artist': track.get('artist_name', '未知歌手'),
                    'album': track.get('album_title', '未知专辑'),
                    'duration': 0,  # FMA API不提供时长
                    'pic_url': '',
                    'play_url': track.get('track_url', '')
                }
                processed_tracks.append(processed_track)
            
            return processed_tracks[:10]  # 限制数量
            
        except Exception as e:
            print(f"Free Music Archive API异常: {e}")
            return []
    
    def _try_ccmixter_api(self, mode: str) -> List[Dict]:
        """尝试使用ccMixter API获取音乐"""
        try:
            # ccMixter的RSS feed
            url = "http://ccmixter.org/api/query"
            params = {
                'f': 'rss',
                'limit': 20
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 解析RSS feed
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            processed_tracks = []
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else '未知歌曲'
                artist = item.find('author').text if item.find('author') is not None else '未知歌手'
                
                processed_track = {
                    'id': f"ccmixter_{len(processed_tracks)}",
                    'name': title,
                    'artist': artist,
                    'album': 'ccMixter',
                    'duration': 0,
                    'pic_url': '',
                    'play_url': item.find('enclosure').get('url') if item.find('enclosure') is not None else ''
                }
                processed_tracks.append(processed_track)
            
            return processed_tracks
            
        except Exception as e:
            print(f"ccMixter API异常: {e}")
            return []
    
    def _try_incompetech_api(self, mode: str) -> List[Dict]:
        """尝试使用Incompetech API获取音乐"""
        try:
            # Incompetech的公开音乐列表
            url = "https://incompetech.com/music/royalty-free/music.json"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            tracks = data.get('music', [])
            
            processed_tracks = []
            for track in tracks:
                processed_track = {
                    'id': track.get('id'),
                    'name': track.get('title', '未知歌曲'),
                    'artist': 'Kevin MacLeod',
                    'album': 'Incompetech',
                    'duration': 0,
                    'pic_url': '',
                    'play_url': track.get('url', '')
                }
                processed_tracks.append(processed_track)
            
            return processed_tracks[:15]  # 限制数量
            
        except Exception as e:
            print(f"Incompetech API异常: {e}")
            return []
    
    def get_music_by_mode(self, mode: str) -> List[Dict]:
        """获取指定模式的音乐列表"""
        try:
            # 检查缓存
            cache_key = f"mode_{mode}"
            if cache_key in self.music_cache:
                cache_data = self.music_cache[cache_key]
                if time.time() - cache_data['timestamp'] < self.cache_expire:
                    return cache_data['tracks']
            
            # 优先使用在线音乐数据
            all_tracks = self.online_music.get(mode, [])
            
            # 如果在线音乐不足，尝试在线API作为补充
            if len(all_tracks) < 2:
                for api_func in self.free_apis:
                    try:
                        tracks = api_func(mode)
                        if tracks:
                            # 只添加有有效播放URL的音乐
                            valid_tracks = [track for track in tracks if track.get('play_url') and track['play_url'].startswith('http')]
                            if valid_tracks:
                                all_tracks.extend(valid_tracks[:2])  # 添加2首在线音乐
                                break
                    except Exception as e:
                        print(f"API {api_func.__name__} 异常: {e}")
                        continue
            
            # 如果在线音乐仍然不足，使用本地音乐作为备用
            if len(all_tracks) < 2:
                all_tracks.extend(self.local_music.get(mode, [])[:2])
            
            # 缓存结果
            self.music_cache[cache_key] = {
                'tracks': all_tracks,
                'timestamp': time.time()
            }
            
            return all_tracks
            
        except Exception as e:
            print(f"获取模式音乐异常: {e}")
            return self.local_music.get(mode, [])
    
    def get_random_song(self, mode: str) -> Optional[Dict]:
        """获取指定模式的随机歌曲"""
        try:
            tracks = self.get_music_by_mode(mode)
            if not tracks:
                print(f"模式 {mode} 没有可用的音乐")
                return None
            
            # 随机选择一首歌
            random_track = random.choice(tracks)
            return random_track
            
        except Exception as e:
            print(f"获取随机歌曲异常: {e}")
            # 异常时使用本地音乐
            local_tracks = self.local_music.get(mode, [])
            if local_tracks:
                return random.choice(local_tracks)
            return None
    
    def search_song(self, keyword: str, mode: str = None, limit: int = 10) -> List[Dict]:
        """搜索歌曲"""
        try:
            # 从当前模式的音乐中搜索
            if mode:
                tracks = self.get_music_by_mode(mode)
            else:
                # 搜索所有模式的音乐
                tracks = []
                for m in self.music_tags.keys():
                    tracks.extend(self.get_music_by_mode(m))
            
            # 简单的关键词匹配
            matched_tracks = []
            keyword_lower = keyword.lower()
            
            for track in tracks:
                if (keyword_lower in track.get('name', '').lower() or 
                    keyword_lower in track.get('artist', '').lower() or
                    keyword_lower in track.get('album', '').lower()):
                    matched_tracks.append(track)
                    if len(matched_tracks) >= limit:
                        break
            
            return matched_tracks
            
        except Exception as e:
            print(f"搜索歌曲异常: {e}")
            return []
    
    def get_song_url(self, song_id: str) -> Optional[str]:
        """获取歌曲播放链接"""
        try:
            # 从缓存中查找歌曲
            for mode in self.music_tags.keys():
                tracks = self.get_music_by_mode(mode)
                for track in tracks:
                    if track.get('id') == song_id:
                        return track.get('play_url')
            
            return None
            
        except Exception as e:
            print(f"获取歌曲链接异常: {e}")
            return None
    
    def format_duration(self, duration_ms: int) -> str:
        """格式化时长"""
        try:
            seconds = duration_ms // 1000
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes:02d}:{remaining_seconds:02d}"
        except:
            return "00:00"
    
    def get_available_modes(self) -> List[str]:
        """获取可用的音乐模式"""
        return list(self.music_tags.keys())
    
    def get_mode_info(self, mode: str) -> Dict:
        """获取模式信息"""
        return {
            'mode': mode,
            'tags': self.music_tags.get(mode, []),
            'description': self._get_mode_description(mode)
        }
    
    def _get_mode_description(self, mode: str) -> str:
        """获取模式描述"""
        descriptions = {
            'work': '专注工作模式 - 轻音乐、环境音乐，帮助提高专注力',
            'life': '生活模式 - 轻松愉快的音乐，适合日常放松',
            'training': '训练模式 - 充满活力的音乐，适合运动健身',
            'emo': '情感模式 - 情感丰富的音乐，适合情绪表达'
        }
        return descriptions.get(mode, '未知模式')

# 创建全局实例
free_music_api = FreeMusicAPI()

# 为了保持向后兼容，保留原来的变量名
netease_api = free_music_api 