from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class GuitarPracticeSession(models.Model):
    """吉他练习会话模型"""

    PRACTICE_TYPE_CHOICES = [
        ("chords", "和弦练习"),
        ("scales", "音阶练习"),
        ("songs", "歌曲练习"),
        ("theory", "乐理学习"),
        ("ear_training", "听力训练"),
        ("fingerpicking", "指弹练习"),
        ("strumming", "扫弦练习"),
        ("other", "其他"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "初级"),
        ("intermediate", "中级"),
        ("advanced", "高级"),
        ("expert", "专家级"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    practice_type = models.CharField(max_length=20, choices=PRACTICE_TYPE_CHOICES, verbose_name="练习类型")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="难度等级")
    duration_minutes = models.IntegerField(verbose_name="练习时长(分钟)")
    bpm = models.IntegerField(blank=True, null=True, verbose_name="节拍器BPM")
    metronome_enabled = models.BooleanField(default=False, verbose_name="是否使用节拍器")

    # 练习内容
    exercises = models.JSONField(default=list, verbose_name="练习项目")
    songs_practiced = models.JSONField(default=list, verbose_name="练习的歌曲")
    chords_practiced = models.JSONField(default=list, verbose_name="练习的和弦")
    scales_practiced = models.JSONField(default=list, verbose_name="练习的音阶")

    # 练习记录
    notes = models.TextField(blank=True, null=True, verbose_name="练习笔记")
    audio_recording_url = models.URLField(blank=True, null=True, verbose_name="录音文件")
    video_recording_url = models.URLField(blank=True, null=True, verbose_name="视频文件")

    # 评价
    self_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name="自我评价")
    difficulty_rating = models.IntegerField(
        blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name="难度评价"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="练习时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "吉他练习"
        verbose_name_plural = "吉他练习"

    def __str__(self):
        return f"{self.user.username} - {self.get_practice_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class GuitarExercise(models.Model):
    """吉他练习项目模型"""

    EXERCISE_CATEGORY_CHOICES = [
        ("chord", "和弦练习"),
        ("scale", "音阶练习"),
        ("arpeggio", "琶音练习"),
        ("strumming", "扫弦模式"),
        ("fingerpicking", "指弹模式"),
        ("theory", "乐理练习"),
        ("ear", "听力练习"),
    ]

    name = models.CharField(max_length=200, verbose_name="练习名称")
    category = models.CharField(max_length=20, choices=EXERCISE_CATEGORY_CHOICES, verbose_name="练习类别")
    description = models.TextField(verbose_name="练习描述")
    difficulty = models.CharField(max_length=20, choices=GuitarPracticeSession.DIFFICULTY_CHOICES, verbose_name="难度等级")

    # 练习内容
    tab_notation = models.TextField(blank=True, null=True, verbose_name="TAB谱")
    standard_notation = models.TextField(blank=True, null=True, verbose_name="五线谱")
    chord_diagrams = models.JSONField(default=list, verbose_name="和弦图")
    instructions = models.TextField(verbose_name="练习说明")

    # 媒体资源
    audio_url = models.URLField(blank=True, null=True, verbose_name="音频文件")
    video_url = models.URLField(blank=True, null=True, verbose_name="视频文件")
    image_url = models.URLField(blank=True, null=True, verbose_name="图片文件")

    # 练习参数
    recommended_bpm = models.IntegerField(default=60, verbose_name="推荐BPM")
    recommended_duration = models.IntegerField(default=10, verbose_name="推荐时长(分钟)")

    # 统计信息
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    average_rating = models.FloatField(default=0.0, verbose_name="平均评分")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["category", "difficulty", "name"]
        verbose_name = "吉他练习项目"
        verbose_name_plural = "吉他练习项目"

    def __str__(self):
        return f"{self.name} ({self.get_difficulty_display()})"


class GuitarSong(models.Model):
    """吉他歌曲模型"""

    GENRE_CHOICES = [
        ("pop", "流行"),
        ("rock", "摇滚"),
        ("folk", "民谣"),
        ("blues", "布鲁斯"),
        ("jazz", "爵士"),
        ("classical", "古典"),
        ("country", "乡村"),
        ("other", "其他"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "初级"),
        ("intermediate", "中级"),
        ("advanced", "高级"),
        ("expert", "专家级"),
    ]

    title = models.CharField(max_length=200, verbose_name="歌曲标题")
    artist = models.CharField(max_length=200, verbose_name="艺术家")
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, verbose_name="音乐风格")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="难度等级")

    # 乐谱信息
    key = models.CharField(max_length=10, blank=True, null=True, verbose_name="调性")
    time_signature = models.CharField(max_length=10, blank=True, null=True, verbose_name="拍号")
    bpm = models.IntegerField(blank=True, null=True, verbose_name="BPM")

    # 乐谱文件
    tab_notation = models.TextField(blank=True, null=True, verbose_name="TAB谱")
    chord_chart = models.TextField(blank=True, null=True, verbose_name="和弦谱")
    lyrics = models.TextField(blank=True, null=True, verbose_name="歌词")

    # 媒体资源
    original_audio_url = models.URLField(blank=True, null=True, verbose_name="原唱音频")
    backing_track_url = models.URLField(blank=True, null=True, verbose_name="伴奏音频")
    tutorial_video_url = models.URLField(blank=True, null=True, verbose_name="教学视频")

    # 练习信息
    chords_used = models.JSONField(default=list, verbose_name="使用的和弦")
    techniques_used = models.JSONField(default=list, verbose_name="使用的技巧")
    practice_notes = models.TextField(blank=True, null=True, verbose_name="练习要点")

    # 统计信息
    practice_count = models.IntegerField(default=0, verbose_name="练习次数")
    average_rating = models.FloatField(default=0.0, verbose_name="平均评分")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏次数")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["title", "artist"]
        verbose_name = "吉他歌曲"
        verbose_name_plural = "吉他歌曲"

    def __str__(self):
        return f"{self.title} - {self.artist}"


class GuitarProgress(models.Model):
    """吉他学习进度模型"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")

    # 总体进度
    total_practice_time = models.IntegerField(default=0, verbose_name="总练习时长(分钟)")
    total_sessions = models.IntegerField(default=0, verbose_name="总练习次数")
    current_streak = models.IntegerField(default=0, verbose_name="当前连续天数")
    longest_streak = models.IntegerField(default=0, verbose_name="最长连续天数")

    # 技能水平
    chord_mastery = models.FloatField(default=0.0, verbose_name="和弦掌握度")
    scale_mastery = models.FloatField(default=0.0, verbose_name="音阶掌握度")
    strumming_mastery = models.FloatField(default=0.0, verbose_name="扫弦掌握度")
    fingerpicking_mastery = models.FloatField(default=0.0, verbose_name="指弹掌握度")
    theory_mastery = models.FloatField(default=0.0, verbose_name="乐理掌握度")

    # 学习目标
    current_goal = models.CharField(max_length=200, blank=True, null=True, verbose_name="当前目标")
    goal_deadline = models.DateField(blank=True, null=True, verbose_name="目标截止日期")
    goal_progress = models.IntegerField(default=0, verbose_name="目标进度(%)")

    # 统计信息
    songs_learned = models.IntegerField(default=0, verbose_name="学会的歌曲数")
    exercises_completed = models.IntegerField(default=0, verbose_name="完成的练习数")
    average_session_length = models.FloatField(default=0.0, verbose_name="平均练习时长(分钟)")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "吉他学习进度"
        verbose_name_plural = "吉他学习进度"

    def __str__(self):
        return f"{self.user.username} - 吉他进度"

    def get_overall_mastery(self):
        """获取总体掌握度"""
        masteries = [
            self.chord_mastery,
            self.scale_mastery,
            self.strumming_mastery,
            self.fingerpicking_mastery,
            self.theory_mastery,
        ]
        return sum(masteries) / len(masteries)

    def get_skill_level(self):
        """获取技能等级"""
        overall_mastery = self.get_overall_mastery()
        if overall_mastery >= 90:
            return "专家级"
        elif overall_mastery >= 70:
            return "高级"
        elif overall_mastery >= 40:
            return "中级"
        else:
            return "初级"


class GuitarTab(models.Model):
    """吉他TAB谱模型"""

    TAB_TYPE_CHOICES = [
        ("chord", "和弦谱"),
        ("melody", "旋律谱"),
        ("bass", "贝斯谱"),
        ("full", "完整谱"),
    ]

    song = models.ForeignKey(GuitarSong, on_delete=models.CASCADE, related_name="tabs", verbose_name="歌曲")
    tab_type = models.CharField(max_length=20, choices=TAB_TYPE_CHOICES, verbose_name="TAB类型")
    title = models.CharField(max_length=200, verbose_name="TAB标题")

    # TAB内容
    tab_content = models.TextField(verbose_name="TAB内容")
    difficulty = models.CharField(max_length=20, choices=GuitarSong.DIFFICULTY_CHOICES, verbose_name="难度等级")

    # 版本信息
    version = models.CharField(max_length=20, default="1.0", verbose_name="版本号")
    is_official = models.BooleanField(default=False, verbose_name="是否官方版本")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")

    # 评价信息
    rating = models.FloatField(default=0.0, verbose_name="评分")
    rating_count = models.IntegerField(default=0, verbose_name="评分次数")

    # 使用统计
    download_count = models.IntegerField(default=0, verbose_name="下载次数")
    view_count = models.IntegerField(default=0, verbose_name="查看次数")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "吉他TAB谱"
        verbose_name_plural = "吉他TAB谱"
        unique_together = ["song", "tab_type", "version"]

    def __str__(self):
        return f"{self.song.title} - {self.get_tab_type_display()} v{self.version}"
