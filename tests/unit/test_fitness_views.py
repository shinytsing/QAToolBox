import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta

from api.v1.fitness.models import FitnessProfile, FitnessWorkout, FitnessAchievement

User = get_user_model()

class FitnessViewsTestCase(APITestCase):
    """健身视图测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建健身资料
        self.fitness_profile = FitnessProfile.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            age=25,
            gender='male',
            activity_level='moderate'
        )
        
        # 创建训练记录
        self.workout = FitnessWorkout.objects.create(
            user=self.user,
            name='测试训练',
            workout_type='strength',
            duration=60,
            calories_burned=300,
            notes='测试训练记录'
        )
        
        # 创建成就记录
        self.achievement = FitnessAchievement.objects.create(
            user=self.user,
            title='首次训练',
            description='完成第一次训练',
            achievement_type='milestone',
            points=10
        )
    
    def get_auth_headers(self):
        """获取认证头"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        return {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}
    
    def test_get_fitness_profile(self):
        """测试获取健身资料"""
        response = self.client.get('/api/v1/fitness/profile/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['height'], 175.0)
        self.assertEqual(response.data['data']['weight'], 70.0)
    
    def test_update_fitness_profile(self):
        """测试更新健身资料"""
        update_data = {
            'height': 180.0,
            'weight': 75.0,
            'age': 26,
            'activity_level': 'high'
        }
        
        response = self.client.put('/api/v1/fitness/profile/', update_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证更新
        self.fitness_profile.refresh_from_db()
        self.assertEqual(self.fitness_profile.height, 180.0)
        self.assertEqual(self.fitness_profile.weight, 75.0)
    
    def test_create_workout(self):
        """测试创建训练记录"""
        workout_data = {
            'name': '新训练',
            'workout_type': 'cardio',
            'duration': 45,
            'calories_burned': 250,
            'notes': '有氧训练'
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', workout_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], '新训练')
    
    def test_get_workouts_list(self):
        """测试获取训练记录列表"""
        response = self.client.get('/api/v1/fitness/workouts/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '测试训练')
    
    def test_get_workout_detail(self):
        """测试获取训练记录详情"""
        response = self.client.get(f'/api/v1/fitness/workouts/{self.workout.id}/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], '测试训练')
    
    def test_update_workout(self):
        """测试更新训练记录"""
        update_data = {
            'name': '更新训练',
            'duration': 90,
            'calories_burned': 400
        }
        
        response = self.client.put(f'/api/v1/fitness/workouts/{self.workout.id}/', update_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证更新
        self.workout.refresh_from_db()
        self.assertEqual(self.workout.name, '更新训练')
        self.assertEqual(self.workout.duration, 90)
    
    def test_delete_workout(self):
        """测试删除训练记录"""
        response = self.client.delete(f'/api/v1/fitness/workouts/{self.workout.id}/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 验证删除
        self.assertFalse(FitnessWorkout.objects.filter(id=self.workout.id).exists())
    
    def test_get_achievements_list(self):
        """测试获取成就列表"""
        response = self.client.get('/api/v1/fitness/achievements/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['title'], '首次训练')
    
    def test_create_achievement(self):
        """测试创建成就"""
        achievement_data = {
            'title': '新成就',
            'description': '完成新成就',
            'achievement_type': 'streak',
            'points': 20
        }
        
        response = self.client.post('/api/v1/fitness/achievements/', achievement_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['title'], '新成就')
    
    def test_get_workout_stats(self):
        """测试获取训练统计"""
        response = self.client.get('/api/v1/fitness/workouts/stats/', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('total_workouts', response.data['data'])
        self.assertIn('total_duration', response.data['data'])
        self.assertIn('total_calories', response.data['data'])
    
    def test_get_workouts_by_date_range(self):
        """测试按日期范围获取训练记录"""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/v1/fitness/workouts/?start_date={start_date}&end_date={end_date}',
            **self.get_auth_headers()
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_get_workouts_by_type(self):
        """测试按类型获取训练记录"""
        response = self.client.get('/api/v1/fitness/workouts/?workout_type=strength', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        response = self.client.get('/api/v1/fitness/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_workout_validation(self):
        """测试训练记录验证"""
        invalid_data = {
            'name': '',  # 空名称
            'workout_type': 'invalid_type',  # 无效类型
            'duration': -10,  # 负数时长
            'calories_burned': 'invalid'  # 无效卡路里
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', invalid_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_achievement_validation(self):
        """测试成就验证"""
        invalid_data = {
            'title': '',  # 空标题
            'achievement_type': 'invalid_type',  # 无效类型
            'points': -5  # 负数积分
        }
        
        response = self.client.post('/api/v1/fitness/achievements/', invalid_data, **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_pagination(self):
        """测试分页"""
        # 创建多个训练记录
        for i in range(15):
            FitnessWorkout.objects.create(
                user=self.user,
                name=f'训练 {i}',
                workout_type='strength',
                duration=60,
                calories_burned=300
            )
        
        response = self.client.get('/api/v1/fitness/workouts/?page=1&page_size=10', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 10)
        self.assertIn('pagination', response.data)
    
    def test_workout_search(self):
        """测试训练记录搜索"""
        response = self.client.get('/api/v1/fitness/workouts/?search=测试', **self.get_auth_headers())
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '测试训练')
