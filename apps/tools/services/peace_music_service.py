import logging
import os
import random
from typing import Dict, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class PeaceMusicService:
    """和平音乐服务 - 管理本地冥想音乐文件"""

    def __init__(self):
        self.peace_music_dir = os.path.join(settings.MEDIA_ROOT, "peace_music")

        # 音乐分类配置
        self.music_categories = {
            "nature": {
                "name": "自然音效",
                "icon": "fas fa-tree",
                "description": "大自然的声音，帮助放松身心",
                "keywords": ["rain", "thunder", "calming", "gentle", "golden"],
            },
            "ambient": {
                "name": "环境音效",
                "icon": "fas fa-cloud",
                "description": "舒缓的环境音效，营造冥想氛围",
                "keywords": ["ambient", "texture", "pad"],
            },
            "instrumental": {
                "name": "器乐音效",
                "icon": "fas fa-music",
                "description": "轻柔的器乐声，引导内心平静",
                "keywords": ["sitar", "flute", "epic", "instrumental", "reveal"],
            },
            "binaural": {
                "name": "双耳节拍",
                "icon": "fas fa-brain",
                "description": "双耳节拍音效，促进深度放松",
                "keywords": ["angelical", "pad", "binaural", "uplifting"],
            },
            "zen": {
                "name": "禅意音效",
                "icon": "fas fa-om",
                "description": "禅意音效，营造宁静氛围",
                "keywords": ["gentle", "rain", "relaxation", "sleep", "calming"],
            },
            "motivational": {
                "name": "激励音效",
                "icon": "fas fa-star",
                "description": "激励人心的音乐，提升正能量",
                "keywords": ["leap", "motiv", "uplifting"],
            },
            "atmospheric": {
                "name": "氛围音效",
                "icon": "fas fa-moon",
                "description": "营造宁静氛围的音效",
                "keywords": ["atmospheric", "texture", "pad"],
            },
        }

        # 扫描并分类音乐文件
        self.music_files = self._scan_music_files()

    def _scan_music_files(self) -> Dict[str, List[Dict]]:
        """扫描音乐文件并按分类组织"""
        categorized_music = {category: [] for category in self.music_categories.keys()}

        if not os.path.exists(self.peace_music_dir):
            logger.warning(f"和平音乐目录不存在: {self.peace_music_dir}")
            return categorized_music

        try:
            for filename in os.listdir(self.peace_music_dir):
                if filename.lower().endswith((".mp3", ".wav", ".flac", ".m4a")):
                    file_path = os.path.join(self.peace_music_dir, filename)
                    file_size = os.path.getsize(file_path)

                    # 根据文件名和关键词分类
                    category = self._categorize_music_file(filename)

                    music_info = {
                        "id": len(categorized_music[category]) + 1,
                        "name": self._extract_music_name(filename),
                        "filename": filename,
                        "file_path": file_path,
                        "url": f"/media/peace_music/{filename}",
                        "size": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "category": category,
                        "artist": "Peace Music Library",
                        "duration": "未知",  # 可以后续添加音频时长检测
                        "description": self.music_categories[category]["description"],
                    }

                    categorized_music[category].append(music_info)

        except Exception as e:
            logger.error(f"扫描音乐文件失败: {e}")

        return categorized_music

    def _categorize_music_file(self, filename: str) -> str:
        """根据文件名分类音乐"""
        filename_lower = filename.lower()

        # 重新分配音乐文件到各个冥想分类
        if "rain-and-thunder" in filename_lower:
            return "nature"  # 雷雨声 - 自然音效
        elif "one-week-at-golden" in filename_lower:
            return "nature"  # 环境音效 - 自然音效
        elif "uplifting-pad" in filename_lower:
            return "binaural"  # 提升氛围音效 - 双耳节拍
        elif "sitar" in filename_lower:
            return "instrumental"  # 西塔琴 - 器乐音效
        elif "leap-motiv" in filename_lower:
            return "ambient"  # 激励音效 - 环境音效
        elif "gentle-rain" in filename_lower:
            return "zen"  # 轻柔雨声 - 禅意音效
        elif "calming-rain" in filename_lower:
            return "zen"  # 平静雨声 - 禅意音效

        # 检查每个分类的关键词
        for category, config in self.music_categories.items():
            for keyword in config["keywords"]:
                if keyword.lower() in filename_lower:
                    return category

        # 默认分类
        return "ambient"

    def _extract_music_name(self, filename: str) -> str:
        """从文件名提取音乐名称"""
        # 移除文件扩展名
        name = os.path.splitext(filename)[0]

        # 替换下划线和连字符为空格
        name = name.replace("_", " ").replace("-", " ")

        # 首字母大写
        name = " ".join(word.capitalize() for word in name.split())

        return name

    def get_music_by_category(self, category: str) -> List[Dict]:
        """获取指定分类的音乐列表"""
        if category not in self.music_categories:
            logger.warning(f"未知的音乐分类: {category}")
            return []

        return self.music_files.get(category, [])

    def get_random_music_by_category(self, category: str) -> Optional[Dict]:
        """获取指定分类的随机音乐"""
        music_list = self.get_music_by_category(category)
        if music_list:
            return random.choice(music_list)
        return None

    def get_random_music(self) -> Optional[Dict]:
        """获取随机音乐"""
        all_music = []
        for category_music in self.music_files.values():
            all_music.extend(category_music)

        if all_music:
            return random.choice(all_music)
        return None

    def get_all_categories(self) -> Dict:
        """获取所有音乐分类信息"""
        categories_info = {}
        for category, config in self.music_categories.items():
            music_count = len(self.music_files.get(category, []))
            categories_info[category] = {
                "name": config["name"],
                "icon": config["icon"],
                "description": config["description"],
                "music_count": music_count,
            }
        return categories_info

    def search_music(self, keyword: str) -> List[Dict]:
        """搜索音乐"""
        keyword_lower = keyword.lower()
        results = []

        for category_music in self.music_files.values():
            for music in category_music:
                if keyword_lower in music["name"].lower() or keyword_lower in music["filename"].lower():
                    results.append(music)

        return results

    def get_music_by_id(self, music_id: int, category: str = None) -> Optional[Dict]:
        """根据ID获取音乐"""
        if category:
            music_list = self.get_music_by_category(category)
            for music in music_list:
                if music["id"] == music_id:
                    return music
        else:
            for category_music in self.music_files.values():
                for music in category_music:
                    if music["id"] == music_id:
                        return music

        return None

    def get_total_music_count(self) -> int:
        """获取总音乐数量"""
        total = 0
        for category_music in self.music_files.values():
            total += len(category_music)
        return total

    def refresh_music_library(self):
        """刷新音乐库"""
        self.music_files = self._scan_music_files()
        logger.info(f"音乐库已刷新，共找到 {self.get_total_music_count()} 首音乐")


# 全局实例
peace_music_service = PeaceMusicService()
