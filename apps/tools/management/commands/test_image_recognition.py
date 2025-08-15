from django.core.management.base import BaseCommand
from apps.tools.services.food_image_mapping import (
    recognize_food_from_image, 
    get_food_suggestions_by_image
)
import tempfile
import os


class Command(BaseCommand):
    help = '测试图像识别功能'

    def handle(self, *args, **options):
        self.stdout.write('🧪 开始测试图像识别功能...')
        
        # 测试不同的图片文件名
        test_images = [
            'chicken_dish.jpg',
            'pork_braised.jpg', 
            'beef_steak.jpg',
            'fish_steamed.jpg',
            'noodle_stir_fry.jpg',
            'rice_fried.jpg',
            'bread_sandwich.jpg',
            'pizza_margherita.jpg',
            'pasta_carbonara.jpg',
            'salad_green.jpg',
            'tofu_mapo.jpg',
            'duck_roasted.jpg',
            'shrimp_boiled.jpg',
            'hotpot_spicy.jpg',
            'bbq_grilled.jpg',
            'unknown_food.jpg'
        ]
        
        for i, image_name in enumerate(test_images, 1):
            self.stdout.write(f'\n📸 测试 {i}: {image_name}')
            
            # 创建临时文件路径
            temp_path = os.path.join(tempfile.gettempdir(), image_name)
            
            # 测试识别功能
            recognition_result = recognize_food_from_image(temp_path)
            
            self.stdout.write(f'   识别结果: {recognition_result["food_name"]}')
            self.stdout.write(f'   置信度: {recognition_result["confidence"]:.2f}')
            
            if recognition_result["alternatives"]:
                self.stdout.write(f'   替代选项: {[alt["name"] for alt in recognition_result["alternatives"]]}')
            
            # 测试建议功能
            suggestions = get_food_suggestions_by_image(temp_path)
            self.stdout.write(f'   相似建议: {suggestions}')
        
        self.stdout.write('\n✅ 图像识别功能测试完成!')
        self.stdout.write('\n📋 功能说明:')
        self.stdout.write('   - 基于文件名进行智能识别')
        self.stdout.write('   - 提供置信度和替代选项')
        self.stdout.write('   - 生成相似食品建议')
        self.stdout.write('   - 支持跳转到食物随机器')
