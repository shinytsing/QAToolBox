"""
三重觉醒改造计划服务
实现物理级存在感、代码健身房、痛苦货币化系统
"""

import random
import time
from datetime import timedelta
from typing import Dict, List

from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.utils import timezone

from ..models import (
    AIDependencyMeter,
    CodeWorkoutSession,
    CoPilotCollaboration,
    DailyWorkoutChallenge,
    ExhaustionProof,
    FitnessWorkoutSession,
    PainCurrency,
    WorkoutDashboard,
)


class TripleAwakeningService:
    """三重觉醒服务类"""

    def __init__(self):
        self.philosophy_questions = [
            "存在的意义是什么？",
            "痛苦与成长的关系？",
            "如何在虚无中创造价值？",
            "自由意志是否存在？",
            "意识与物质的边界在哪里？",
            "时间是否只是人类的幻觉？",
            "死亡是终点还是起点？",
            "爱是本能还是选择？",
            "真理是客观还是主观？",
            "人类是否真的在进化？",
        ]

    def create_fitness_workout(self, user: User, workout_data: Dict) -> FitnessWorkoutSession:
        """创建健身训练会话"""
        workout = FitnessWorkoutSession.objects.create(
            user=user,
            workout_type=workout_data.get("workout_type", "mixed"),
            intensity=workout_data.get("intensity", "moderate"),
            duration_minutes=workout_data.get("duration_minutes", 30),
            calories_burned=workout_data.get("calories_burned", 0),
            heart_rate_avg=workout_data.get("heart_rate_avg", 0),
            heart_rate_max=workout_data.get("heart_rate_max", 0),
            exercises=workout_data.get("exercises", []),
            notes=workout_data.get("notes", ""),
            audio_recording_url=workout_data.get("audio_recording_url", ""),
        )

        # 更新训练仪表盘
        self._update_workout_dashboard(user)

        # 如果达到极限，创建力竭证明
        if workout_data.get("is_exhausted", False):
            self._create_exhaustion_proof(user, "fitness", workout)

        return workout

    def create_code_workout(self, user: User, workout_data: Dict) -> CodeWorkoutSession:
        """创建代码训练会话"""
        workout = CodeWorkoutSession.objects.create(
            user=user,
            workout_type=workout_data.get("workout_type", "pull_up"),
            duration_seconds=workout_data.get("duration_seconds", 60),
            difficulty_level=workout_data.get("difficulty_level", 1),
            code_snippet=workout_data.get("code_snippet", ""),
            ai_rejection_count=workout_data.get("ai_rejection_count", 0),
            manual_code_lines=workout_data.get("manual_code_lines", 0),
            refactored_functions=workout_data.get("refactored_functions", 0),
        )

        # 更新AI依赖度仪表
        self._update_ai_dependency_meter(user)

        # 如果达到极限，创建力竭证明
        if workout_data.get("is_exhausted", False):
            self._create_exhaustion_proof(user, "coding", workout)

        return workout

    def _create_exhaustion_proof(self, user: User, proof_type: str, workout_session) -> ExhaustionProof:
        """创建力竭证明"""
        # 生成哲学问题
        philosophy_question = random.choice(self.philosophy_questions)

        # 生成推特内容
        twitter_content = f"用户@{user.username} 刚刚在#{philosophy_question}的思考中达到精神力竭"

        # 创建NFT元数据
        nft_metadata = {
            "name": f"力竭证明 #{workout_session.id}",
            "description": f"用户{user.username}在{proof_type}训练中达到极限的证明",
            "image": f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={twitter_content}",
            "attributes": [
                {"trait_type": "类型", "value": proof_type},
                {"trait_type": "哲学问题", "value": philosophy_question},
                {"trait_type": "时间戳", "value": timezone.now().isoformat()},
                {"trait_type": "用户", "value": user.username},
            ],
        }

        proof = ExhaustionProof.objects.create(
            user=user,
            proof_type=proof_type,
            title=f"{proof_type}力竭证明",
            description=twitter_content,
            heart_rate_data={
                "avg": getattr(workout_session, "heart_rate_avg", 0),
                "max": getattr(workout_session, "heart_rate_max", 0),
            },
            audio_recording_url=getattr(workout_session, "audio_recording_url", ""),
            nft_metadata=nft_metadata,
        )

        # 奖励痛苦货币
        self._award_pain_currency(user, "exhaustion", 10)

        return proof

    def _update_workout_dashboard(self, user: User):
        """更新训练仪表盘"""
        dashboard, created = WorkoutDashboard.objects.get_or_create(user=user)

        # 计算统计数据
        workouts = FitnessWorkoutSession.objects.filter(user=user)
        total_workouts = workouts.count()
        total_duration = workouts.aggregate(Sum("duration_minutes"))["duration_minutes__sum"] or 0
        total_calories = workouts.aggregate(Sum("calories_burned"))["calories_burned__sum"] or 0

        # 计算连续天数
        current_streak = self._calculate_streak(user)

        # 更新仪表盘
        dashboard.total_workouts = total_workouts
        dashboard.total_duration = total_duration
        dashboard.total_calories = total_calories
        dashboard.current_streak = current_streak
        if current_streak > dashboard.longest_streak:
            dashboard.longest_streak = current_streak

        # 计算最爱训练
        favorite = workouts.values("workout_type").annotate(count=Count("id")).order_by("-count").first()
        if favorite:
            dashboard.favorite_workout = favorite["workout_type"]

        dashboard.save()

    def _update_ai_dependency_meter(self, user: User):
        """更新AI依赖度仪表"""
        meter, created = AIDependencyMeter.objects.get_or_create(user=user)

        # 计算代码统计
        code_workouts = CodeWorkoutSession.objects.filter(user=user)
        total_lines = code_workouts.aggregate(Sum("manual_code_lines"))["manual_code_lines__sum"] or 0
        ai_rejections = code_workouts.aggregate(Sum("ai_rejection_count"))["ai_rejection_count__sum"] or 0

        # 模拟AI生成代码行数（实际项目中应该从代码编辑器获取）
        ai_lines = total_lines * 0.3  # 假设30%的代码是AI生成的

        meter.total_code_lines = total_lines + int(ai_lines)
        meter.ai_generated_lines = int(ai_lines)
        meter.manual_code_lines = total_lines
        meter.ai_rejection_count = ai_rejections
        meter.dependency_score = meter.calculate_dependency_score()
        meter.save()

    def _calculate_streak(self, user: User) -> int:
        """计算连续训练天数"""
        workouts = FitnessWorkoutSession.objects.filter(user=user).order_by("-created_at")
        if not workouts:
            return 0

        streak = 0
        current_date = timezone.now().date()

        for i in range(30):  # 最多检查30天
            check_date = current_date - timedelta(days=i)
            if workouts.filter(created_at__date=check_date).exists():
                streak += 1
            else:
                break

        return streak

    def _award_pain_currency(self, user: User, currency_type: str, amount: int):
        """奖励痛苦货币"""
        currency, created = PainCurrency.objects.get_or_create(
            user=user, currency_type=currency_type, defaults={"amount": 0, "total_earned": 0, "total_spent": 0}
        )

        currency.amount += amount
        currency.total_earned += amount
        currency.save()

    def create_copilot_collaboration(self, user: User, collaboration_data: Dict) -> CoPilotCollaboration:
        """创建AI协作声明"""
        collaboration = CoPilotCollaboration.objects.create(
            user=user,
            collaboration_type=collaboration_data.get("collaboration_type", "skeleton"),
            original_code=collaboration_data.get("original_code", ""),
            ai_generated_code=collaboration_data.get("ai_generated_code", ""),
            final_code=collaboration_data.get("final_code", ""),
            project_name=collaboration_data.get("project_name", ""),
            description=collaboration_data.get("description", ""),
        )

        return collaboration

    def get_daily_challenge(self, user: User, challenge_type: str = "mixed") -> DailyWorkoutChallenge:
        """获取或创建每日挑战"""
        today = timezone.now().date()
        challenge, created = DailyWorkoutChallenge.objects.get_or_create(
            user=user, date=today, defaults={"challenge_type": challenge_type}
        )

        if created:
            # 生成每日任务
            challenge.tasks = self._generate_daily_tasks(challenge_type)
            challenge.save()

        return challenge

    def _generate_daily_tasks(self, challenge_type: str) -> List[Dict]:
        """生成每日任务"""
        if challenge_type == "fitness":
            return [
                {"id": 1, "type": "fitness", "title": "完成30个深蹲", "points": 10, "completed": False},
                {"id": 2, "type": "fitness", "title": "做20个俯卧撑", "points": 15, "completed": False},
                {"id": 3, "type": "fitness", "title": "平板支撑2分钟", "points": 20, "completed": False},
                {"id": 4, "type": "fitness", "title": "跑步30分钟", "points": 25, "completed": False},
            ]
        elif challenge_type == "coding":
            return [
                {"id": 1, "type": "coding", "title": "写1行原生JS", "points": 5, "completed": False},
                {"id": 2, "type": "coding", "title": "拒绝1次AI补全", "points": 10, "completed": False},
                {"id": 3, "type": "coding", "title": "重构1个函数", "points": 15, "completed": False},
                {"id": 4, "type": "coding", "title": "手写一个算法", "points": 20, "completed": False},
            ]
        else:  # mixed
            return [
                {"id": 1, "type": "fitness", "title": "完成20个深蹲", "points": 8, "completed": False},
                {"id": 2, "type": "coding", "title": "写1行原生JS", "points": 5, "completed": False},
                {"id": 3, "type": "fitness", "title": "平板支撑1分钟", "points": 10, "completed": False},
                {"id": 4, "type": "coding", "title": "拒绝1次AI补全", "points": 10, "completed": False},
            ]

    def complete_task(self, user: User, task_id: int) -> Dict:
        """完成任务"""
        challenge = self.get_daily_challenge(user)

        # 查找任务
        task = None
        for t in challenge.tasks:
            if t["id"] == task_id and not t["completed"]:
                task = t
                break

        if not task:
            return {"success": False, "message": "任务不存在或已完成"}

        # 标记任务完成
        task["completed"] = True
        challenge.completed_tasks.append(task)
        challenge.total_score += task["points"]

        # 检查是否完成所有任务
        all_completed = all(t["completed"] for t in challenge.tasks)
        if all_completed and not challenge.is_completed:
            challenge.is_completed = True
            challenge.completed_at = timezone.now()
            challenge.reward_unlocked = True
            # 解锁"开发者增肌食谱"彩蛋
            self._award_pain_currency(user, "breakthrough", 50)

        challenge.save()

        return {"success": True, "task": task, "total_score": challenge.total_score, "all_completed": all_completed}

    def get_workout_dashboard_data(self, user: User) -> Dict:
        """获取训练仪表盘数据"""
        dashboard, created = WorkoutDashboard.objects.get_or_create(user=user)

        # 获取最近的训练数据
        recent_workouts = FitnessWorkoutSession.objects.filter(user=user).order_by("-created_at")[:10]

        # 获取力量增长曲线数据
        strength_data = self._get_strength_growth_data(user)

        return {
            "dashboard": {
                "total_workouts": dashboard.total_workouts,
                "total_duration": dashboard.total_duration,
                "total_calories": dashboard.total_calories,
                "current_streak": dashboard.current_streak,
                "longest_streak": dashboard.longest_streak,
                "favorite_workout": dashboard.favorite_workout,
            },
            "recent_workouts": [
                {
                    "id": w.id,
                    "type": w.get_workout_type_display(),
                    "intensity": w.get_intensity_display(),
                    "duration": w.duration_minutes,
                    "calories": w.calories_burned,
                    "date": w.created_at.strftime("%Y-%m-%d %H:%M"),
                }
                for w in recent_workouts
            ],
            "strength_growth": strength_data,
        }

    def _get_strength_growth_data(self, user: User) -> Dict:
        """获取力量增长曲线数据"""
        # 获取最近30天的训练数据
        thirty_days_ago = timezone.now() - timedelta(days=30)
        workouts = FitnessWorkoutSession.objects.filter(user=user, created_at__gte=thirty_days_ago).order_by("created_at")

        # 按日期分组统计
        daily_stats = {}
        for workout in workouts:
            date = workout.created_at.date()
            if date not in daily_stats:
                daily_stats[date] = {"workouts": 0, "total_duration": 0, "total_calories": 0}
            daily_stats[date]["workouts"] += 1
            daily_stats[date]["total_duration"] += workout.duration_minutes
            daily_stats[date]["total_calories"] += workout.calories_burned

        # 转换为图表数据格式
        chart_data = []
        for date, stats in sorted(daily_stats.items()):
            chart_data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "workouts": stats["workouts"],
                    "duration": stats["total_duration"],
                    "calories": stats["total_calories"],
                }
            )

        return chart_data

    def get_ai_dependency_data(self, user: User) -> Dict:
        """获取AI依赖度数据"""
        meter, created = AIDependencyMeter.objects.get_or_create(user=user)

        return {
            "total_lines": meter.total_code_lines,
            "ai_lines": meter.ai_generated_lines,
            "manual_lines": meter.manual_code_lines,
            "rejection_count": meter.ai_rejection_count,
            "dependency_score": meter.dependency_score,
            "last_updated": meter.last_updated.strftime("%Y-%m-%d %H:%M"),
        }

    def get_pain_currency_data(self, user: User) -> Dict:
        """获取痛苦货币数据"""
        currencies = PainCurrency.objects.filter(user=user)

        currency_data = {}
        for currency in currencies:
            currency_data[currency.currency_type] = {
                "amount": currency.amount,
                "total_earned": currency.total_earned,
                "total_spent": currency.total_spent,
                "display_name": currency.get_currency_type_display(),
            }

        return currency_data

    def record_audio_exhaustion(self, user: User, audio_data: bytes, workout_session_id: int) -> str:
        """记录力竭喘息声"""
        # 这里应该实现音频文件保存逻辑
        # 为了演示，我们返回一个模拟的URL
        timestamp = int(time.time())
        audio_url = f"/media/exhaustion_audio/{user.id}_{workout_session_id}_{timestamp}.wav"

        # 更新训练会话的录音URL
        try:
            workout = FitnessWorkoutSession.objects.get(id=workout_session_id, user=user)
            workout.audio_recording_url = audio_url
            workout.save()
        except FitnessWorkoutSession.DoesNotExist:
            pass

        return audio_url

    def generate_exhaustion_tweet(self, user: User, proof_type: str) -> str:
        """生成力竭推特内容"""
        philosophy_question = random.choice(self.philosophy_questions)
        return f"用户@{user.username} 刚刚在#{philosophy_question}的思考中达到精神力竭 🔥💪 #三重觉醒 #力竭证明"


class WorkoutAudioProcessor:
    """训练音频处理器"""

    @staticmethod
    def process_exhaustion_audio(audio_data: bytes) -> Dict:
        """处理力竭音频"""
        # 这里应该实现音频分析逻辑
        # 为了演示，返回模拟数据
        return {
            "duration": 5.0,
            "intensity": random.randint(7, 10),
            "breathing_rate": random.randint(20, 40),
            "exhaustion_level": random.randint(8, 10),
        }

    @staticmethod
    def generate_css_animation(intensity: int) -> str:
        """根据强度生成CSS动画"""
        if intensity >= 9:
            return """
            .exhaustion-animation {
                animation: extremeShake 0.5s ease-in-out infinite;
                filter: hue-rotate(45deg) brightness(1.2);
            }
            @keyframes extremeShake {
                0%, 100% { transform: translateX(0px) rotate(0deg); }
                25% { transform: translateX(-3px) rotate(-1deg); }
                75% { transform: translateX(3px) rotate(1deg); }
            }
            """
        elif intensity >= 7:
            return """
            .exhaustion-animation {
                animation: moderateShake 1s ease-in-out infinite;
                filter: brightness(1.1);
            }
            @keyframes moderateShake {
                0%, 100% { transform: translateX(0px); }
                50% { transform: translateX(-2px); }
            }
            """
        else:
            return """
            .exhaustion-animation {
                animation: lightPulse 2s ease-in-out infinite;
            }
            @keyframes lightPulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.8; }
            }
            """
