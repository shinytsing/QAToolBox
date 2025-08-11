"""
版本时间跟踪工具
用于记录和管理ModeShift项目的实际开发时间
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class VersionTracker:
    """版本时间跟踪器"""
    
    def __init__(self, data_file: str = "version_history.json"):
        self.data_file = data_file
        self.versions = self._load_versions()
    
    def _load_versions(self) -> Dict:
        """加载版本历史数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载版本历史失败: {e}")
                return self._get_default_versions()
        else:
            return self._get_default_versions()
    
    def _save_versions(self):
        """保存版本历史数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存版本历史失败: {e}")
    
    def _get_default_versions(self) -> Dict:
        """获取默认版本历史"""
        return {
            "project_start": "2023-11-20",
            "current_version": "1.0.0",
            "versions": [
                {
                    "version": "1.0.0",
                    "date": "2024-01-20",
                    "title": "正式版本发布",
                    "features": ["吉他训练", "美食随机", "Emo轮换", "PDF优化"],
                    "description": "正式版本发布，新增吉他训练系统、美食随机器等核心功能"
                },
                {
                    "version": "0.9.0",
                    "date": "2024-01-15",
                    "title": "社交功能完善",
                    "features": ["塔罗牌", "心动链接", "社交订阅", "求职机"],
                    "description": "完善社交功能，新增塔罗牌占卜、心动链接、Boss直聘求职机等"
                },
                {
                    "version": "0.8.0",
                    "date": "2024-01-10",
                    "title": "AI功能增强",
                    "features": ["旅游攻略", "抖音分析", "爬虫系统", "AI增强"],
                    "description": "增强AI功能，新增旅游攻略生成、抖音数据分析等智能功能"
                },
                {
                    "version": "0.7.0",
                    "date": "2024-01-05",
                    "title": "核心功能完善",
                    "features": ["生活日记", "音乐播放", "PDF转换", "目标管理"],
                    "description": "完善核心功能模块，包括日记系统、音乐播放器、PDF转换等"
                },
                {
                    "version": "0.6.0",
                    "date": "2023-12-25",
                    "title": "四大模式完成",
                    "features": ["极客模式", "狂暴模式", "Emo模式", "生活模式"],
                    "description": "完成四大主题模式的开发，包含各种专业工具和功能"
                },
                {
                    "version": "0.5.0",
                    "date": "2023-12-20",
                    "title": "主题系统实现",
                    "features": ["多主题系统", "UI重新设计", "响应式优化"],
                    "description": "实现多主题系统，重新设计用户界面，优化响应式设计"
                },
                {
                    "version": "0.3.0",
                    "date": "2023-12-10",
                    "title": "基础工具完善",
                    "features": ["基础工具", "API接口", "数据库优化"],
                    "description": "完善基础工具功能，实现API接口系统，优化数据库设计"
                },
                {
                    "version": "0.1.0",
                    "date": "2023-11-20",
                    "title": "项目启动",
                    "features": ["基础架构", "用户认证", "后台管理"],
                    "description": "ModeShift项目正式启动，建立基础架构和用户认证系统"
                }
            ]
        }
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        return self.versions.get("current_version", "1.0.0")
    
    def get_project_start_date(self) -> str:
        """获取项目启动日期"""
        return self.versions.get("project_start", "2023-11-20")
    
    def get_all_versions(self) -> List[Dict]:
        """获取所有版本信息"""
        return self.versions.get("versions", [])
    
    def get_version_by_number(self, version: str) -> Optional[Dict]:
        """根据版本号获取版本信息"""
        for v in self.versions.get("versions", []):
            if v["version"] == version:
                return v
        return None
    
    def add_version(self, version: str, title: str, features: List[str], description: str, date: str = None):
        """添加新版本"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        new_version = {
            "version": version,
            "date": date,
            "title": title,
            "features": features,
            "description": description
        }
        
        self.versions["versions"].append(new_version)
        self.versions["current_version"] = version
        self._save_versions()
    
    def update_version(self, version: str, **kwargs):
        """更新版本信息"""
        for v in self.versions.get("versions", []):
            if v["version"] == version:
                v.update(kwargs)
                self._save_versions()
                return True
        return False
    
    def get_development_duration(self) -> str:
        """计算开发周期"""
        start_date = datetime.strptime(self.get_project_start_date(), "%Y-%m-%d")
        end_date = datetime.now()
        duration = end_date - start_date
        
        months = duration.days // 30
        if months > 0:
            return f"{months}个月"
        else:
            days = duration.days
            return f"{days}天"
    
    def get_total_features(self) -> int:
        """计算总功能数"""
        total = 0
        for version in self.versions.get("versions", []):
            total += len(version.get("features", []))
        return total
    
    def get_version_count(self) -> int:
        """获取版本总数"""
        return len(self.versions.get("versions", []))
    
    def format_date_for_display(self, date_str: str) -> str:
        """格式化日期显示"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%Y年%m月%d日")
        except:
            return date_str


# 全局版本跟踪器实例
version_tracker = VersionTracker()


def get_version_context():
    """获取版本上下文数据，用于模板渲染"""
    versions = version_tracker.get_all_versions()
    
    # 为每个版本添加格式化日期
    for version in versions:
        version['date_formatted'] = version_tracker.format_date_for_display(version['date'])
    
    return {
        "current_version": version_tracker.get_current_version(),
        "project_start": version_tracker.get_project_start_date(),
        "development_duration": version_tracker.get_development_duration(),
        "total_features": version_tracker.get_total_features(),
        "version_count": version_tracker.get_version_count(),
        "versions": versions
    }


# 使用示例
if __name__ == "__main__":
    # 创建版本跟踪器
    tracker = VersionTracker()
    
    # 获取当前版本信息
    print(f"当前版本: {tracker.get_current_version()}")
    print(f"项目启动: {tracker.get_project_start_date()}")
    print(f"开发周期: {tracker.get_development_duration()}")
    print(f"版本总数: {tracker.get_version_count()}")
    print(f"功能总数: {tracker.get_total_features()}")
    
    # 获取所有版本
    versions = tracker.get_all_versions()
    for version in versions:
        print(f"v{version['version']} ({version['date']}): {version['title']}")
