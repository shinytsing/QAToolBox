#!/usr/bin/env python
"""
主题快捷键切换功能测试脚本
用于验证快捷键切换主题时模板是否正确更新
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class ThemeShortcutTester:
    """主题快捷键测试器"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:8000"
        self.test_results = []
    
    def setup_driver(self):
        """设置WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ WebDriver设置成功")
            return True
        except Exception as e:
            print(f"❌ WebDriver设置失败: {e}")
            return False
    
    def test_shortcut_keys(self):
        """测试快捷键功能"""
        print("\n🔧 开始测试快捷键切换功能...")
        
        test_pages = [
            "/",
            "/tools/emo-diary/",
            "/tools/life-diary/",
            "/tools/fitness-center/",
            "/tools/creative-writer/"
        ]
        
        for page in test_pages:
            print(f"\n📄 测试页面: {page}")
            self.test_page_shortcuts(page)
        
        self.print_test_summary()
    
    def test_page_shortcuts(self, page_path):
        """测试单个页面的快捷键"""
        try:
            # 访问页面
            url = self.base_url + page_path
            self.driver.get(url)
            time.sleep(2)
            
            # 获取初始主题
            initial_theme = self.get_current_theme()
            print(f"   初始主题: {initial_theme}")
            
            # 测试快捷键切换
            shortcuts = [
                (Keys.CONTROL + "1", "life", "生活模式"),
                (Keys.CONTROL + "2", "work", "极客模式"),
                (Keys.CONTROL + "3", "training", "狂暴模式"),
                (Keys.CONTROL + "4", "emo", "Emo模式")
            ]
            
            for shortcut, expected_theme, theme_name in shortcuts:
                # 发送快捷键
                self.driver.find_element(By.TAG_NAME, "body").send_keys(shortcut)
                time.sleep(1)
                
                # 检查主题是否切换
                current_theme = self.get_current_theme()
                success = current_theme == expected_theme
                
                result = {
                    "page": page_path,
                    "shortcut": shortcut,
                    "expected": expected_theme,
                    "actual": current_theme,
                    "success": success,
                    "theme_name": theme_name
                }
                
                self.test_results.append(result)
                
                status = "✅" if success else "❌"
                print(f"   {status} {shortcut} -> {theme_name}: {current_theme}")
                
                # 等待一下再测试下一个快捷键
                time.sleep(0.5)
        
        except Exception as e:
            print(f"   ❌ 页面测试失败: {e}")
            self.test_results.append({
                "page": page_path,
                "error": str(e),
                "success": False
            })
    
    def get_current_theme(self):
        """获取当前主题"""
        try:
            # 检查body类名
            body_class = self.driver.find_element(By.TAG_NAME, "body").get_attribute("class")
            
            # 检查CSS文件
            theme_css = self.driver.find_element(By.ID, "dynamic-theme-css").get_attribute("href")
            
            # 检查页面标题
            page_title = self.driver.title
            
            # 根据CSS文件判断主题
            if "geek.css" in theme_css:
                return "work"
            elif "life.css" in theme_css:
                return "life"
            elif "rage.css" in theme_css:
                return "training"
            elif "emo.css" in theme_css:
                return "emo"
            else:
                return "unknown"
        
        except Exception as e:
            print(f"   获取主题失败: {e}")
            return "error"
    
    def test_template_updates(self):
        """测试模板更新"""
        print("\n🎨 测试模板更新功能...")
        
        try:
            # 访问emo日记页面
            self.driver.get(self.base_url + "/tools/emo-diary/")
            time.sleep(2)
            
            # 检查初始模板元素
            initial_elements = self.get_template_elements()
            print(f"   初始模板元素: {len(initial_elements)} 个")
            
            # 切换到不同主题并检查模板更新
            themes = ["life", "work", "training", "emo"]
            
            for theme in themes:
                # 发送快捷键
                shortcut = Keys.CONTROL + str(themes.index(theme) + 1)
                self.driver.find_element(By.TAG_NAME, "body").send_keys(shortcut)
                time.sleep(1)
                
                # 检查模板是否更新
                updated_elements = self.get_template_elements()
                template_updated = len(updated_elements) > 0
                
                status = "✅" if template_updated else "❌"
                print(f"   {status} {theme}模式模板更新: {len(updated_elements)} 个元素")
        
        except Exception as e:
            print(f"   ❌ 模板更新测试失败: {e}")
    
    def get_template_elements(self):
        """获取模板相关元素"""
        try:
            elements = []
            
            # 检查容器元素
            containers = self.driver.find_elements(By.CSS_SELECTOR, 
                ".emo-diary-container, .geek-diary-container, .life-diary-container, .training-diary-container")
            elements.extend(containers)
            
            # 检查标题元素
            titles = self.driver.find_elements(By.CSS_SELECTOR, ".page-title")
            elements.extend(titles)
            
            # 检查提示文本
            hints = self.driver.find_elements(By.CSS_SELECTOR, ".hint-text")
            elements.extend(hints)
            
            return elements
        
        except Exception as e:
            print(f"   获取模板元素失败: {e}")
            return []
    
    def test_shortcut_indicators(self):
        """测试快捷键提示"""
        print("\n⌨️ 测试快捷键提示...")
        
        try:
            # 访问主页
            self.driver.get(self.base_url + "/")
            time.sleep(2)
            
            # 查找快捷键提示文本
            shortcut_texts = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'Ctrl+1/2/3/4') or contains(text(), '快捷键')]")
            
            if shortcut_texts:
                print(f"   ✅ 找到 {len(shortcut_texts)} 个快捷键提示")
                for text in shortcut_texts[:3]:  # 只显示前3个
                    print(f"      - {text.text[:50]}...")
            else:
                print("   ❌ 未找到快捷键提示")
        
        except Exception as e:
            print(f"   ❌ 快捷键提示测试失败: {e}")
    
    def print_test_summary(self):
        """打印测试总结"""
        print("\n📊 测试结果总结:")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # 显示失败的测试
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result.get("success", False):
                    if "error" in result:
                        print(f"   - {result['page']}: {result['error']}")
                    else:
                        print(f"   - {result['page']} {result['shortcut']}: "
                              f"期望 {result['expected']}, 实际 {result['actual']}")
        
        # 显示成功的测试
        if successful_tests > 0:
            print("\n✅ 成功的测试:")
            for result in self.test_results:
                if result.get("success", False):
                    print(f"   - {result['page']} {result['shortcut']}: {result['theme_name']}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始主题快捷键功能测试")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # 测试快捷键功能
            self.test_shortcut_keys()
            
            # 测试模板更新
            self.test_template_updates()
            
            # 测试快捷键提示
            self.test_shortcut_indicators()
            
            return True
        
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔚 测试完成，WebDriver已关闭")


def main():
    """主函数"""
    print("QAToolBox 主题快捷键功能测试")
    print("=" * 50)
    
    # 检查Django服务器是否运行
    import requests
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code != 200:
            print("❌ Django服务器未正常运行")
            return
    except:
        print("❌ 无法连接到Django服务器，请确保服务器正在运行")
        print("   运行命令: python manage.py runserver")
        return
    
    # 运行测试
    tester = ThemeShortcutTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试完成！")
    else:
        print("\n💥 测试过程中出现问题")


if __name__ == "__main__":
    main() 