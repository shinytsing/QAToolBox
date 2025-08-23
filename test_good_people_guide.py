#!/usr/bin/env python3
"""
好心人攻略功能测试脚本
用于测试WanderAI好心人攻略的各项功能
"""

import requests
import json
import os
from datetime import datetime

class GoodPeopleGuideTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, data=None):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   错误详情: {data}")
        print()
    
    def test_get_guides_list(self):
        """测试获取攻略列表"""
        try:
            url = f"{self.base_url}/tools/api/user_generated_travel_guide/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    guides_count = len(data.get('guides', []))
                    self.log_test(
                        "获取攻略列表",
                        True,
                        f"成功获取到 {guides_count} 个攻略"
                    )
                else:
                    self.log_test(
                        "获取攻略列表",
                        False,
                        "API返回失败",
                        data.get('error')
                    )
            else:
                self.log_test(
                    "获取攻略列表",
                    False,
                    f"HTTP状态码错误: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "获取攻略列表",
                False,
                f"请求异常: {str(e)}"
            )
    
    def test_create_guide(self):
        """测试创建攻略"""
        try:
            url = f"{self.base_url}/tools/api/user_generated_travel_guide/"
            
            # 准备测试数据
            test_data = {
                'title': f'测试攻略 - {datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'destination': '北京',
                'travel_style': 'cultural',
                'budget_range': 'medium',
                'travel_duration': '3-5天',
                'interests': json.dumps(['文化', '历史', '美食']),
                'summary': '这是一个自动化测试创建的攻略',
                'content': '''
# 北京3日游测试攻略

## 第一天：故宫 + 天安门广场
- 上午：游览故宫博物院
- 下午：天安门广场 + 国家博物馆
- 晚上：王府井步行街

## 第二天：长城 + 颐和园
- 上午：八达岭长城
- 下午：颐和园
- 晚上：后海酒吧街

## 第三天：胡同 + 购物
- 上午：南锣鼓巷胡同游
- 下午：三里屯购物
- 晚上：鸟巢水立方夜景

## 美食推荐
- 全聚德烤鸭
- 老北京炸酱面
- 东来顺涮羊肉

## 交通建议
- 地铁为主
- 打车为辅
- 共享单车短途

## 预算明细
- 住宿：300元/晚
- 餐饮：150元/天
- 交通：50元/天
- 门票：200元
- 总计：约1200元
                '''
            }
            
            response = self.session.post(url, data=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    guide_id = data.get('guide_id')
                    self.log_test(
                        "创建攻略",
                        True,
                        f"成功创建攻略，ID: {guide_id}"
                    )
                    return guide_id
                else:
                    self.log_test(
                        "创建攻略",
                        False,
                        "API返回失败",
                        data.get('error')
                    )
            else:
                self.log_test(
                    "创建攻略",
                    False,
                    f"HTTP状态码错误: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "创建攻略",
                False,
                f"请求异常: {str(e)}"
            )
        return None
    
    def test_get_guide_detail(self, guide_id):
        """测试获取攻略详情"""
        if not guide_id:
            self.log_test("获取攻略详情", False, "缺少攻略ID")
            return
        
        try:
            url = f"{self.base_url}/tools/api/user_generated_travel_guide/{guide_id}/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    guide = data.get('guide', {})
                    self.log_test(
                        "获取攻略详情",
                        True,
                        f"成功获取攻略: {guide.get('title', '未知标题')}"
                    )
                else:
                    self.log_test(
                        "获取攻略详情",
                        False,
                        "API返回失败",
                        data.get('error')
                    )
            else:
                self.log_test(
                    "获取攻略详情",
                    False,
                    f"HTTP状态码错误: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "获取攻略详情",
                False,
                f"请求异常: {str(e)}"
            )
    
    def test_use_guide(self, guide_id):
        """测试使用攻略"""
        if not guide_id:
            self.log_test("使用攻略", False, "缺少攻略ID")
            return
        
        try:
            url = f"{self.base_url}/tools/api/user_generated_travel_guide/{guide_id}/use/"
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': self.get_csrf_token()
            }
            
            response = self.session.post(url, headers=headers, json={})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "使用攻略",
                        True,
                        "成功使用攻略"
                    )
                else:
                    self.log_test(
                        "使用攻略",
                        False,
                        "API返回失败",
                        data.get('error')
                    )
            else:
                self.log_test(
                    "使用攻略",
                    False,
                    f"HTTP状态码错误: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "使用攻略",
                False,
                f"请求异常: {str(e)}"
            )
    
    def test_search_guides(self):
        """测试搜索攻略"""
        try:
            url = f"{self.base_url}/tools/api/user_generated_travel_guide/"
            params = {
                'destination': '北京',
                'travel_style': 'cultural'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    guides_count = len(data.get('guides', []))
                    self.log_test(
                        "搜索攻略",
                        True,
                        f"成功搜索到 {guides_count} 个北京文化型攻略"
                    )
                else:
                    self.log_test(
                        "搜索攻略",
                        False,
                        "API返回失败",
                        data.get('error')
                    )
            else:
                self.log_test(
                    "搜索攻略",
                    False,
                    f"HTTP状态码错误: {response.status_code}"
                )
        except Exception as e:
            self.log_test(
                "搜索攻略",
                False,
                f"请求异常: {str(e)}"
            )
    
    def get_csrf_token(self):
        """获取CSRF Token（简化版本）"""
        try:
            # 获取登录页面来获取CSRF Token
            response = self.session.get(f"{self.base_url}/users/login/")
            if response.status_code == 200:
                # 这里需要根据实际的CSRF Token获取方式来实现
                # 简化处理，返回空字符串
                return ""
        except:
            pass
        return ""
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🤝 开始好心人攻略功能测试")
        print("=" * 50)
        
        # 1. 测试获取攻略列表
        self.test_get_guides_list()
        
        # 2. 测试创建攻略
        guide_id = self.test_create_guide()
        
        # 3. 测试获取攻略详情
        self.test_get_guide_detail(guide_id)
        
        # 4. 测试使用攻略
        self.test_use_guide(guide_id)
        
        # 5. 测试搜索攻略
        self.test_search_guides()
        
        # 输出测试总结
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("=" * 50)
        print("📊 测试总结")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        # 保存测试结果到文件
        self.save_results()
    
    def save_results(self):
        """保存测试结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"good_people_guide_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试结果已保存到: {filename}")
        except Exception as e:
            print(f"\n⚠️ 保存测试结果失败: {str(e)}")

def main():
    """主函数"""
    import sys
    
    # 获取服务器地址
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🚀 连接到服务器: {base_url}")
    print("注意: 请确保服务器正在运行并且好心人攻略功能已启用")
    print()
    
    # 创建测试器并运行测试
    tester = GoodPeopleGuideTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
