from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.tools.models import FoodItem
import json


class Command(BaseCommand):
    help = '初始化食物数据用于照片绑定功能'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始初始化食物数据...'))
        
        # 中餐食物数据
        chinese_foods = [
            {'name': '麻婆豆腐', 'cuisine': 'chinese', 'tags': ['川菜', '豆腐', '辣', '下饭菜']},
            {'name': '宫保鸡丁', 'cuisine': 'chinese', 'tags': ['川菜', '鸡肉', '花生', '辣']},
            {'name': '红烧肉', 'cuisine': 'chinese', 'tags': ['江浙菜', '猪肉', '甜', '红烧']},
            {'name': '糖醋里脊', 'cuisine': 'chinese', 'tags': ['鲁菜', '猪肉', '酸甜', '炸']},
            {'name': '鱼香肉丝', 'cuisine': 'chinese', 'tags': ['川菜', '猪肉', '下饭菜', '辣']},
            {'name': '青椒肉丝', 'cuisine': 'chinese', 'tags': ['家常菜', '猪肉', '青椒', '炒']},
            {'name': '番茄炒蛋', 'cuisine': 'chinese', 'tags': ['家常菜', '鸡蛋', '番茄', '酸甜']},
            {'name': '白切鸡', 'cuisine': 'chinese', 'tags': ['粤菜', '鸡肉', '清淡', '蒸']},
            {'name': '北京烤鸭', 'cuisine': 'chinese', 'tags': ['京菜', '鸭肉', '烤', '名菜']},
            {'name': '东坡肉', 'cuisine': 'chinese', 'tags': ['江浙菜', '猪肉', '红烧', '甜']},
            {'name': '炸酱面', 'cuisine': 'chinese', 'tags': ['京菜', '面条', '豆瓣酱', '主食']},
            {'name': '蛋炒饭', 'cuisine': 'chinese', 'tags': ['家常菜', '米饭', '鸡蛋', '主食']},
            {'name': '叉烧肉', 'cuisine': 'chinese', 'tags': ['粤菜', '猪肉', '烤', '甜']},
            {'name': '烧鹅', 'cuisine': 'chinese', 'tags': ['粤菜', '鹅肉', '烤', '脆皮']},
            {'name': '水煮鱼', 'cuisine': 'chinese', 'tags': ['川菜', '鱼肉', '辣', '麻']},
            {'name': '火锅', 'cuisine': 'chinese', 'tags': ['川菜', '涮菜', '辣', '聚餐']},
            {'name': '小龙虾', 'cuisine': 'chinese', 'tags': ['湘菜', '虾类', '辣', '夜宵']},
            {'name': '剁椒鱼头', 'cuisine': 'chinese', 'tags': ['湘菜', '鱼头', '辣', '蒸']},
            {'name': '回锅肉', 'cuisine': 'chinese', 'tags': ['川菜', '猪肉', '豆瓣酱', '辣']},
            {'name': '麻辣香锅', 'cuisine': 'chinese', 'tags': ['川菜', '混合', '辣', '麻']},
        ]
        
        # 西餐食物数据
        western_foods = [
            {'name': '意大利面', 'cuisine': 'western', 'tags': ['意式', '面条', '番茄', '主食']},
            {'name': '披萨', 'cuisine': 'western', 'tags': ['意式', '芝士', '烤', '快餐']},
            {'name': '汉堡包', 'cuisine': 'western', 'tags': ['美式', '牛肉', '面包', '快餐']},
            {'name': '牛排', 'cuisine': 'western', 'tags': ['西式', '牛肉', '煎', '高档']},
            {'name': '沙拉', 'cuisine': 'western', 'tags': ['西式', '蔬菜', '健康', '轻食']},
            {'name': '土豆泥', 'cuisine': 'western', 'tags': ['西式', '土豆', '奶香', '配菜']},
            {'name': '炸鸡', 'cuisine': 'western', 'tags': ['美式', '鸡肉', '炸', '快餐']},
            {'name': '三明治', 'cuisine': 'western', 'tags': ['西式', '面包', '简餐', '便当']},
        ]
        
        # 日料食物数据
        japanese_foods = [
            {'name': '寿司', 'cuisine': 'japanese', 'tags': ['日式', '鱼肉', '米饭', '生食']},
            {'name': '拉面', 'cuisine': 'japanese', 'tags': ['日式', '面条', '汤', '主食']},
            {'name': '天妇罗', 'cuisine': 'japanese', 'tags': ['日式', '炸物', '虾', '蔬菜']},
            {'name': '刺身', 'cuisine': 'japanese', 'tags': ['日式', '鱼肉', '生食', '新鲜']},
            {'name': '乌冬面', 'cuisine': 'japanese', 'tags': ['日式', '面条', '汤', '主食']},
            {'name': '章鱼小丸子', 'cuisine': 'japanese', 'tags': ['日式', '章鱼', '小食', '街头']},
            {'name': '日式烤肉', 'cuisine': 'japanese', 'tags': ['日式', '牛肉', '烤', '聚餐']},
        ]
        
        # 韩料食物数据
        korean_foods = [
            {'name': '韩式烤肉', 'cuisine': 'korean', 'tags': ['韩式', '牛肉', '烤', '聚餐']},
            {'name': '泡菜', 'cuisine': 'korean', 'tags': ['韩式', '白菜', '发酵', '配菜']},
            {'name': '石锅拌饭', 'cuisine': 'korean', 'tags': ['韩式', '米饭', '蔬菜', '主食']},
            {'name': '年糕', 'cuisine': 'korean', 'tags': ['韩式', '年糕', '辣', '小食']},
            {'name': '韩式炸鸡', 'cuisine': 'korean', 'tags': ['韩式', '鸡肉', '炸', '甜辣']},
            {'name': '部队锅', 'cuisine': 'korean', 'tags': ['韩式', '火锅', '辣', '混合']},
            {'name': '冷面', 'cuisine': 'korean', 'tags': ['韩式', '面条', '冷食', '夏日']},
        ]
        
        # 合并所有食物数据
        all_foods = chinese_foods + western_foods + japanese_foods + korean_foods
        
        created_count = 0
        updated_count = 0
        
        for food_data in all_foods:
            food_item, created = FoodItem.objects.get_or_create(
                name=food_data['name'],
                cuisine=food_data['cuisine'],
                defaults={
                    'description': f"美味的{food_data['name']}",
                    'meal_types': ['lunch', 'dinner'],
                    'tags': food_data['tags'],
                    'difficulty': 'medium',
                    'cooking_time': 30,
                    'ingredients': [],
                    'popularity_score': 5.0,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'创建食物: {food_item.name}')
            else:
                # 更新标签
                food_item.tags = food_data['tags']
                food_item.save()
                updated_count += 1
                self.stdout.write(f'更新食物: {food_item.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'食物数据初始化完成！'
                f'创建了 {created_count} 个新食物，'
                f'更新了 {updated_count} 个现有食物。'
                f'总共 {len(all_foods)} 个食物。'
            )
        )
