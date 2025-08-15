#!/usr/bin/env python3
"""
DeepSeek图像识别功能测试脚本
"""

import os
import sys
import django
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def test_deepseek_image_recognition():
    """测试DeepSeek图像识别功能"""
    print("🧪 开始测试DeepSeek图像识别功能...")
    
    try:
        from apps.tools.services.deepseek_image_recognition import DeepSeekImageRecognition
        
        # 检查API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            print("❌ DEEPSEEK_API_KEY 未配置")
            print("请在 .env 文件中设置 DEEPSEEK_API_KEY=your_api_key")
            return False
        
        print(f"✅ DeepSeek API密钥已配置: {api_key[:10]}...")
        
        # 创建识别服务
        recognition_service = DeepSeekImageRecognition()
        print("✅ DeepSeek图像识别服务初始化成功")
        
        # 测试图像路径
        test_image_path = "static/img/food/beef-4805622_1280.jpg"
        
        if not os.path.exists(test_image_path):
            print(f"❌ 测试图像不存在: {test_image_path}")
            print("请确保测试图像文件存在")
            return False
        
        print(f"✅ 找到测试图像: {test_image_path}")
        
        # 进行图像识别
        print("🔄 开始图像识别...")
        result = recognition_service.recognize_food_image(test_image_path)
        
        print("\n📊 识别结果:")
        print(f"  成功: {result['success']}")
        print(f"  识别食品: {result.get('recognized_food', 'N/A')}")
        print(f"  置信度: {result.get('confidence', 0.0)}")
        print(f"  描述: {result.get('description', 'N/A')}")
        print(f"  营养信息: {result.get('nutrition_info', {})}")
        print(f"  相似食品: {result.get('similar_foods', [])}")
        
        if result['success']:
            print("\n🎉 DeepSeek图像识别测试成功！")
            
            # 测试食品建议功能
            print("\n🔄 测试食品建议功能...")
            suggestions = recognition_service.get_food_suggestions(
                result['recognized_food'],
                result['nutrition_info']
            )
            
            print(f"✅ 获取到 {len(suggestions)} 类建议:")
            for suggestion in suggestions:
                print(f"  - {suggestion['title']}: {suggestion['items']}")
            
            return True
        else:
            print(f"\n❌ 图像识别失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_recognition():
    """测试批量识别功能"""
    print("\n🧪 测试批量识别功能...")
    
    try:
        from apps.tools.services.deepseek_image_recognition import DeepSeekImageRecognition
        
        recognition_service = DeepSeekImageRecognition()
        
        # 查找测试图像
        test_images = []
        food_img_dir = "static/img/food"
        
        if os.path.exists(food_img_dir):
            for file in os.listdir(food_img_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    test_images.append(os.path.join(food_img_dir, file))
        
        if not test_images:
            print("❌ 没有找到测试图像")
            return False
        
        # 限制测试数量
        test_images = test_images[:3]
        print(f"✅ 找到 {len(test_images)} 张测试图像")
        
        # 批量识别
        results = recognition_service.batch_recognize(test_images)
        
        print(f"\n📊 批量识别结果 ({len(results)} 张图像):")
        for i, result in enumerate(results):
            image_path = result['image_path']
            recognition_result = result['result']
            
            print(f"\n  图像 {i+1}: {os.path.basename(image_path)}")
            print(f"    成功: {recognition_result['success']}")
            print(f"    识别食品: {recognition_result.get('recognized_food', 'N/A')}")
            print(f"    置信度: {recognition_result.get('confidence', 0.0)}")
        
        success_count = sum(1 for r in results if r['result']['success'])
        print(f"\n✅ 批量识别完成: {success_count}/{len(results)} 张图像识别成功")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ 批量识别测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 DeepSeek图像识别功能测试")
    print("=" * 50)
    
    # 测试基本识别功能
    basic_test_passed = test_deepseek_image_recognition()
    
    # 测试批量识别功能
    batch_test_passed = test_batch_recognition()
    
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    print(f"  基本识别功能: {'✅ 通过' if basic_test_passed else '❌ 失败'}")
    print(f"  批量识别功能: {'✅ 通过' if batch_test_passed else '❌ 失败'}")
    
    if basic_test_passed and batch_test_passed:
        print("\n🎉 所有测试通过！DeepSeek图像识别功能正常工作")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查配置和网络连接")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
