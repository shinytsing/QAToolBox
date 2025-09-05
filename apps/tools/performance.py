import functools
import logging
import time

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import connection

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        logger.info(f"执行时间: {execution_time:.4f}秒")
        return False

    def get_execution_time(self):
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


class DatabaseOptimizer:
    """数据库优化器"""

    @staticmethod
    def optimize_queryset(queryset, select_related=None, prefetch_related=None):
        """优化查询集"""
        if select_related:
            queryset = queryset.select_related(*select_related)

        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        return queryset

    @staticmethod
    def get_query_count():
        """获取查询次数"""
        return len(connection.queries)

    @staticmethod
    def get_query_time():
        """获取查询总时间"""
        return sum(float(query["time"]) for query in connection.queries)

    @staticmethod
    def log_slow_queries(threshold=1.0):
        """记录慢查询"""
        for query in connection.queries:
            if float(query["time"]) > threshold:
                logger.warning(f"慢查询: {query['time']}秒 - {query['sql']}")

    @staticmethod
    def clear_query_log():
        """清理查询日志"""
        connection.queries = []


class CacheManager:
    """缓存管理器"""

    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """生成缓存键"""
        key_parts = [prefix]

        # 添加位置参数
        for arg in args:
            key_parts.append(str(arg))

        # 添加关键字参数
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

        return ":".join(key_parts)

    @staticmethod
    def cache_result(timeout=300, key_prefix="cache"):
        """缓存结果装饰器"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = CacheManager.get_cache_key(key_prefix, *args, **kwargs)

                # 尝试从缓存获取
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"缓存命中: {cache_key}")
                    return cached_result

                # 执行函数并缓存结果
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                logger.debug(f"缓存设置: {cache_key}")

                return result

            return wrapper

        return decorator

    @staticmethod
    def invalidate_cache(pattern):
        """清除匹配模式的缓存"""
        # 这里可以实现更复杂的缓存清除逻辑
        # 目前只是简单的日志记录
        logger.info(f"清除缓存模式: {pattern}")


class PaginationOptimizer:
    """分页优化器"""

    @staticmethod
    def optimize_pagination(queryset, page_size=20, page_number=1):
        """优化分页查询"""
        paginator = Paginator(queryset, page_size)

        try:
            page = paginator.page(page_number)
        except Exception:
            page = paginator.page(1)

        return {
            "objects": page.object_list,
            "has_previous": page.has_previous(),
            "has_next": page.has_next(),
            "previous_page_number": page.previous_page_number() if page.has_previous() else None,
            "next_page_number": page.next_page_number() if page.has_next() else None,
            "num_pages": paginator.num_pages,
            "current_page": page.number,
            "total_count": paginator.count,
        }


class StaticFileOptimizer:
    """静态文件优化器"""

    @staticmethod
    def compress_css(css_content):
        """压缩CSS"""
        import re

        # 移除注释
        css_content = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

        # 移除多余空白
        css_content = re.sub(r"\s+", " ", css_content)
        css_content = re.sub(r";\s*}", "}", css_content)
        css_content = re.sub(r"{\s*", "{", css_content)
        css_content = re.sub(r"}\s*", "}", css_content)

        return css_content.strip()

    @staticmethod
    def compress_js(js_content):
        """压缩JavaScript"""
        import re

        # 移除单行注释
        js_content = re.sub(r"//.*$", "", js_content, flags=re.MULTILINE)

        # 移除多行注释
        js_content = re.sub(r"/\*.*?\*/", "", js_content, flags=re.DOTALL)

        # 移除多余空白
        js_content = re.sub(r"\s+", " ", js_content)

        return js_content.strip()

    @staticmethod
    def minify_html(html_content):
        """压缩HTML"""
        import re

        # 移除HTML注释
        html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)

        # 移除多余空白
        html_content = re.sub(r"\s+", " ", html_content)
        html_content = re.sub(r">\s+<", "><", html_content)

        return html_content.strip()


class ResponseOptimizer:
    """响应优化器"""

    @staticmethod
    def add_cache_headers(response, max_age=3600):
        """添加缓存头"""
        response["Cache-Control"] = f"public, max-age={max_age}"
        response["Expires"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time() + max_age))
        return response

    @staticmethod
    def add_compression_headers(response):
        """添加压缩头"""
        response["Content-Encoding"] = "gzip"
        return response

    @staticmethod
    def optimize_response(response, compress=True, cache=True):
        """优化响应"""
        if compress:
            response = ResponseOptimizer.add_compression_headers(response)

        if cache:
            response = ResponseOptimizer.add_cache_headers(response)

        return response


class MemoryOptimizer:
    """内存优化器"""

    @staticmethod
    def chunk_processing(items, chunk_size=1000, processor_func=None):
        """分块处理大量数据"""
        results = []

        for i in range(0, len(items), chunk_size):
            chunk = items[i : i + chunk_size]

            if processor_func:
                chunk_results = processor_func(chunk)
                results.extend(chunk_results)
            else:
                results.extend(chunk)

        return results

    @staticmethod
    def lazy_loading(queryset, batch_size=100):
        """懒加载查询集"""
        for i in range(0, queryset.count(), batch_size):
            batch = queryset[i : i + batch_size]
            for item in batch:
                yield item


class QueryOptimizer:
    """查询优化器"""

    @staticmethod
    def optimize_filter_conditions(conditions):
        """优化过滤条件"""
        optimized_conditions = []

        for condition in conditions:
            if hasattr(condition, "field"):
                # 确保索引字段在前
                if condition.field.db_index:
                    optimized_conditions.insert(0, condition)
                else:
                    optimized_conditions.append(condition)
            else:
                optimized_conditions.append(condition)

        return optimized_conditions

    @staticmethod
    def use_index_hints(queryset, index_name):
        """使用索引提示"""
        # 这里可以实现数据库特定的索引提示
        # 目前只是返回原始查询集
        return queryset

    @staticmethod
    def avoid_n_plus_one(queryset, related_fields):
        """避免N+1查询问题"""
        return queryset.select_related(*related_fields)


class PerformanceDecorator:
    """性能装饰器"""

    @staticmethod
    def monitor_performance(func):
        """监控函数性能"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceMonitor() as monitor:
                result = func(*args, **kwargs)

            execution_time = monitor.get_execution_time()
            if execution_time and execution_time > 1.0:
                logger.warning(f"函数 {func.__name__} 执行时间过长: {execution_time:.4f}秒")

            return result

        return wrapper

    @staticmethod
    def cache_with_timeout(timeout=300):
        """带超时的缓存装饰器"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

                # 尝试从缓存获取
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # 执行函数并缓存结果
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)

                return result

            return wrapper

        return decorator

    @staticmethod
    def database_optimization(select_related=None, prefetch_related=None):
        """数据库优化装饰器"""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 记录查询前的状态
                initial_queries = DatabaseOptimizer.get_query_count()

                result = func(*args, **kwargs)

                # 记录查询后的状态
                final_queries = DatabaseOptimizer.get_query_count()
                query_count = final_queries - initial_queries

                if query_count > 10:
                    logger.warning(f"函数 {func.__name__} 执行了 {query_count} 次查询")

                return result

            return wrapper

        return decorator


# 全局性能监控实例
performance_monitor = PerformanceMonitor()
database_optimizer = DatabaseOptimizer()
cache_manager = CacheManager()


def performance_middleware(get_response):
    """性能中间件"""

    def middleware(request):
        # 请求开始时间
        start_time = time.time()

        # 清理查询日志
        database_optimizer.clear_query_log()

        # 处理请求
        response = get_response(request)

        # 计算处理时间
        processing_time = time.time() - start_time

        # 记录性能指标
        query_count = database_optimizer.get_query_count()
        query_time = database_optimizer.get_query_time()

        # 添加性能头
        response["X-Processing-Time"] = f"{processing_time:.4f}"
        response["X-Query-Count"] = str(query_count)
        response["X-Query-Time"] = f"{query_time:.4f}"

        # 记录慢请求
        if processing_time > 2.0:
            logger.warning(f"慢请求: {request.path} - {processing_time:.4f}秒")

        # 记录慢查询
        database_optimizer.log_slow_queries(threshold=0.5)

        return response

    return middleware
