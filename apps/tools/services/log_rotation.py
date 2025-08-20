"""
日志轮转服务
定期轮转和压缩日志文件
"""
import os
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class LogRotationService:
    """日志轮转服务"""
    
    def __init__(self):
        self.rotation_config = {
            'max_size_mb': 100,  # 最大文件大小（MB）
            'retention_days': 30,  # 保留天数
            'compress_old_logs': True,  # 压缩旧日志
            'backup_count': 5,  # 备份文件数量
        }
        
        # 日志文件路径
        self.log_paths = [
            'logs/django.log',
            'logs/celery.log',
            'logs/error.log',
            'logs/access.log',
            'logs/performance.log',
        ]
    
    def rotate_logs(self) -> Dict[str, Any]:
        """轮转日志文件"""
        results = {}
        
        try:
            for log_path in self.log_paths:
                if os.path.exists(log_path):
                    result = self._rotate_single_log(log_path)
                    results[log_path] = result
                else:
                    results[log_path] = {'status': 'not_found'}
            
            # 清理旧日志文件
            cleanup_result = self._cleanup_old_logs()
            results['cleanup'] = cleanup_result
            
            logger.info("日志轮转完成")
            return {
                'status': 'success',
                'results': results,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"日志轮转失败: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now()
            }
    
    def _rotate_single_log(self, log_path: str) -> Dict[str, Any]:
        """轮转单个日志文件"""
        try:
            file_size_mb = os.path.getsize(log_path) / (1024 * 1024)
            
            # 检查文件大小是否需要轮转
            if file_size_mb < self.rotation_config['max_size_mb']:
                return {
                    'status': 'no_rotation_needed',
                    'size_mb': round(file_size_mb, 2)
                }
            
            # 创建备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{log_path}.{timestamp}"
            
            # 移动当前日志文件
            shutil.move(log_path, backup_path)
            
            # 压缩备份文件
            if self.rotation_config['compress_old_logs']:
                self._compress_log_file(backup_path)
                backup_path += '.gz'
            
            # 创建新的日志文件
            Path(log_path).touch()
            
            return {
                'status': 'rotated',
                'original_size_mb': round(file_size_mb, 2),
                'backup_path': backup_path,
                'compressed': self.rotation_config['compress_old_logs']
            }
            
        except Exception as e:
            logger.error(f"轮转日志文件失败 {log_path}: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _compress_log_file(self, file_path: str) -> None:
        """压缩日志文件"""
        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 删除原文件
            os.remove(file_path)
            
        except Exception as e:
            logger.error(f"压缩日志文件失败 {file_path}: {e}")
    
    def _cleanup_old_logs(self) -> Dict[str, Any]:
        """清理旧日志文件"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.rotation_config['retention_days'])
            deleted_files = 0
            deleted_size_mb = 0
            
            # 遍历日志目录
            log_dir = Path('logs')
            if not log_dir.exists():
                return {'status': 'no_logs_directory'}
            
            for log_file in log_dir.glob('*'):
                if log_file.is_file() and self._is_old_log_file(log_file, cutoff_date):
                    try:
                        file_size_mb = log_file.stat().st_size / (1024 * 1024)
                        log_file.unlink()
                        deleted_files += 1
                        deleted_size_mb += file_size_mb
                        
                        logger.info(f"删除旧日志文件: {log_file}")
                        
                    except Exception as e:
                        logger.warning(f"删除日志文件失败 {log_file}: {e}")
            
            return {
                'status': 'cleaned',
                'deleted_files': deleted_files,
                'deleted_size_mb': round(deleted_size_mb, 2),
                'retention_days': self.rotation_config['retention_days']
            }
            
        except Exception as e:
            logger.error(f"清理旧日志文件失败: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _is_old_log_file(self, file_path: Path, cutoff_date: datetime) -> bool:
        """检查是否为旧日志文件"""
        try:
            # 检查文件修改时间
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return mtime < cutoff_date
        except Exception:
            return False
    
    def get_log_stats(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        try:
            stats = {}
            
            for log_path in self.log_paths:
                if os.path.exists(log_path):
                    file_size_mb = os.path.getsize(log_path) / (1024 * 1024)
                    stats[log_path] = {
                        'exists': True,
                        'size_mb': round(file_size_mb, 2),
                        'needs_rotation': file_size_mb >= self.rotation_config['max_size_mb']
                    }
                else:
                    stats[log_path] = {
                        'exists': False,
                        'size_mb': 0,
                        'needs_rotation': False
                    }
            
            # 获取日志目录统计
            log_dir = Path('logs')
            if log_dir.exists():
                total_files = len(list(log_dir.glob('*')))
                total_size_mb = sum(
                    f.stat().st_size for f in log_dir.glob('*') if f.is_file()
                ) / (1024 * 1024)
                
                stats['directory'] = {
                    'total_files': total_files,
                    'total_size_mb': round(total_size_mb, 2)
                }
            else:
                stats['directory'] = {
                    'total_files': 0,
                    'total_size_mb': 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取日志统计信息失败: {e}")
            return {'error': str(e)}
    
    def create_log_directories(self) -> None:
        """创建日志目录"""
        try:
            # 创建logs目录
            Path('logs').mkdir(exist_ok=True)
            
            # 创建子目录
            subdirs = ['django', 'celery', 'error', 'access', 'performance']
            for subdir in subdirs:
                Path(f'logs/{subdir}').mkdir(exist_ok=True)
            
            logger.info("日志目录创建完成")
            
        except Exception as e:
            logger.error(f"创建日志目录失败: {e}")


# 全局实例
log_rotation_service = LogRotationService()


# 轮转函数
def rotate_logs() -> Dict[str, Any]:
    """轮转日志文件"""
    return log_rotation_service.rotate_logs()


# 获取统计信息
def get_log_stats() -> Dict[str, Any]:
    """获取日志统计信息"""
    return log_rotation_service.get_log_stats()


# 创建目录
def create_log_directories() -> None:
    """创建日志目录"""
    log_rotation_service.create_log_directories()
