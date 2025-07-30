# QAToolbox/apps/tools/urls.py
from django.urls import path
from .views import test_case_generator, download_file, redbook_generator
from .api_GenerateTestCases import GenerateTestCasesAPI
from .api_GenerateRedBook import  GenerateRedBookAPI  # 从api.py导入

urlpatterns = [
    path('download/<str:filename>/', download_file, name='download_file'),
    path('test-case-generator/', test_case_generator, name='test_case_generator'),
    path('redbook-generator/', redbook_generator, name='redbook_generator_page'),
    path('api/generate-testcases/', GenerateTestCasesAPI.as_view(), name='generate_testcases_api'),
    # 修正API路由：使用类名.as_view()的形式
    path('api/redbook-generate/', GenerateRedBookAPI.as_view(), name='redbook_generate_api'),
]