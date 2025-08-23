from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class EnhancedFitnessWorkoutSession(models.Model):
    """增强版健身训练会话模型"""
    WORKOUT_TYPE_CHOICES = [
        ('strength', '力量训练'),
        ('cardio', '有氧运动'),
        ('flexibility', '柔韧性训练'),
        ('balance', '平衡训练'),
        ('mixed', '混合训练'),
    ]
    
    INTENSITY_CHOICES = [
        ('light', '轻度'),
        ('moderate', '中度'),
        ('intense', '高强度'),
        ('extreme', '极限'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES, verbose_name='训练类型')
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, verbose_name='强度等级')
    duration_minutes = models.IntegerField(verbose_name='训练时长(分钟)')
    calories_burned = models.IntegerField(default=0, verbose_name='消耗卡路里')
    heart_rate_avg = models.IntegerField(default=0, verbose_name='平均心率')
    heart_rate_max = models.IntegerField(default=0, verbose_name='最大心率')
    exercises = models.JSONField(default=list, verbose_name='训练动作')
    notes = models.TextField(blank=True, null=True, verbose_name='训练笔记')
    audio_recording_url = models.URLField(blank=True, null=True, verbose_name='喘息录音')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='训练时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '健身训练'
        verbose_name_plural = '健身训练'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EnhancedCodeWorkoutSession(models.Model):
    """增强版代码训练会话模型"""
    WORKOUT_TYPE_CHOICES = [
        ('pull_up', '引体向上(原生JS)'),
        ('plank', '平板支撑(拒绝AI)'),
        ('squat', '深蹲(重构函数)'),
        ('push_up', '俯卧撑(手写算法)'),
        ('burpee', '波比跳(调试代码)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES, verbose_name='训练类型')
    duration_seconds = models.IntegerField(verbose_name='训练时长(秒)')
    difficulty_level = models.IntegerField(default=1, verbose_name='难度等级')
    code_snippet = models.TextField(blank=True, null=True, verbose_name='代码片段')
    ai_rejection_count = models.IntegerField(default=0, verbose_name='拒绝AI次数')
    manual_code_lines = models.IntegerField(default=0, verbose_name='手写代码行数')
    refactored_functions = models.IntegerField(default=0, verbose_name='重构函数数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='训练时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '代码训练'
        verbose_name_plural = '代码训练'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EnhancedExhaustionProof(models.Model):
    """增强版力竭证明NFT模型"""
    PROOF_TYPE_CHOICES = [
        ('fitness', '健身力竭'),
        ('coding', '编程力竭'),
        ('mental', '精神力竭'),
        ('mixed', '混合力竭'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPE_CHOICES, verbose_name='证明类型')
    title = models.CharField(max_length=200, verbose_name='证明标题')
    description = models.TextField(verbose_name='证明描述')
    heart_rate_data = models.JSONField(default=dict, verbose_name='心率数据')
    audio_recording_url = models.URLField(blank=True, null=True, verbose_name='录音文件')
    nft_metadata = models.JSONField(default=dict, verbose_name='NFT元数据')
    nft_token_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='NFT代币ID')
    blockchain_tx_hash = models.CharField(max_length=200, blank=True, null=True, verbose_name='区块链交易哈希')
    is_minted = models.BooleanField(default=False, verbose_name='是否已铸造')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '力竭证明'
        verbose_name_plural = '力竭证明'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_proof_type_display()} - {self.title}"


class EnhancedAIDependencyMeter(models.Model):
    """增强版AI依赖度仪表模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    total_code_lines = models.IntegerField(default=0, verbose_name='总代码行数')
    ai_generated_lines = models.IntegerField(default=0, verbose_name='AI生成代码行数')
    manual_code_lines = models.IntegerField(default=0, verbose_name='手写代码行数')
    ai_rejection_count = models.IntegerField(default=0, verbose_name='拒绝AI次数')
    dependency_score = models.FloatField(default=0.0, verbose_name='依赖度评分')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = 'AI依赖度仪表'
        verbose_name_plural = 'AI依赖度仪表'
    
    def __str__(self):
        return f"{self.user.username} - 依赖度: {self.dependency_score:.2f}%"
    
    def calculate_dependency_score(self):
        """计算AI依赖度评分"""
        if self.total_code_lines == 0:
            return 0.0
        return (self.ai_generated_lines / self.total_code_lines) * 100


class EnhancedCoPilotCollaboration(models.Model):
    """增强版AI协作声明模型"""
    COLLABORATION_TYPE_CHOICES = [
        ('skeleton', '骨架代码'),
        ('muscle', '肌肉代码'),
        ('nervous', '神经系统'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    collaboration_type = models.CharField(max_length=20, choices=COLLABORATION_TYPE_CHOICES, verbose_name='协作类型')
    original_code = models.TextField(verbose_name='原始代码')
    ai_generated_code = models.TextField(verbose_name='AI生成代码')
    final_code = models.TextField(verbose_name='最终代码')
    project_name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, null=True, verbose_name='协作描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI协作声明'
        verbose_name_plural = 'AI协作声明'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_collaboration_type_display()} - {self.project_name}"


class EnhancedDailyWorkoutChallenge(models.Model):
    """增强版每日训练挑战模型"""
    CHALLENGE_TYPE_CHOICES = [
        ('fitness', '健身挑战'),
        ('coding', '编程挑战'),
        ('mixed', '混合挑战'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES, verbose_name='挑战类型')
    date = models.DateField(auto_now_add=True, verbose_name='挑战日期')
    tasks = models.JSONField(default=list, verbose_name='挑战任务')
    completed_tasks = models.JSONField(default=list, verbose_name='完成任务')
    total_score = models.IntegerField(default=0, verbose_name='总得分')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    reward_unlocked = models.BooleanField(default=False, verbose_name='是否解锁奖励')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '每日训练挑战'
        verbose_name_plural = '每日训练挑战'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_challenge_type_display()} - {self.date}"


class EnhancedPainCurrency(models.Model):
    """增强版痛苦货币模型"""
    CURRENCY_TYPE_CHOICES = [
        ('exhaustion', '力竭币'),
        ('rejection', '拒绝币'),
        ('manual', '手写币'),
        ('breakthrough', '突破币'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    currency_type = models.CharField(max_length=20, choices=CURRENCY_TYPE_CHOICES, verbose_name='货币类型')
    amount = models.IntegerField(default=0, verbose_name='数量')
    total_earned = models.IntegerField(default=0, verbose_name='总获得')
    total_spent = models.IntegerField(default=0, verbose_name='总消费')
    last_earned = models.DateTimeField(auto_now=True, verbose_name='最后获得时间')
    
    class Meta:
        unique_together = ['user', 'currency_type']
        verbose_name = '痛苦货币'
        verbose_name_plural = '痛苦货币'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_currency_type_display()}: {self.amount}"


class EnhancedWorkoutDashboard(models.Model):
    """增强版训练仪表盘模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    total_workouts = models.IntegerField(default=0, verbose_name='总训练次数')
    total_duration = models.IntegerField(default=0, verbose_name='总训练时长(分钟)')
    total_calories = models.IntegerField(default=0, verbose_name='总消耗卡路里')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    favorite_workout = models.CharField(max_length=50, blank=True, null=True, verbose_name='最爱训练')
    weekly_stats = models.JSONField(default=dict, verbose_name='周统计')
    monthly_stats = models.JSONField(default=dict, verbose_name='月统计')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = '训练仪表盘'
        verbose_name_plural = '训练仪表盘'
    
    def __str__(self):
        return f"{self.user.username} - 训练仪表盘"


class EnhancedExerciseWeightRecord(models.Model):
    """增强版锻炼重量记录模型"""
    EXERCISE_TYPE_CHOICES = [
        # 三大项
        ('squat', '深蹲'),
        ('bench_press', '卧推'),
        ('deadlift', '硬拉'),
        # 其他力量训练
        ('overhead_press', '推举'),
        ('barbell_row', '杠铃划船'),
        ('pull_up', '引体向上'),
        ('dip', '双杠臂屈伸'),
        ('lunge', '弓步蹲'),
        ('leg_press', '腿举'),
        ('leg_curl', '腿弯举'),
        ('leg_extension', '腿伸展'),
        ('calf_raise', '提踵'),
        ('bicep_curl', '弯举'),
        ('tricep_extension', '臂屈伸'),
        ('shoulder_press', '肩推'),
        ('lateral_raise', '侧平举'),
        ('rear_delt_fly', '后三角肌飞鸟'),
        ('chest_fly', '飞鸟'),
        ('lat_pulldown', '高位下拉'),
        ('face_pull', '面拉'),
        ('shrug', '耸肩'),
        ('upright_row', '直立划船'),
        ('good_morning', '早安式'),
        ('romanian_deadlift', '罗马尼亚硬拉'),
        ('sumo_deadlift', '相扑硬拉'),
        ('front_squat', '前蹲'),
        ('back_squat', '后蹲'),
        ('box_squat', '箱式深蹲'),
        ('pause_squat', '暂停深蹲'),
        ('close_grip_bench', '窄握卧推'),
        ('wide_grip_bench', '宽握卧推'),
        ('incline_bench', '上斜卧推'),
        ('decline_bench', '下斜卧推'),
        ('dumbbell_bench', '哑铃卧推'),
        ('dumbbell_squat', '哑铃深蹲'),
        ('goblet_squat', '高脚杯深蹲'),
        ('bulgarian_split_squat', '保加利亚分腿蹲'),
        ('step_up', '台阶上'),
        ('hip_thrust', '臀桥'),
        ('glute_bridge', '臀桥'),
        ('plank', '平板支撑'),
        ('side_plank', '侧平板'),
        ('crunch', '卷腹'),
        ('sit_up', '仰卧起坐'),
        ('russian_twist', '俄罗斯转体'),
        ('mountain_climber', '登山者'),
        ('burpee', '波比跳'),
        ('jumping_jack', '开合跳'),
        ('high_knee', '高抬腿'),
        ('butt_kick', '后踢腿'),
        ('other', '其他'),
    ]
    
    REP_TYPE_CHOICES = [
        ('1rm', '1RM'),
        ('3rm', '3RM'),
        ('5rm', '5RM'),
        ('8rm', '8RM'),
        ('10rm', '10RM'),
        ('12rm', '12RM'),
        ('15rm', '15RM'),
        ('20rm', '20RM'),
        ('max_reps', '最大次数'),
        ('custom', '自定义'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES, verbose_name='锻炼类型')
    weight = models.FloatField(verbose_name='重量(kg)')
    reps = models.IntegerField(verbose_name='次数')
    rep_type = models.CharField(max_length=10, choices=REP_TYPE_CHOICES, default='custom', verbose_name='次数类型')
    sets = models.IntegerField(default=1, verbose_name='组数')
    rpe = models.IntegerField(null=True, blank=True, verbose_name='RPE(1-10)')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    workout_date = models.DateField(verbose_name='训练日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')
    
    class Meta:
        ordering = ['-workout_date', '-created_at']
        verbose_name = '锻炼重量记录'
        verbose_name_plural = '锻炼重量记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_exercise_type_display()} - {self.weight}kg x {self.reps}次"
    
    def get_estimated_1rm(self):
        """估算1RM"""
        if self.reps == 1:
            return self.weight
        
        # 使用Epley公式估算1RM
        if self.reps <= 10:
            return round(self.weight * (1 + self.reps / 30), 1)
        else:
            # 对于高次数，使用更保守的估算
            return round(self.weight * (1 + self.reps / 40), 1)
    
    def get_weight_class(self):
        """获取重量等级"""
        if self.exercise_type in ['squat', 'bench_press', 'deadlift']:
            if self.weight < 50:
                return '初学者'
            elif self.weight < 100:
                return '进阶者'
            elif self.weight < 150:
                return '中级者'
            elif self.weight < 200:
                return '高级者'
            else:
                return '专家级'
        return '标准'


class EnhancedFitnessStrengthProfile(models.Model):
    """增强版健身力量档案模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 三大项最佳记录
    squat_1rm = models.FloatField(null=True, blank=True, verbose_name='深蹲1RM(kg)')
    squat_1rm_date = models.DateField(null=True, blank=True, verbose_name='深蹲1RM日期')
    bench_press_1rm = models.FloatField(null=True, blank=True, verbose_name='卧推1RM(kg)')
    bench_press_1rm_date = models.DateField(null=True, blank=True, verbose_name='卧推1RM日期')
    deadlift_1rm = models.FloatField(null=True, blank=True, verbose_name='硬拉1RM(kg)')
    deadlift_1rm_date = models.DateField(null=True, blank=True, verbose_name='硬拉1RM日期')
    
    # 总重量
    total_1rm = models.FloatField(null=True, blank=True, verbose_name='三大项总重量(kg)')
    
    # 体重相关
    bodyweight = models.FloatField(null=True, blank=True, verbose_name='记录时体重(kg)')
    bodyweight_date = models.DateField(null=True, blank=True, verbose_name='体重记录日期')
    
    # 力量系数
    strength_coefficient = models.FloatField(null=True, blank=True, verbose_name='力量系数(总重量/体重)')
    
    # 目标设定
    squat_goal = models.FloatField(null=True, blank=True, verbose_name='深蹲目标(kg)')
    bench_press_goal = models.FloatField(null=True, blank=True, verbose_name='卧推目标(kg)')
    deadlift_goal = models.FloatField(null=True, blank=True, verbose_name='硬拉目标(kg)')
    total_goal = models.FloatField(null=True, blank=True, verbose_name='总重量目标(kg)')
    
    # 统计信息
    total_workouts = models.IntegerField(default=0, verbose_name='总训练次数')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    total_duration = models.IntegerField(default=0, verbose_name='总训练时长(分钟)')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '健身力量档案'
        verbose_name_plural = '健身力量档案'
    
    def __str__(self):
        return f"{self.user.username} - 力量档案"
    
    def update_stats(self):
        """更新统计数据"""
        from datetime import datetime, timedelta
        
        # 更新总训练次数
        self.total_workouts = EnhancedExerciseWeightRecord.objects.filter(user=self.user).count()
        
        # 更新连续天数
        records = EnhancedExerciseWeightRecord.objects.filter(user=self.user).order_by('-workout_date')
        if records.exists():
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            current_date = datetime.now().date()
            
            for i, record in enumerate(records):
                if i == 0:
                    if record.workout_date == current_date:
                        temp_streak = 1
                    else:
                        break
                else:
                    prev_record = records[i-1]
                    if (prev_record.workout_date - record.workout_date).days == 1:
                        temp_streak += 1
                    else:
                        break
            
            self.current_streak = temp_streak
            
            # 计算最长连续天数
            dates = list(records.values_list('workout_date', flat=True).distinct())
            if dates:
                dates.sort(reverse=True)
                temp_streak = 1
                longest_streak = 1
                
                for i in range(1, len(dates)):
                    if (dates[i-1] - dates[i]).days == 1:
                        temp_streak += 1
                        longest_streak = max(longest_streak, temp_streak)
                    else:
                        temp_streak = 1
                
                self.longest_streak = longest_streak
        
        self.save()
    
    def update_1rm_records(self):
        """更新1RM记录"""
        # 更新深蹲1RM
        squat_records = EnhancedExerciseWeightRecord.objects.filter(
            user=self.user, 
            exercise_type='squat'
        ).order_by('-weight', '-workout_date')
        
        if squat_records.exists():
            best_squat = squat_records.first()
            self.squat_1rm = best_squat.get_estimated_1rm()
            self.squat_1rm_date = best_squat.workout_date
        
        # 更新卧推1RM
        bench_records = EnhancedExerciseWeightRecord.objects.filter(
            user=self.user, 
            exercise_type='bench_press'
        ).order_by('-weight', '-workout_date')
        
        if bench_records.exists():
            best_bench = bench_records.first()
            self.bench_press_1rm = best_bench.get_estimated_1rm()
            self.bench_press_1rm_date = best_bench.workout_date
        
        # 更新硬拉1RM
        deadlift_records = EnhancedExerciseWeightRecord.objects.filter(
            user=self.user, 
            exercise_type='deadlift'
        ).order_by('-weight', '-workout_date')
        
        if deadlift_records.exists():
            best_deadlift = deadlift_records.first()
            self.deadlift_1rm = best_deadlift.get_estimated_1rm()
            self.deadlift_1rm_date = best_deadlift.workout_date
        
        # 更新总重量
        if self.squat_1rm and self.bench_press_1rm and self.deadlift_1rm:
            self.total_1rm = self.squat_1rm + self.bench_press_1rm + self.deadlift_1rm
        
        # 更新力量系数
        if self.total_1rm and self.bodyweight:
            self.strength_coefficient = round(self.total_1rm / self.bodyweight, 2)
        
        self.save()
    
    def get_strength_level(self):
        """获取力量等级"""
        if not self.total_1rm:
            return '未记录'
        
        if self.total_1rm < 200:
            return '初学者'
        elif self.total_1rm < 400:
            return '进阶者'
        elif self.total_1rm < 600:
            return '中级者'
        elif self.total_1rm < 800:
            return '高级者'
        else:
            return '专家级'
    
    def get_progress_percentage(self, exercise_type):
        """获取进度百分比"""
        current = getattr(self, f'{exercise_type}_1rm', 0) or 0
        goal = getattr(self, f'{exercise_type}_goal', 0) or 0
        
        if goal == 0:
            return 0
        
        return min(round((current / goal) * 100, 1), 100)


class EnhancedFitnessUserProfile(models.Model):
    """增强版健身用户档案模型"""
    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
    ]
    
    GOAL_CHOICES = [
        ('lose_weight', '减脂'),
        ('gain_muscle', '增肌'),
        ('maintain', '维持体重'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', '久坐'),
        ('light', '轻度活动'),
        ('moderate', '中度活动'),
        ('high', '重度活动'),
    ]
    
    INTENSITY_CHOICES = [
        ('conservative', '保守型'),
        ('balanced', '均衡型'),
        ('aggressive', '激进型'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    age = models.IntegerField(default=25, verbose_name='年龄')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    height = models.FloatField(default=170.0, verbose_name='身高(cm)')
    weight = models.FloatField(default=70.0, verbose_name='当前体重(kg)')
    body_fat_percentage = models.FloatField(null=True, blank=True, verbose_name='体脂率(%)')
    bmr = models.FloatField(null=True, blank=True, verbose_name='基础代谢率')
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='maintain', verbose_name='健身目标')
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='balanced', verbose_name='目标强度')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='moderate', verbose_name='日常活动量')
    dietary_preferences = models.JSONField(default=list, verbose_name='饮食偏好')
    allergies = models.JSONField(default=list, verbose_name='过敏食物')
    training_days_per_week = models.IntegerField(default=3, verbose_name='每周训练天数')
    training_intensity = models.CharField(max_length=20, default='moderate', verbose_name='训练强度')
    training_duration = models.IntegerField(default=60, verbose_name='训练时长(分钟)')
    
    # 徽章和成就展示
    selected_badges = models.JSONField(default=dict, verbose_name='选中的徽章')
    badge_showcase_layout = models.CharField(max_length=20, default='grid', verbose_name='徽章展示布局')
    show_achievements_publicly = models.BooleanField(default=True, verbose_name='公开显示成就')
    
    # 个人资料展示设置
    profile_visibility = models.CharField(max_length=20, default='public', verbose_name='资料可见性')
    show_stats_publicly = models.BooleanField(default=True, verbose_name='公开显示统计')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '健身用户档案'
        verbose_name_plural = '健身用户档案'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_display()}"


class EnhancedDietPlan(models.Model):
    """增强版饮食计划模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    daily_calories = models.IntegerField(verbose_name='每日总热量')
    protein_goal = models.IntegerField(verbose_name='蛋白质目标(g)')
    carbs_goal = models.IntegerField(verbose_name='碳水目标(g)')
    fat_goal = models.IntegerField(verbose_name='脂肪目标(g)')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '饮食计划'
        verbose_name_plural = '饮食计划'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.start_date} 到 {self.end_date}"


class EnhancedMeal(models.Model):
    """增强版餐食模型"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐'),
        ('pre_workout', '训练前'),
        ('post_workout', '训练后'),
    ]
    
    plan = models.ForeignKey(EnhancedDietPlan, on_delete=models.CASCADE, verbose_name='饮食计划')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name='餐食类型')
    day_of_week = models.IntegerField(verbose_name='星期几(1-7)')
    description = models.TextField(verbose_name='餐食描述')
    ingredients = models.JSONField(default=list, verbose_name='食材清单')
    calories = models.IntegerField(verbose_name='热量')
    protein = models.FloatField(verbose_name='蛋白质(g)')
    carbs = models.FloatField(verbose_name='碳水(g)')
    fat = models.FloatField(verbose_name='脂肪(g)')
    ideal_time = models.TimeField(null=True, blank=True, verbose_name='理想用餐时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '餐食'
        verbose_name_plural = '餐食'
        ordering = ['day_of_week', 'meal_type']
    
    def __str__(self):
        return f"{self.plan.user.username} - {self.get_meal_type_display()} - 第{self.day_of_week}天"


class EnhancedNutritionReminder(models.Model):
    """增强版营养提醒模型"""
    REMINDER_TYPE_CHOICES = [
        ('meal_time', '用餐时间'),
        ('pre_workout', '训练前加餐'),
        ('post_workout', '训练后补充'),
        ('hydration', '水分补充'),
        ('meal_log', '餐食记录'),
        ('weight_track', '体重记录'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='提醒类型')
    message = models.TextField(verbose_name='提醒内容')
    trigger_time = models.TimeField(null=True, blank=True, verbose_name='触发时间')
    trigger_days = models.JSONField(default=list, verbose_name='触发日期(1-7)')
    is_recurring = models.BooleanField(default=True, verbose_name='是否重复')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    last_sent = models.DateTimeField(null=True, blank=True, verbose_name='最后发送时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '营养提醒'
        verbose_name_plural = '营养提醒'
        ordering = ['trigger_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_reminder_type_display()}"


class EnhancedMealLog(models.Model):
    """增强版餐食记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    meal = models.ForeignKey(EnhancedMeal, on_delete=models.CASCADE, verbose_name='计划餐食')
    consumed_date = models.DateField(verbose_name='消费日期')
    consumed_time = models.TimeField(verbose_name='消费时间')
    actual_calories = models.IntegerField(null=True, blank=True, verbose_name='实际热量')
    actual_protein = models.FloatField(null=True, blank=True, verbose_name='实际蛋白质')
    actual_carbs = models.FloatField(null=True, blank=True, verbose_name='实际碳水')
    actual_fat = models.FloatField(null=True, blank=True, verbose_name='实际脂肪')
    notes = models.TextField(blank=True, verbose_name='备注')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '餐食记录'
        verbose_name_plural = '餐食记录'
        ordering = ['-consumed_date', '-consumed_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.meal.get_meal_type_display()} - {self.consumed_date}"


class EnhancedWeightTracking(models.Model):
    """增强版体重追踪模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    weight = models.FloatField(verbose_name='体重(kg)')
    body_fat_percentage = models.FloatField(null=True, blank=True, verbose_name='体脂率(%)')
    measurement_date = models.DateField(verbose_name='测量日期')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '体重追踪'
        verbose_name_plural = '体重追踪'
        ordering = ['-measurement_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.weight}kg - {self.measurement_date}"


class EnhancedFoodDatabase(models.Model):
    """增强版食物数据库模型"""
    name = models.CharField(max_length=200, verbose_name='食物名称')
    category = models.CharField(max_length=100, verbose_name='食物类别')
    calories_per_100g = models.FloatField(verbose_name='每100g热量')
    protein_per_100g = models.FloatField(verbose_name='每100g蛋白质')
    carbs_per_100g = models.FloatField(verbose_name='每100g碳水')
    fat_per_100g = models.FloatField(verbose_name='每100g脂肪')
    fiber_per_100g = models.FloatField(default=0, verbose_name='每100g纤维')
    is_vegetarian = models.BooleanField(default=False, verbose_name='是否素食')
    is_gluten_free = models.BooleanField(default=False, verbose_name='是否无麸质')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '食物数据库'
        verbose_name_plural = '食物数据库'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
