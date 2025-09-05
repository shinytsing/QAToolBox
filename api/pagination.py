"""
API分页配置
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .response import APIResponse


class StandardResultsSetPagination(PageNumberPagination):
    """标准分页配置"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return APIResponse.paginated(data, self.page.paginator, self.page)


class LargeResultsSetPagination(PageNumberPagination):
    """大结果集分页配置"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return APIResponse.paginated(data, self.page.paginator, self.page)


class SmallResultsSetPagination(PageNumberPagination):
    """小结果集分页配置"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return APIResponse.paginated(data, self.page.paginator, self.page)
