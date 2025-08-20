"""
缓存测试管理命令
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import time


class Command(BaseCommand):
    help = '测试缓存系统功能'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='测试迭代次数 (默认: 10)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='详细输出'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('开始缓存测试...')
        
        iterations = options['iterations']
        verbose = options['verbose']
        
        results = {
            'basic_read_write': self._test_basic_read_write(),
            'expiration': self._test_expiration(),
            'bulk_operations': self._test_bulk_operations(iterations),
            'performance': self._test_performance(iterations),
            'connection': self._test_connection()
        }
        
        if verbose:
            self._print_detailed_results(results)
        else:
            self._print_summary_results(results)
        
        # 检查是否有失败的测试
        failed_tests = [r for r in results.values() if not r['success']]
        if failed_tests:
            self.stdout.write(
                self.style.ERROR(f'发现 {len(failed_tests)} 个缓存测试失败')
            )
            return 1
        else:
            self.stdout.write(
                self.style.SUCCESS('所有缓存测试通过')
            )
            return 0
    
    def _test_basic_read_write(self):
        """测试基本读写功能"""
        try:
            test_key = 'cache_test_basic'
            test_value = 'test_value_123'
            
            # 写入测试
            cache.set(test_key, test_value, timeout=60)
            
            # 读取测试
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                return {
                    'success': True,
                    'message': '基本读写功能正常',
                    'details': f'写入值: {test_value}, 读取值: {retrieved_value}'
                }
            else:
                return {
                    'success': False,
                    'message': '基本读写功能失败',
                    'details': f'期望值: {test_value}, 实际值: {retrieved_value}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'基本读写测试异常: {e}',
                'details': str(e)
            }
    
    def _test_expiration(self):
        """测试过期功能"""
        try:
            test_key = 'cache_test_expiration'
            test_value = 'expiration_test'
            
            # 设置1秒过期
            cache.set(test_key, test_value, timeout=1)
            
            # 立即读取应该成功
            immediate_value = cache.get(test_key)
            if immediate_value != test_value:
                return {
                    'success': False,
                    'message': '过期测试失败：立即读取失败',
                    'details': f'期望值: {test_value}, 实际值: {immediate_value}'
                }
            
            # 等待2秒后读取应该失败
            time.sleep(2)
            expired_value = cache.get(test_key)
            
            if expired_value is None:
                return {
                    'success': True,
                    'message': '过期功能正常',
                    'details': '数据在1秒后正确过期'
                }
            else:
                return {
                    'success': False,
                    'message': '过期功能失败',
                    'details': f'数据未过期，值: {expired_value}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'过期测试异常: {e}',
                'details': str(e)
            }
    
    def _test_bulk_operations(self, iterations):
        """测试批量操作"""
        try:
            test_data = {}
            for i in range(iterations):
                test_data[f'bulk_key_{i}'] = f'bulk_value_{i}'
            
            # 批量设置
            cache.set_many(test_data, timeout=60)
            
            # 批量获取
            retrieved_data = cache.get_many(test_data.keys())
            
            # 检查数据完整性
            missing_keys = set(test_data.keys()) - set(retrieved_data.keys())
            if missing_keys:
                return {
                    'success': False,
                    'message': f'批量操作失败：缺少 {len(missing_keys)} 个键',
                    'details': f'缺少的键: {list(missing_keys)[:5]}...'
                }
            
            # 检查数据正确性
            incorrect_values = []
            for key, expected_value in test_data.items():
                if retrieved_data.get(key) != expected_value:
                    incorrect_values.append(key)
            
            if incorrect_values:
                return {
                    'success': False,
                    'message': f'批量操作失败：{len(incorrect_values)} 个值不正确',
                    'details': f'不正确的键: {incorrect_values[:5]}...'
                }
            
            return {
                'success': True,
                'message': f'批量操作正常 ({iterations} 个键值对)',
                'details': f'成功处理 {len(test_data)} 个键值对'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'批量操作测试异常: {e}',
                'details': str(e)
            }
    
    def _test_performance(self, iterations):
        """测试性能"""
        try:
            start_time = time.time()
            
            # 写入性能测试
            for i in range(iterations):
                cache.set(f'perf_key_{i}', f'perf_value_{i}', timeout=60)
            
            write_time = time.time() - start_time
            
            # 读取性能测试
            start_time = time.time()
            for i in range(iterations):
                cache.get(f'perf_key_{i}')
            
            read_time = time.time() - start_time
            
            avg_write_time = write_time / iterations * 1000  # 毫秒
            avg_read_time = read_time / iterations * 1000   # 毫秒
            
            # 性能基准：写入 < 10ms, 读取 < 5ms
            write_ok = avg_write_time < 10
            read_ok = avg_read_time < 5
            
            if write_ok and read_ok:
                return {
                    'success': True,
                    'message': '性能测试通过',
                    'details': f'平均写入时间: {avg_write_time:.2f}ms, 平均读取时间: {avg_read_time:.2f}ms'
                }
            else:
                return {
                    'success': False,
                    'message': '性能测试失败',
                    'details': f'写入时间: {avg_write_time:.2f}ms (期望<10ms), 读取时间: {avg_read_time:.2f}ms (期望<5ms)'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'性能测试异常: {e}',
                'details': str(e)
            }
    
    def _test_connection(self):
        """测试连接"""
        try:
            # 测试连接
            cache.set('connection_test', 'ok', timeout=10)
            result = cache.get('connection_test')
            
            if result == 'ok':
                return {
                    'success': True,
                    'message': '缓存连接正常',
                    'details': '连接测试通过'
                }
            else:
                return {
                    'success': False,
                    'message': '缓存连接失败',
                    'details': f'连接测试失败，返回值: {result}'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接测试异常: {e}',
                'details': str(e)
            }
    
    def _print_detailed_results(self, results):
        """打印详细结果"""
        for test_name, result in results.items():
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"✅ {test_name}: {result['message']}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ {test_name}: {result['message']}"))
            
            self.stdout.write(f"   详情: {result['details']}")
            self.stdout.write("")
    
    def _print_summary_results(self, results):
        """打印摘要结果"""
        passed = sum(1 for r in results.values() if r['success'])
        total = len(results)
        
        self.stdout.write(f"缓存测试结果: {passed}/{total} 通过")
        
        for test_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            self.stdout.write(f"{status} {test_name}: {result['message']}")
