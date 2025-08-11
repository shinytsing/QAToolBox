import requests
import json
import random
from typing import Dict, List, Optional
import logging
from .peace_music_service import peace_music_service

logger = logging.getLogger(__name__)

class MeditationAudioService:
    """冥想音效服务 - 使用PeaceMusicService获取本地冥想音乐"""
    
    def __init__(self):
        self.pixabay_api_key = "36817612-8c0c4c8c8c8c8c8c8c8c8c8c"  # 请替换为实际的API密钥
        self.pixabay_base_url = "https://pixabay.com/api/"
        
        # 冥想音效分类
        self.meditation_sounds = {
            "nature": {
                "name": "自然音效",
                "keywords": ["冥想", "自然", "森林", "流水", "鸟鸣"],
                "description": "大自然的声音，帮助放松身心"
            },
            "ambient": {
                "name": "环境音效", 
                "keywords": ["冥想", "环境", "白噪音", "雨声", "风声"],
                "description": "舒缓的环境音效，营造冥想氛围"
            },
            "instrumental": {
                "name": "器乐音效",
                "keywords": ["冥想", "器乐", "钢琴", "古筝", "笛子"],
                "description": "轻柔的器乐声，引导内心平静"
            },
            "binaural": {
                "name": "双耳节拍",
                "keywords": ["冥想", "双耳节拍", "脑波", "放松"],
                "description": "双耳节拍音效，促进深度放松"
            },
            "zen": {
                "name": "禅意音效",
                "keywords": ["冥想", "禅意", "寺庙", "钟声", "诵经"],
                "description": "禅意音效，营造宁静氛围"
            }
        }

    def get_meditation_sound(self, category: str) -> Optional[Dict]:
        """
        获取指定类别的冥想音效 - 使用PeaceMusicService
        
        Args:
            category: 音效类别 (nature, ambient, instrumental, binaural, zen)
            
        Returns:
            音效信息字典或None
        """
        if category not in self.meditation_sounds:
            logger.warning(f"未知的冥想音效类别: {category}")
            return None
        
        # 使用PeaceMusicService获取对应分类的随机音乐
        music = peace_music_service.get_random_music_by_category(category)
        if music:
            logger.info(f"使用PeaceMusicService获取冥想音效: {category} - {music['name']}")
            return {
                "name": music["name"],
                "artist": music["artist"],
                "play_url": music["url"],
                "duration": 300,  # 默认5分钟
                "source": "peace_music",
                "category": category,
                "description": self.meditation_sounds[category]["description"]
            }
        
        # 如果PeaceMusicService没有找到音乐，尝试从Pixabay获取
        logger.warning(f"PeaceMusicService未找到{category}分类的音乐，尝试从Pixabay获取")
        return self._get_from_pixabay(category)

    def _get_from_pixabay(self, category: str) -> Optional[Dict]:
        """从Pixabay API获取音效"""
        try:
            sound_config = self.meditation_sounds[category]
            keywords = sound_config["keywords"]
            
            # 随机选择一个关键词
            keyword = random.choice(keywords)
            
            params = {
                "key": self.pixabay_api_key,
                "q": keyword,
                "audio_type": "music",  # 只搜索音乐类型
                "category": "music",
                "safesearch": "true",
                "per_page": 20,
                "lang": "zh"
            }
            
            response = requests.get(self.pixabay_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("hits"):
                # 随机选择一个音效
                hit = random.choice(data["hits"])
                
                return {
                    "name": hit.get("title", f"{sound_config['name']}音效"),
                    "artist": hit.get("user", "Pixabay"),
                    "play_url": hit.get("previewURL", ""),
                    "duration": hit.get("duration", 300),
                    "source": "pixabay",
                    "category": category,
                    "description": sound_config["description"]
                }
                
        except Exception as e:
            logger.error(f"Pixabay API调用失败: {e}")
            
        return None

    def get_all_categories(self) -> Dict:
        """获取所有冥想音效类别"""
        return {
            category: {
                "name": config["name"],
                "description": config["description"],
                "keywords": config["keywords"]
            }
            for category, config in self.meditation_sounds.items()
        }

    def search_meditation_sounds(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        搜索冥想音效
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            音效列表
        """
        try:
            params = {
                "key": self.pixabay_api_key,
                "q": f"冥想 {keyword}",
                "audio_type": "music",
                "category": "music", 
                "safesearch": "true",
                "per_page": limit,
                "lang": "zh"
            }
            
            response = requests.get(self.pixabay_base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if data.get("hits"):
                for hit in data["hits"][:limit]:
                    results.append({
                        "name": hit.get("title", "冥想音效"),
                        "artist": hit.get("user", "Pixabay"),
                        "play_url": hit.get("previewURL", ""),
                        "duration": hit.get("duration", 300),
                        "source": "pixabay",
                        "description": "冥想专用音效"
                    })
                    
            return results
            
        except Exception as e:
            logger.error(f"搜索冥想音效失败: {e}")
            return []

    def get_random_meditation_sound(self) -> Optional[Dict]:
        """获取随机冥想音效"""
        categories = list(self.meditation_sounds.keys())
        category = random.choice(categories)
        return self.get_meditation_sound(category)

# 全局实例
meditation_audio_service = MeditationAudioService()
