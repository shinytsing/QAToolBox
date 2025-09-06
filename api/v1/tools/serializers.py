"""
极客工具模块序列化器
"""
from rest_framework import serializers
from apps.tools.models import PDFConversionRecord, JobSearchRequest


class PDFConversionSerializer(serializers.ModelSerializer):
    """PDF转换序列化器"""
    
    class Meta:
        model = PDFConversionRecord
        fields = (
            'id', 'user', 'original_filename', 'converted_filename',
            'conversion_type', 'file_size', 'status', 'error_message',
            'created_at', 'completed_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'completed_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class WebCrawlerSerializer(serializers.Serializer):
    """网页爬虫序列化器"""
    url = serializers.URLField()
    crawler_type = serializers.ChoiceField(choices=[
        ('general', '通用爬虫'),
        ('news', '新闻爬虫'),
        ('ecommerce', '电商爬虫'),
        ('social', '社交媒体爬虫'),
        ('job', '招聘信息爬虫'),
        ('real_estate', '房产信息爬虫'),
    ])
    max_pages = serializers.IntegerField(min_value=1, max_value=100, default=10)
    delay = serializers.FloatField(min_value=0.1, max_value=10.0, default=1.0)
    headers = serializers.JSONField(required=False, default=dict)
    selectors = serializers.JSONField(required=False, default=dict)
    filters = serializers.JSONField(required=False, default=dict)
    output_format = serializers.ChoiceField(choices=[
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('xml', 'XML'),
    ], default='json')


class TestCaseGeneratorSerializer(serializers.Serializer):
    """测试用例生成序列化器"""
    test_type = serializers.ChoiceField(choices=[
        ('api', 'API测试'),
        ('ui', 'UI测试'),
        ('unit', '单元测试'),
        ('integration', '集成测试'),
        ('performance', '性能测试'),
        ('security', '安全测试'),
    ])
    function_description = serializers.CharField(max_length=1000)
    programming_language = serializers.ChoiceField(choices=[
        ('python', 'Python'),
        ('java', 'Java'),
        ('javascript', 'JavaScript'),
        ('csharp', 'C#'),
        ('php', 'PHP'),
        ('go', 'Go'),
    ])
    test_framework = serializers.ChoiceField(choices=[
        ('pytest', 'pytest'),
        ('unittest', 'unittest'),
        ('junit', 'JUnit'),
        ('jest', 'Jest'),
        ('mocha', 'Mocha'),
        ('nunit', 'NUnit'),
        ('phpunit', 'PHPUnit'),
    ])
    test_level = serializers.ChoiceField(choices=[
        ('basic', '基础测试'),
        ('comprehensive', '全面测试'),
        ('edge_cases', '边界测试'),
        ('stress', '压力测试'),
    ], default='basic')
    include_negative_tests = serializers.BooleanField(default=True)
    include_boundary_tests = serializers.BooleanField(default=True)
    include_data_driven_tests = serializers.BooleanField(default=False)


class ProxyConfigSerializer(serializers.Serializer):
    """代理配置序列化器"""
    proxy_type = serializers.ChoiceField(choices=[
        ('http', 'HTTP代理'),
        ('https', 'HTTPS代理'),
        ('socks4', 'SOCKS4代理'),
        ('socks5', 'SOCKS5代理'),
    ])
    host = serializers.CharField(max_length=255)
    port = serializers.IntegerField(min_value=1, max_value=65535)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True)
    enabled = serializers.BooleanField(default=True)


class DataAnalysisSerializer(serializers.Serializer):
    """数据分析序列化器"""
    data_source = serializers.ChoiceField(choices=[
        ('file', '文件上传'),
        ('url', 'URL链接'),
        ('database', '数据库'),
        ('api', 'API接口'),
    ])
    file = serializers.FileField(required=False)
    url = serializers.URLField(required=False)
    analysis_type = serializers.ChoiceField(choices=[
        ('descriptive', '描述性分析'),
        ('predictive', '预测性分析'),
        ('prescriptive', '规范性分析'),
        ('diagnostic', '诊断性分析'),
    ])
    output_format = serializers.ChoiceField(choices=[
        ('chart', '图表'),
        ('table', '表格'),
        ('report', '报告'),
        ('json', 'JSON数据'),
    ])
    parameters = serializers.JSONField(required=False, default=dict)


class CodeFormatterSerializer(serializers.Serializer):
    """代码格式化序列化器"""
    code = serializers.CharField()
    language = serializers.ChoiceField(choices=[
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('php', 'PHP'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ])
    style = serializers.ChoiceField(choices=[
        ('pep8', 'PEP 8'),
        ('google', 'Google Style'),
        ('airbnb', 'Airbnb Style'),
        ('standard', 'Standard'),
        ('prettier', 'Prettier'),
        ('black', 'Black'),
    ], required=False)
    options = serializers.JSONField(required=False, default=dict)


class QRCodeGeneratorSerializer(serializers.Serializer):
    """二维码生成序列化器"""
    content = serializers.CharField(max_length=2000)
    size = serializers.IntegerField(min_value=100, max_value=1000, default=200)
    format = serializers.ChoiceField(choices=[
        ('png', 'PNG'),
        ('jpg', 'JPG'),
        ('svg', 'SVG'),
    ], default='png')
    error_correction = serializers.ChoiceField(choices=[
        ('L', '低'),
        ('M', '中'),
        ('Q', '高'),
        ('H', '最高'),
    ], default='M')
    border = serializers.IntegerField(min_value=0, max_value=10, default=4)
    color = serializers.CharField(max_length=7, default='#000000')
    background_color = serializers.CharField(max_length=7, default='#FFFFFF')


class HashGeneratorSerializer(serializers.Serializer):
    """哈希生成序列化器"""
    text = serializers.CharField()
    algorithm = serializers.ChoiceField(choices=[
        ('md5', 'MD5'),
        ('sha1', 'SHA-1'),
        ('sha256', 'SHA-256'),
        ('sha512', 'SHA-512'),
        ('blake2b', 'BLAKE2b'),
        ('blake2s', 'BLAKE2s'),
    ])
    encoding = serializers.ChoiceField(choices=[
        ('hex', '十六进制'),
        ('base64', 'Base64'),
        ('binary', '二进制'),
    ], default='hex')


class Base64EncoderSerializer(serializers.Serializer):
    """Base64编码序列化器"""
    text = serializers.CharField()
    operation = serializers.ChoiceField(choices=[
        ('encode', '编码'),
        ('decode', '解码'),
    ])
    encoding = serializers.ChoiceField(choices=[
        ('utf-8', 'UTF-8'),
        ('ascii', 'ASCII'),
        ('latin-1', 'Latin-1'),
    ], default='utf-8')
