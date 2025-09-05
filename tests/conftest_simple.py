"""
简化的pytest配置文件
用于基础测试，避免复杂的Django设置
"""

import os
import sys

import django
from django.conf import settings

# 设置Django环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test_minimal")

# 配置Django
django.setup()

import pytest


@pytest.fixture(scope="session")
def django_db_setup():
    """数据库设置"""
    # 使用SQLite内存数据库
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """为所有测试启用数据库访问"""
    pass


def pytest_configure(config):
    """pytest配置"""
    # 禁用迁移以加速测试
    settings.MIGRATION_MODULES = {
        "auth": None,
        "contenttypes": None,
        "sessions": None,
        "users": None,
        "tools": None,
        "content": None,
    }

    # 测试数据库配置
    settings.DATABASES["default"]["NAME"] = ":memory:"

    # 禁用缓存
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

    # 禁用Celery
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

    # 静态文件设置
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

    # 邮件设置
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
