import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.tools.models import (
    ToolUsageLog, SocialMediaSubscription, LifeDiaryEntry,
    ChatRoom, LifeGoal, FitnessWorkoutSession, TravelGuide,
    ExerciseWeightRecord
)


@pytest.mark.django_db
class TestToolUsageLog:
    """工具使用日志测试"""
    
    def test_create_tool_usage_log(self, user):
        """测试创建工具使用日志"""
        log = ToolUsageLog.objects.create(
            user=user,
            tool_type='TEST_CASE',
            input_data='test input',
            output_file='test_output.txt'
        )
        assert log.user == user
        assert log.tool_type == 'TEST_CASE'
        assert log.input_data == 'test input'
        assert log.output_file == 'test_output.txt'
    
    def test_get_user_tool_usage(self, user):
        """测试获取用户工具使用统计"""
        # 创建测试数据
        ToolUsageLog.objects.create(
            user=user,
            tool_type='TEST_CASE',
            input_data='test',
            output_file='test.txt'
        )
        
        stats = ToolUsageLog.get_user_tool_usage(user, days=30)
        assert stats['total_usage'] == 1
        assert stats['recent_usage'] == 1
        assert len(stats['tool_breakdown']) == 1


@pytest.mark.django_db
class TestSocialMediaSubscription:
    """社交媒体订阅测试"""
    
    def test_create_subscription(self, user):
        """测试创建订阅"""
        subscription = SocialMediaSubscription.objects.create(
            user=user,
            platform='xiaohongshu',
            target_user_id='test_user_123',
            target_user_name='测试用户',
            subscription_types=['newPosts', 'newFollowers'],
            frequency=30
        )
        assert subscription.user == user
        assert subscription.platform == 'xiaohongshu'
        assert subscription.status == 'active'
    
    def test_should_check_now(self, user):
        """测试是否应该检查"""
        subscription = SocialMediaSubscription.objects.create(
            user=user,
            platform='xiaohongshu',
            target_user_id='test_user_123',
            target_user_name='测试用户',
            subscription_types=['newPosts'],
            frequency=30
        )
        # 新创建的订阅应该立即检查
        assert subscription.should_check_now() is True
        
        # 标记为已检查
        subscription.mark_checked()
        assert subscription.should_check_now() is False


@pytest.mark.django_db
class TestLifeDiaryEntry:
    """生活日记测试"""
    
    def test_create_diary_entry(self, user):
        """测试创建日记条目"""
        entry = LifeDiaryEntry.objects.create(
            user=user,
            date=timezone.now().date(),
            title='测试日记',
            content='这是测试内容',
            mood='good',
            weather='sunny'
        )
        assert entry.user == user
        assert entry.title == '测试日记'
        assert entry.mood == 'good'
        assert entry.word_count > 0
    
    def test_get_writing_streak(self, user):
        """测试获取写作连续天数"""
        # 创建连续3天的日记
        for i in range(3):
            date = timezone.now().date() - timedelta(days=i)
            LifeDiaryEntry.objects.create(
                user=user,
                date=date,
                title=f'日记{i+1}',
                content='测试内容',
                mood='good'
            )
        
        streak = LifeDiaryEntry.get_writing_streak(user)
        assert streak == 3


@pytest.mark.django_db
class TestFitnessProfile:
    """健身档案测试"""
    
    def test_create_fitness_profile(self, user):
        """测试创建健身档案"""
        profile = FitnessProfile.objects.create(
            user=user,
            bodyweight=70.0,
            height=175,
            squat_goal=100,
            bench_press_goal=80,
            deadlift_goal=120
        )
        assert profile.user == user
        assert profile.bodyweight == 70.0
        assert profile.squat_goal == 100
    
    def test_get_progress_percentage(self, user):
        """测试进度百分比计算"""
        profile = FitnessProfile.objects.create(
            user=user,
            squat_1rm=80,
            squat_goal=100,
            bench_press_1rm=60,
            bench_press_goal=80,
            deadlift_1rm=90,
            deadlift_goal=120
        )
        
        # 测试进度百分比计算
        squat_progress = profile.get_progress_percentage('squat')
        bench_progress = profile.get_progress_percentage('bench_press')
        deadlift_progress = profile.get_progress_percentage('deadlift')
        
        assert squat_progress == 80.0  # 80/100 * 100
        assert bench_progress == 75.0  # 60/80 * 100
        assert deadlift_progress == 75.0  # 90/120 * 100
    
    def test_get_progress_percentage_zero_goal(self, user):
        """测试目标为0时的进度百分比"""
        profile = FitnessProfile.objects.create(
            user=user,
            squat_1rm=80,
            squat_goal=0
        )
        
        progress = profile.get_progress_percentage('squat')
        assert progress == 0
    
    def test_get_progress_percentage_over_100(self, user):
        """测试超过100%的进度百分比"""
        profile = FitnessProfile.objects.create(
            user=user,
            squat_1rm=120,
            squat_goal=100
        )
        
        progress = profile.get_progress_percentage('squat')
        assert progress == 100.0  # 应该被限制在100%
    
    def test_get_strength_level(self, user):
        """测试力量等级判断"""
        # 测试初学者
        profile1 = FitnessProfile.objects.create(
            user=user,
            total_1rm=150
        )
        assert profile1.get_strength_level() == '初学者'
        
        # 测试进阶者
        profile2 = FitnessProfile.objects.create(
            user=user,
            total_1rm=300
        )
        assert profile2.get_strength_level() == '进阶者'
        
        # 测试中级者
        profile3 = FitnessProfile.objects.create(
            user=user,
            total_1rm=500
        )
        assert profile3.get_strength_level() == '中级者'
        
        # 测试高级者
        profile4 = FitnessProfile.objects.create(
            user=user,
            total_1rm=700
        )
        assert profile4.get_strength_level() == '高级者'
        
        # 测试专家级
        profile5 = FitnessProfile.objects.create(
            user=user,
            total_1rm=900
        )
        assert profile5.get_strength_level() == '专家级'
        
        # 测试未记录
        profile6 = FitnessProfile.objects.create(
            user=user,
            total_1rm=None
        )
        assert profile6.get_strength_level() == '未记录'
    
    def test_update_1rm_records(self, user):
        """测试更新1RM记录"""
        profile = FitnessProfile.objects.create(
            user=user,
            bodyweight=70.0
        )
        
        # 创建深蹲记录
        ExerciseWeightRecord.objects.create(
            user=user,
            exercise_type='squat',
            weight=80,
            reps=5,
            workout_date=timezone.now().date()
        )
        
        # 创建卧推记录
        ExerciseWeightRecord.objects.create(
            user=user,
            exercise_type='bench_press',
            weight=60,
            reps=5,
            workout_date=timezone.now().date()
        )
        
        # 创建硬拉记录
        ExerciseWeightRecord.objects.create(
            user=user,
            exercise_type='deadlift',
            weight=100,
            reps=5,
            workout_date=timezone.now().date()
        )
        
        # 更新1RM记录
        profile.update_1rm_records()
        
        # 验证1RM值已更新
        assert profile.squat_1rm is not None
        assert profile.bench_press_1rm is not None
        assert profile.deadlift_1rm is not None
        assert profile.total_1rm is not None
        assert profile.strength_coefficient is not None


@pytest.mark.django_db
class TestExerciseWeightRecord:
    """运动重量记录测试"""
    
    def test_create_exercise_record(self, user):
        """测试创建运动记录"""
        record = ExerciseWeightRecord.objects.create(
            user=user,
            exercise_type='squat',
            weight=80,
            reps=5,
            workout_date=timezone.now().date()
        )
        assert record.user == user
        assert record.exercise_type == 'squat'
        assert record.weight == 80
        assert record.reps == 5
    
    def test_get_estimated_1rm(self, user):
        """测试估算1RM"""
        record = ExerciseWeightRecord.objects.create(
            user=user,
            exercise_type='squat',
            weight=80,
            reps=5,
            workout_date=timezone.now().date()
        )
        
        estimated_1rm = record.get_estimated_1rm()
        assert estimated_1rm > 80  # 1RM应该大于5RM重量


@pytest.mark.django_db
class TestChatRoom:
    """聊天室测试"""
    
    def test_create_chat_room(self, user):
        """测试创建聊天室"""
        room = ChatRoom.objects.create(
            name='测试聊天室',
            creator=user,
            max_participants=10
        )
        assert room.name == '测试聊天室'
        assert room.creator == user
        assert room.max_participants == 10
        assert room.status == 'active'
    
    def test_join_chat_room(self, user):
        """测试加入聊天室"""
        room = ChatRoom.objects.create(
            name='测试聊天室',
            creator=user,
            max_participants=10
        )
        
        # 测试加入聊天室
        success = room.join_room(user)
        assert success is True
        assert user in room.participants.all()
    
    def test_leave_chat_room(self, user):
        """测试离开聊天室"""
        room = ChatRoom.objects.create(
            name='测试聊天室',
            creator=user,
            max_participants=10
        )
        room.join_room(user)
        
        # 测试离开聊天室
        success = room.leave_room(user)
        assert success is True
        assert user not in room.participants.all()


@pytest.mark.django_db
class TestLifeGoal:
    """生活目标测试"""
    
    def test_create_life_goal(self, user):
        """测试创建生活目标"""
        goal = LifeGoal.objects.create(
            user=user,
            title='学习Python',
            description='掌握Python编程基础',
            category='learning',
            target_date=timezone.now().date() + timedelta(days=30),
            priority='high'
        )
        assert goal.user == user
        assert goal.title == '学习Python'
        assert goal.category == 'learning'
        assert goal.priority == 'high'
    
    def test_get_progress_percentage(self, user):
        """测试目标进度百分比"""
        goal = LifeGoal.objects.create(
            user=user,
            title='学习Python',
            description='掌握Python编程基础',
            category='learning',
            target_date=timezone.now().date() + timedelta(days=30),
            priority='high',
            progress=75
        )
        
        progress = goal.get_progress_percentage()
        assert progress == 75


@pytest.mark.django_db
class TestFitnessWorkoutSession:
    """健身训练会话测试"""
    
    def test_create_workout_session(self, user):
        """测试创建训练会话"""
        session = FitnessWorkoutSession.objects.create(
            user=user,
            workout_date=timezone.now().date(),
            duration_minutes=60,
            workout_type='strength',
            notes='测试训练'
        )
        assert session.user == user
        assert session.duration_minutes == 60
        assert session.workout_type == 'strength'
    
    def test_calculate_calories_burned(self, user):
        """测试计算消耗卡路里"""
        session = FitnessWorkoutSession.objects.create(
            user=user,
            workout_date=timezone.now().date(),
            duration_minutes=60,
            workout_type='strength',
            intensity='moderate'
        )
        
        calories = session.calculate_calories_burned()
        assert calories > 0


@pytest.mark.django_db
class TestTravelGuide:
    """旅行指南测试"""
    
    def test_create_travel_guide(self, user):
        """测试创建旅行指南"""
        guide = TravelGuide.objects.create(
            user=user,
            destination='北京',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=7),
            budget=5000,
            travel_style='budget'
        )
        assert guide.user == user
        assert guide.destination == '北京'
        assert guide.budget == 5000
        assert guide.travel_style == 'budget'
    
    def test_generate_itinerary(self, user):
        """测试生成行程"""
        guide = TravelGuide.objects.create(
            user=user,
            destination='北京',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=3),
            budget=3000,
            travel_style='budget'
        )
        
        itinerary = guide.generate_itinerary()
        assert itinerary is not None
        assert len(itinerary) > 0


@pytest.mark.performance
class TestModelPerformance:
    """模型性能测试"""
    
    def test_bulk_create_performance(self, user_factory):
        """测试批量创建性能"""
        users = user_factory.create_batch(100)
        
        # 批量创建工具使用日志
        logs = []
        for user in users:
            logs.append(ToolUsageLog(
                user=user,
                tool_type='TEST_CASE',
                input_data='test',
                output_file='test.txt'
            ))
        
        # 测量批量创建时间
        import time
        start_time = time.time()
        ToolUsageLog.objects.bulk_create(logs)
        end_time = time.time()
        
        # 批量创建应该比逐个创建快
        assert end_time - start_time < 1.0  # 应该在1秒内完成
    
    def test_query_performance(self, user):
        """测试查询性能"""
        # 创建大量测试数据
        logs = []
        for i in range(1000):
            logs.append(ToolUsageLog(
                user=user,
                tool_type='TEST_CASE',
                input_data=f'test{i}',
                output_file=f'test{i}.txt'
            ))
        ToolUsageLog.objects.bulk_create(logs)
        
        # 测试查询性能
        import time
        start_time = time.time()
        result = ToolUsageLog.objects.filter(user=user).count()
        end_time = time.time()
        
        assert result == 1000
        assert end_time - start_time < 0.1  # 查询应该在0.1秒内完成
