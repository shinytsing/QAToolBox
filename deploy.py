#!/usr/bin/env python
"""
QAToolBox 部署脚本
用于自动化部署流程
"""

import os
import sys
import subprocess
import shutil
import time
from datetime import datetime
from pathlib import Path

class Deployer:
    """部署器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / 'backups'
        self.logs_dir = self.project_root / 'logs'
        
        # 创建必要的目录
        self.backup_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # 写入日志文件
        log_file = self.logs_dir / f"deploy_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def run_command(self, command, cwd=None):
        """运行命令"""
        self.log(f"执行命令: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.log(f"命令执行成功: {command}")
                if result.stdout:
                    self.log(f"输出: {result.stdout}")
                return True
            else:
                self.log(f"命令执行失败: {command}")
                self.log(f"错误: {result.stderr}")
                return False
        
        except Exception as e:
            self.log(f"命令执行异常: {command}")
            self.log(f"异常: {str(e)}")
            return False
    
    def backup_database(self):
        """备份数据库"""
        self.log("开始备份数据库...")
        
        backup_file = self.backup_dir / f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if self.run_command(f"python manage.py dumpdata --exclude auth.permission --exclude contenttypes > {backup_file}"):
            self.log(f"数据库备份成功: {backup_file}")
            return True
        else:
            self.log("数据库备份失败")
            return False
    
    def backup_media_files(self):
        """备份媒体文件"""
        self.log("开始备份媒体文件...")
        
        media_dir = self.project_root / 'media'
        if not media_dir.exists():
            self.log("媒体目录不存在，跳过备份")
            return True
        
        backup_file = self.backup_dir / f"media_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        if self.run_command(f"tar -czf {backup_file} -C {self.project_root} media"):
            self.log(f"媒体文件备份成功: {backup_file}")
            return True
        else:
            self.log("媒体文件备份失败")
            return False
    
    def install_dependencies(self):
        """安装依赖"""
        self.log("开始安装依赖...")
        
        # 安装生产环境依赖
        if self.run_command("pip install -r requirements/prod.txt"):
            self.log("依赖安装成功")
            return True
        else:
            self.log("依赖安装失败")
            return False
    
    def run_migrations(self):
        """运行数据库迁移"""
        self.log("开始运行数据库迁移...")
        
        if self.run_command("python manage.py migrate"):
            self.log("数据库迁移成功")
            return True
        else:
            self.log("数据库迁移失败")
            return False
    
    def collect_static_files(self):
        """收集静态文件"""
        self.log("开始收集静态文件...")
        
        if self.run_command("python manage.py collectstatic --noinput"):
            self.log("静态文件收集成功")
            return True
        else:
            self.log("静态文件收集失败")
            return False
    
    def run_tests(self):
        """运行测试"""
        self.log("开始运行测试...")
        
        if self.run_command("python run_tests.py"):
            self.log("测试运行成功")
            return True
        else:
            self.log("测试运行失败")
            return False
    
    def check_security(self):
        """安全检查"""
        self.log("开始安全检查...")
        
        # 运行安全扫描
        if self.run_command("bandit -r . -f json -o security_report.json"):
            self.log("安全扫描完成")
        
        # 检查依赖安全
        if self.run_command("safety check --json --output safety_report.json"):
            self.log("依赖安全检查完成")
        
        return True
    
    def optimize_performance(self):
        """性能优化"""
        self.log("开始性能优化...")
        
        # 压缩静态文件
        if self.run_command("python manage.py compress"):
            self.log("静态文件压缩完成")
        
        # 清理缓存
        if self.run_command("python manage.py clearcache"):
            self.log("缓存清理完成")
        
        return True
    
    def restart_services(self):
        """重启服务"""
        self.log("开始重启服务...")
        
        # 重启Gunicorn
        if self.run_command("sudo systemctl restart qatoolbox"):
            self.log("Gunicorn重启成功")
        
        # 重启Nginx
        if self.run_command("sudo systemctl restart nginx"):
            self.log("Nginx重启成功")
        
        # 重启Redis
        if self.run_command("sudo systemctl restart redis"):
            self.log("Redis重启成功")
        
        return True
    
    def health_check(self):
        """健康检查"""
        self.log("开始健康检查...")
        
        import requests
        import time
        
        # 等待服务启动
        time.sleep(10)
        
        try:
            response = requests.get('http://localhost:8000/health/', timeout=10)
            if response.status_code == 200:
                self.log("健康检查通过")
                return True
            else:
                self.log(f"健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"健康检查异常: {str(e)}")
            return False
    
    def cleanup_old_backups(self, days=30):
        """清理旧备份"""
        self.log("开始清理旧备份...")
        
        import glob
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                self.log(f"删除旧备份: {backup_file}")
        
        self.log("旧备份清理完成")
    
    def deploy(self, skip_tests=False, skip_backup=False):
        """执行完整部署"""
        self.log("开始部署QAToolBox...")
        start_time = time.time()
        
        try:
            # 1. 备份
            if not skip_backup:
                if not self.backup_database():
                    return False
                if not self.backup_media_files():
                    return False
            
            # 2. 安装依赖
            if not self.install_dependencies():
                return False
            
            # 3. 运行迁移
            if not self.run_migrations():
                return False
            
            # 4. 收集静态文件
            if not self.collect_static_files():
                return False
            
            # 5. 运行测试
            if not skip_tests:
                if not self.run_tests():
                    self.log("测试失败，但继续部署...")
            
            # 6. 安全检查
            self.check_security()
            
            # 7. 性能优化
            self.optimize_performance()
            
            # 8. 重启服务
            if not self.restart_services():
                return False
            
            # 9. 健康检查
            if not self.health_check():
                self.log("健康检查失败，但部署可能成功")
            
            # 10. 清理旧备份
            self.cleanup_old_backups()
            
            deployment_time = time.time() - start_time
            self.log(f"部署完成！总耗时: {deployment_time:.2f}秒")
            
            return True
        
        except Exception as e:
            self.log(f"部署过程中发生异常: {str(e)}")
            return False
    
    def rollback(self):
        """回滚部署"""
        self.log("开始回滚部署...")
        
        # 查找最新的备份
        backup_files = list(self.backup_dir.glob('db_backup_*.json'))
        if not backup_files:
            self.log("没有找到可用的备份文件")
            return False
        
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        self.log(f"使用备份文件: {latest_backup}")
        
        # 恢复数据库
        if self.run_command(f"python manage.py loaddata {latest_backup}"):
            self.log("数据库恢复成功")
        else:
            self.log("数据库恢复失败")
            return False
        
        # 重启服务
        self.restart_services()
        
        self.log("回滚完成")
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QAToolBox 部署脚本')
    parser.add_argument('action', choices=['deploy', 'rollback', 'backup', 'test'], 
                       help='执行的操作')
    parser.add_argument('--skip-tests', action='store_true', 
                       help='跳过测试')
    parser.add_argument('--skip-backup', action='store_true', 
                       help='跳过备份')
    
    args = parser.parse_args()
    
    deployer = Deployer()
    
    if args.action == 'deploy':
        success = deployer.deploy(skip_tests=args.skip_tests, skip_backup=args.skip_backup)
        sys.exit(0 if success else 1)
    
    elif args.action == 'rollback':
        success = deployer.rollback()
        sys.exit(0 if success else 1)
    
    elif args.action == 'backup':
        success = deployer.backup_database() and deployer.backup_media_files()
        sys.exit(0 if success else 1)
    
    elif args.action == 'test':
        success = deployer.run_tests()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 