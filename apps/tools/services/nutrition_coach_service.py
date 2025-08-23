# NutriCoach Pro服务已隐藏 - 此服务暂时停用
# 如需重新启用，请取消注释相关代码并在urls.py中重新启用路由

"""
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings


class NutritionCoachService:
    """健身营养定制引擎服务"""
    
    def __init__(self):
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.deepseek_api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
    
    def calculate_bmr(self, age: int, gender: str, weight: float, height: float) -> float:
        """计算基础代谢率 (Mifflin-St Jeor公式)"""
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """计算每日总能量消耗"""
        activity_factors = {
            'sedentary': 1.2,      # 久坐
            'light': 1.375,        # 轻度活动
            'moderate': 1.55,      # 中度活动
            'high': 1.725          # 重度活动
        }
        return bmr * activity_factors.get(activity_level, 1.2)
    
    def adjust_calories_for_goal(self, tdee: float, goal: str, intensity: str = 'balanced') -> float:
        """根据目标调整热量"""
        intensity_factors = {
            'conservative': 0.8,
            'balanced': 1.0,
            'aggressive': 1.2
        }
        
        if goal == 'lose_weight':
            deficit = 500 * intensity_factors.get(intensity, 1.0)
            return tdee - deficit
        elif goal == 'gain_muscle':
            surplus = 300 * intensity_factors.get(intensity, 1.0)
            return tdee + surplus
        else:
            return tdee
    
    def calculate_macros(self, calories: float, goal: str) -> Dict[str, float]:
        """计算宏量营养素分配"""
        if goal == 'gain_muscle':
            # 增肌：高蛋白，中等碳水，适量脂肪
            protein_ratio = 0.35
            carb_ratio = 0.45
            fat_ratio = 0.20
        elif goal == 'lose_weight':
            # 减脂：高蛋白，低碳水，中等脂肪
            protein_ratio = 0.40
            carb_ratio = 0.30
            fat_ratio = 0.30
        else:
            # 维持：均衡分配
            protein_ratio = 0.30
            carb_ratio = 0.40
            fat_ratio = 0.30
        
        # 计算具体克数（每克蛋白质/碳水=4kcal，脂肪=9kcal）
        protein_g = int((calories * protein_ratio) / 4)
        carb_g = int((calories * carb_ratio) / 4)
        fat_g = int((calories * fat_ratio) / 9)
        
        return {
            'protein': protein_g,
            'carbs': carb_g,
            'fat': fat_g
        }
    
    def generate_meal_plan_with_deepseek(self, user_data: Dict) -> Dict:
        """使用DeepSeek生成个性化饮食计划"""
        # 计算基础数据
        bmr = self.calculate_bmr(
            user_data['age'], 
            user_data['gender'], 
            user_data['weight'], 
            user_data['height']
        )
        tdee = self.calculate_tdee(bmr, user_data['activity_level'])
        calories = self.adjust_calories_for_goal(tdee, user_data['goal'], user_data.get('intensity', 'balanced'))
        macros = self.calculate_macros(calories, user_data['goal'])
        
        # 构建DeepSeek请求
        prompt = self._build_meal_plan_prompt(user_data, calories, macros)
        
        try:
            response = self._call_deepseek_api(prompt)
            meal_plan = self._parse_deepseek_response(response)
            
            return {
                'daily_calories': calories,
                'macros': macros,
                'meal_plan': meal_plan,
                'bmr': bmr,
                'tdee': tdee
            }
        except Exception as e:
            # 如果API调用失败，返回基础计划
            return self._generate_fallback_meal_plan(user_data, calories, macros)
    
    def _build_meal_plan_prompt(self, user_data: Dict, calories: float, macros: Dict) -> str:
        """构建DeepSeek提示词"""
        return f"""
请为以下健身用户生成一周的个性化饮食计划：

用户信息：
- 年龄：{user_data['age']}岁
- 性别：{user_data['gender']}
- 身高：{user_data['height']}cm
- 体重：{user_data['weight']}kg
- 健身目标：{user_data['goal']}
- 活动水平：{user_data['activity_level']}
- 饮食偏好：{user_data.get('dietary_preferences', [])}
- 过敏食物：{user_data.get('allergies', [])}

营养目标：
- 每日总热量：{calories}卡路里
- 蛋白质：{macros['protein']}g
- 碳水：{macros['carbs']}g
- 脂肪：{macros['fat']}g

请生成包含以下内容的7天饮食计划：
1. 每天3-4餐（早餐、午餐、晚餐、加餐）
2. 每餐的具体食材、分量和烹饪方法
3. 每餐的营养成分分析
4. 符合用户饮食偏好和过敏限制
5. 适合健身人群的食材选择

请以JSON格式返回，包含以下结构：
{{
    "week_plan": [
        {{
            "day": 1,
            "meals": [
                {{
                    "meal_type": "breakfast",
                    "name": "餐食名称",
                    "ingredients": ["食材1", "食材2"],
                    "instructions": "烹饪方法",
                    "nutrition": {{
                        "calories": 500,
                        "protein": 25,
                        "carbs": 60,
                        "fat": 15
                    }}
                }}
            ]
        }}
    ]
}}
"""
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        headers = {
            'Authorization': f'Bearer {self.deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的健身营养师，擅长为健身人群制定个性化饮食计划。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }
        
        response = requests.post(self.deepseek_api_url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_deepseek_response(self, response: str) -> List[Dict]:
        """解析DeepSeek响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            
            data = json.loads(json_str)
            return data.get('week_plan', [])
        except (json.JSONDecodeError, KeyError):
            # 如果解析失败，返回空计划
            return []
    
    def _generate_fallback_meal_plan(self, user_data: Dict, calories: float, macros: Dict) -> Dict:
        """生成备用饮食计划"""
        # 简化的备用计划
        daily_meals = [
            {
                'meal_type': 'breakfast',
                'name': '蛋白质燕麦粥',
                'ingredients': ['燕麦', '蛋白粉', '蓝莓', '坚果'],
                'nutrition': {
                    'calories': int(calories * 0.25),
                    'protein': int(macros['protein'] * 0.25),
                    'carbs': int(macros['carbs'] * 0.25),
                    'fat': int(macros['fat'] * 0.25)
                }
            },
            {
                'meal_type': 'lunch',
                'name': '鸡胸肉沙拉',
                'ingredients': ['鸡胸肉', '生菜', '番茄', '橄榄油'],
                'nutrition': {
                    'calories': int(calories * 0.35),
                    'protein': int(macros['protein'] * 0.35),
                    'carbs': int(macros['carbs'] * 0.35),
                    'fat': int(macros['fat'] * 0.35)
                }
            },
            {
                'meal_type': 'dinner',
                'name': '三文鱼配蔬菜',
                'ingredients': ['三文鱼', '西兰花', '红薯', '橄榄油'],
                'nutrition': {
                    'calories': int(calories * 0.30),
                    'protein': int(macros['protein'] * 0.30),
                    'carbs': int(macros['carbs'] * 0.30),
                    'fat': int(macros['fat'] * 0.30)
                }
            }
        ]
        
        week_plan = []
        for day in range(1, 8):
            week_plan.append({
                'day': day,
                'meals': daily_meals.copy()
            })
        
        return {
            'daily_calories': calories,
            'macros': macros,
            'meal_plan': week_plan
        }
    
    def generate_reminders(self, user_data: Dict, meal_plan: List[Dict]) -> List[Dict]:
        """生成营养提醒"""
        reminders = []
        
        # 基础用餐时间提醒
        meal_times = {
            'breakfast': '07:00',
            'lunch': '12:00',
            'dinner': '18:00',
            'snack': '15:00'
        }
        
        for meal_type, time in meal_times.items():
            reminders.append({
                'type': 'meal_time',
                'message': f'用餐时间到！记得记录您的{meal_type}',
                'trigger_time': time,
                'is_recurring': True
            })
        
        # 训练相关提醒
        if user_data.get('training_days_per_week', 0) > 0:
            reminders.extend([
                {
                    'type': 'pre_workout',
                    'message': '训练前2小时：建议补充碳水，如香蕉或燕麦',
                    'trigger_time': '16:00',  # 假设训练时间18:00
                    'is_recurring': True
                },
                {
                    'type': 'post_workout',
                    'message': '训练后30分钟内：及时补充蛋白质！',
                    'trigger_time': '18:30',
                    'is_recurring': True
                }
            ])
        
        # 水分补充提醒
        for hour in range(9, 21):
            reminders.append({
                'type': 'hydration',
                'message': f'记得补充水分！目标：每天2L水',
                'trigger_time': f'{hour:02d}:00',
                'is_recurring': True
            })
        
        return reminders
    
    def track_progress(self, user_data: Dict, current_weight: float, current_date: datetime) -> Dict:
        """追踪进度并调整计划"""
        # 这里可以添加进度分析逻辑
        # 比如计算体重变化、调整热量等
        
        return {
            'weight_change': 0,  # 需要历史数据计算
            'plan_adjustment_needed': False,
            'recommendations': []
        }
"""
