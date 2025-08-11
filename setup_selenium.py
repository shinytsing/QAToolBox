#!/usr/bin/env python3
"""
Selenium环境自动安装脚本
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(command, description=""):
    """运行命令并处理错误"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失败: {e.stderr}")
        return False


def check_python_package(package_name):
    """检查Python包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_python_packages():
    """安装Python依赖包"""
    print("\n" + "=" * 50)
    print("安装Python依赖包")
    print("=" * 50)
    
    packages = [
        ('selenium', 'selenium==4.20.0'),
        ('webdriver_manager', 'webdriver-manager==4.0.1'),
        ('requests', 'requests==2.32.4'),
        ('beautifulsoup4', 'beautifulsoup4==4.13.4')
    ]
    
    for package_name, package_spec in packages:
        if check_python_package(package_name):
            print(f"✓ {package_name} 已安装")
        else:
            print(f"正在安装 {package_name}...")
            if run_command(f"pip install {package_spec}", f"安装 {package_name}"):
                print(f"✓ {package_name} 安装成功")
            else:
                print(f"✗ {package_name} 安装失败")
                return False
    
    return True


def check_chrome_installation():
    """检查Chrome浏览器是否已安装"""
    print("\n" + "=" * 50)
    print("检查Chrome浏览器")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    elif system == "linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    elif system == "windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
    else:
        print(f"不支持的操作系统: {system}")
        return False
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ 找到Chrome浏览器: {path}")
            return True
    
    print("✗ 未找到Chrome浏览器")
    return False


def install_chrome():
    """安装Chrome浏览器"""
    print("\n" + "=" * 50)
    print("安装Chrome浏览器")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("在macOS上安装Chrome...")
        if run_command("brew --version", "检查Homebrew"):
            run_command("brew install --cask google-chrome", "安装Chrome")
        else:
            print("请先安装Homebrew: https://brew.sh/")
            print("然后运行: brew install --cask google-chrome")
            return False
    
    elif system == "linux":
        print("在Linux上安装Chrome...")
        # 检测Linux发行版
        if os.path.exists("/etc/debian_version"):
            # Debian/Ubuntu
            commands = [
                "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -",
                "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list",
                "sudo apt update",
                "sudo apt install -y google-chrome-stable"
            ]
        elif os.path.exists("/etc/redhat-release"):
            # CentOS/RHEL
            commands = [
                "sudo yum install -y wget",
                "wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm",
                "sudo yum localinstall -y google-chrome-stable_current_x86_64.rpm"
            ]
        else:
            print("不支持的Linux发行版，请手动安装Chrome")
            return False
        
        for command in commands:
            if not run_command(command, f"执行: {command}"):
                return False
    
    elif system == "windows":
        print("在Windows上安装Chrome...")
        print("请访问 https://www.google.com/chrome/ 下载并安装Chrome浏览器")
        return False
    
    else:
        print(f"不支持的操作系统: {system}")
        return False
    
    return True


def test_selenium_setup():
    """测试Selenium设置"""
    print("\n" + "=" * 50)
    print("测试Selenium设置")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        print("✓ 导入Selenium模块成功")
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        print("正在初始化WebDriver...")
        
        # 自动下载和管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ WebDriver初始化成功")
        
        # 测试访问网页
        print("正在测试网页访问...")
        driver.get("https://www.bilibili.com")
        title = driver.title
        print(f"✓ 成功访问B站，页面标题: {title}")
        
        # 关闭浏览器
        driver.quit()
        print("✓ Selenium测试完成")
        
        return True
        
    except Exception as e:
        print(f"✗ Selenium测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_test_script():
    """创建测试脚本"""
    print("\n" + "=" * 50)
    print("创建测试脚本")
    print("=" * 50)
    
    test_script_content = '''#!/usr/bin/env python3
"""
简单的Selenium测试脚本
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_selenium():
    """测试Selenium基本功能"""
    print("开始测试Selenium...")
    
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    try:
        # 初始化WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ WebDriver初始化成功")
        
        # 访问测试页面
        driver.get("https://www.bilibili.com")
        title = driver.title
        print(f"✓ 页面标题: {title}")
        
        # 关闭浏览器
        driver.quit()
        print("✓ 测试完成")
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_selenium()
'''
    
    with open("simple_selenium_test.py", "w", encoding="utf-8") as f:
        f.write(test_script_content)
    
    print("✓ 创建测试脚本: simple_selenium_test.py")
    print("运行测试: python simple_selenium_test.py")


def main():
    """主函数"""
    print("Selenium环境自动安装脚本")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("✗ 需要Python 3.7或更高版本")
        return False
    
    print(f"✓ Python版本: {sys.version}")
    
    # 安装Python包
    if not install_python_packages():
        print("✗ Python包安装失败")
        return False
    
    # 检查Chrome浏览器
    if not check_chrome_installation():
        print("Chrome浏览器未安装，尝试自动安装...")
        if not install_chrome():
            print("✗ Chrome浏览器安装失败")
            return False
    
    # 测试Selenium设置
    if not test_selenium_setup():
        print("✗ Selenium设置测试失败")
        return False
    
    # 创建测试脚本
    create_test_script()
    
    print("\n" + "=" * 60)
    print("🎉 Selenium环境安装完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 运行测试脚本: python simple_selenium_test.py")
    print("2. 运行完整测试: python test_selenium_crawler.py")
    print("3. 查看使用指南: cat SELENIUM_CRAWLER_README.md")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n安装过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 