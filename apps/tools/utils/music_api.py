import requests
import random
import time
from typing import List, Dict, Optional
from urllib.parse import quote
import json

class FreeMusicAPI:
    """免费音乐API服务"""
    
    def __init__(self):
        # 音乐标签映射
        self.music_tags = {
            'work': ['instrumental', 'ambient', 'electronic', 'focus'],
            'life': ['chill', 'acoustic', 'indie', 'folk'],
            'training': ['rock', 'electronic', 'dance', 'energy'],
            'emo': ['indie', 'alternative', 'sad', 'melancholy']
        }
        
        # 在线音乐数据（备用）
        self.online_music = {
            'work': [
                {
                    'id': 'online_work_1',
                    'name': 'Ambient Work Music',
                    'artist': 'Free Music Archive',
                    'album': 'Focus Collection',
                    'duration': 180000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'  # 示例URL
                },
                {
                    'id': 'online_work_2',
                    'name': 'Deep Focus',
                    'artist': 'Concentration',
                    'album': 'Productivity Mix',
                    'duration': 240000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'  # 示例URL
                }
            ],
            'life': [
                {
                    'id': 'online_life_1',
                    'name': 'Chill Vibes',
                    'artist': 'Indie Music',
                    'album': 'Life Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
                },
                {
                    'id': 'online_life_2',
                    'name': 'Acoustic Dreams',
                    'artist': 'Alternative Music',
                    'album': 'Life Collection',
                    'duration': 180000,
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
            ],
            'emo': [
                {
                    'id': 'online_emo_1',
                    'name': 'Melancholy Dreams',
                    'artist': 'Life Music',
                    'album': 'Emo Collection',
                    'duration': 220000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav'
                },
                {
                    'id': 'online_emo_2',
                    'name': 'Sad Vibes',
                    'artist': 'Life Music',
                    'album': 'Emo Collection',
                    'duration': 200000,
                    'pic_url': '',
                    'play_url': 'https://www.soundjay.com/misc/sounds/fail-buzzer-02.wav'
                }
            ]
        }
        
        # 缓存数据
        self.music_cache = {}
        self.cache_expire = 3600  # 1小时缓存
        
        # 免费音乐API列表（移除了不稳定的Free Music Archive和ccMixter API）
        self.free_apis = [
            self._try_jamendo_api,
            self._try_incompetech_api
        ]
    
    def _try_jamendo_api(self, mode: str) -> List[Dict]:
        """尝试使用Jamendo API获取音乐"""
        try:
            # 获取对应模式的标签
            tags = self.music_tags.get(mode, ['instrumental'])
            tag_str = ','.join(tags[:2])  # 最多使用2个标签
            
            # Jamendo的公开API端点
            url = "https://api.jamendo.com/v3/tracks/"
            params = {
                'client_id': 'your_client_id',  # 需要注册获取
                'format': 'json',
                'limit': 10,
                'tags': tag_str,
                'include': 'musicinfo'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('results', [])
                
                return [
                    {
                        'id': track.get('id', ''),
                        'name': track.get('name', ''),
                        'artist': track.get('artist_name', ''),
                        'album': track.get('album_name', ''),
                        'duration': track.get('duration', 0) * 1000,  # 转换为毫秒
                        'pic_url': track.get('image', ''),
                        'play_url': track.get('audio', '')
                    }
                    for track in tracks
                ]
        except Exception as e:
            print(f"Jamendo API异常: {e}")
        
        return []
    
    # def _try_freemusicarchive_api(self, mode: str) -> List[Dict]:
    #     """尝试使用Free Music Archive API获取音乐（已禁用，API不稳定）"""
    #     # Free Music Archive API已不可用，暂时禁用
    #     return []
    
    # def _try_ccmixter_api(self, mode: str) -> List[Dict]:
    #     """尝试使用ccMixter API获取音乐（已禁用，API不稳定）"""
    #     # ccMixter API已不可用，暂时禁用
    #     return []
    
    def _try_incompetech_api(self, mode: str) -> List[Dict]:
        """尝试使用Incompetech API获取音乐"""
        try:
            # Incompetech的公开音乐数据
            url = "https://incompetech.com/music/royalty-free/music.json"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('music', [])
                
                return [
                    {
                        'id': track.get('id', ''),
                        'name': track.get('title', ''),
                        'artist': 'Kevin MacLeod',
                        'album': 'Incompetech',
                        'duration': track.get('duration', 0) * 1000,
                        'pic_url': '',
                        'play_url': track.get('url', '')
                    }
                    for track in tracks[:10]  # 限制数量
                ]
        except Exception as e:
            print(f"Incompetech API异常: {e}")
        
        return []
    
    def get_music_by_mode(self, mode: str) -> List[Dict]:
        """根据模式获取音乐列表"""
        cache_key = f"music_mode_{mode}"
        
        # 检查缓存
        if cache_key in self.music_cache:
            cache_data = self.music_cache[cache_key]
            if time.time() - cache_data['timestamp'] < self.cache_expire:
                return cache_data['data']
        
        # 尝试从在线API获取
        all_tracks = []
        for api_func in self.free_apis:
            try:
                tracks = api_func(mode)
                if tracks:
                    all_tracks.extend(tracks)
                    break  # 如果获取到数据就停止尝试其他API
            except Exception as e:
                print(f"API {api_func.__name__} 失败: {e}")
                continue
        
        # 如果在线API都失败，使用备用数据
        if not all_tracks:
            all_tracks = self.online_music.get(mode, [])
        
        # 缓存结果
        self.music_cache[cache_key] = {
            'data': all_tracks,
            'timestamp': time.time()
        }
        
        return all_tracks
    
    def get_random_song(self, mode: str) -> Optional[Dict]:
        """获取随机歌曲"""
        tracks = self.get_music_by_mode(mode)
        if tracks:
            return random.choice(tracks)
        return None
    
    def search_song(self, keyword: str, mode: str = None, limit: int = 10) -> List[Dict]:
        """搜索歌曲"""
        if not keyword:
            return []
        
        # 这里可以实现搜索逻辑
        # 目前返回空列表，等待配置在线音乐API
        return []
    
    def get_song_url(self, song_id: str) -> Optional[str]:
        """获取歌曲播放URL"""
        # 这里可以实现获取播放URL的逻辑
        # 目前返回None，等待配置在线音乐API
        return None
    
    def format_duration(self, duration_ms: int) -> str:
        """格式化时长"""
        if not duration_ms:
            return "00:00"
        
        seconds = duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_available_modes(self) -> List[str]:
        """获取可用的音乐模式"""
        return list(self.music_tags.keys())
    
    def get_mode_info(self, mode: str) -> Dict:
        """获取模式信息"""
        return {
            'name': mode,
            'description': self._get_mode_description(mode),
            'tags': self.music_tags.get(mode, [])
        }
    
    def _get_mode_description(self, mode: str) -> str:
        """获取模式描述"""
        descriptions = {
            'work': '专注工作，提高效率',
            'life': '轻松生活，享受时光',
            'training': '激情训练，释放能量',
            'emo': '情感共鸣，心灵治愈'
        }
        return descriptions.get(mode, '未知模式')

# 创建全局实例
free_music_api = FreeMusicAPI() 