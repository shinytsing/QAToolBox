#!/usr/bin/env python3
"""
DeepSeek图像识别功能演示脚本
"""

import os
import sys
import django
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def demo_single_recognition():
    """演示单张图像识别"""
    print("🎯 演示单张图像识别功能")
    print("=" * 50)
    
    try:
        from apps.tools.services.deepseek_image_recognition import DeepSeekImageRecognition
        
        # 创建识别服务
        recognition_service = DeepSeekImageRecognition()
        
        # 测试图像
        test_image = "static/img/food/beef-4805622_1280.jpg"
        
        if not os.path.exists(test_image):
            print(f"❌ 测试图像不存在: {test_image}")
            return False
        
        print(f"📸 识别图像: {os.path.basename(test_image)}")
        print("🔄 正在使用DeepSeek AI进行识别...")
        
        # 开始识别
        start_time = time.time()
        result = recognition_service.recognize_food_image(test_image)
        end_time = time.time()
        
        print(f"⏱️ 识别耗时: {end_time - start_time:.2f}秒")
        print()
        
        if result['success']:
            print("✅ 识别成功！")
            print(f"🍽️ 食品名称: {result['recognized_food']}")
            print(f"📊 置信度: {result['confidence']:.1%}")
            print(f"📝 描述: {result['description']}")
            
            # 显示营养信息
            nutrition = result['nutrition_info']
            if nutrition:
                print("\n🍎 营养信息:")
                print(f"  卡路里: {nutrition.get('calories', 'N/A')} kcal")
                print(f"  蛋白质: {nutrition.get('protein', 'N/A')} g")
                print(f"  脂肪: {nutrition.get('fat', 'N/A')} g")
                print(f"  碳水化合物: {nutrition.get('carbohydrates', 'N/A')} g")
            
            # 显示相似食品
            similar_foods = result['similar_foods']
            if similar_foods:
                print(f"\n🔗 相似食品: {', '.join(similar_foods)}")
            
            return True
        else:
            print(f"❌ 识别失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主演示函数"""
    print("🚀 DeepSeek图像识别功能演示")
    print("=" * 60)
    
    # 检查环境
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY 未配置")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY=your_api_key")
        return False
    
    print(f"✅ DeepSeek API密钥已配置: {api_key[:10]}...")
    print()
    
    # 演示单张图像识别
    single_success = demo_single_recognition()
    
    print("\n" + "=" * 60)
    print("📋 演示总结:")
    print(f"  单张识别: {'✅ 成功' if single_success else '❌ 失败'}")
    
    if single_success:
        print("\n🎉 DeepSeek图像识别功能演示成功！")
        print("\n💡 使用建议:")
        print("  1. 访问 http://localhost:8000/tools/food_image_recognition/")
        print("  2. 上传食品图片进行识别")
        print("  3. 查看详细的营养信息和智能建议")
        print("  4. 探索相似食品推荐")
        return True
    else:
        print("\n⚠️ 演示失败，请检查配置和网络连接")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
