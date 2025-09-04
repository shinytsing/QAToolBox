# Generated manually to create missing diary-related model tables

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0056_add_missing_lifediaryentry_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='LifeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='分类名称')),
                ('description', models.TextField(blank=True, verbose_name='分类描述')),
                ('icon', models.CharField(max_length=10, blank=True, verbose_name='分类图标')),
                ('color', models.CharField(max_length=7, blank=True, verbose_name='分类颜色')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '生活分类',
                'verbose_name_plural': '生活分类',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LifeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='标签名称')),
                ('description', models.TextField(blank=True, verbose_name='标签描述')),
                ('color', models.CharField(max_length=7, blank=True, verbose_name='标签颜色')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '生活标签',
                'verbose_name_plural': '生活标签',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DiaryAchievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievement_type', models.CharField(choices=[('streak', '连续记录'), ('count', '总数统计'), ('variety', '多样性'), ('consistency', '持续性'), ('creative', '创意性')], max_length=20, verbose_name='成就类型')),
                ('name', models.CharField(max_length=100, verbose_name='成就名称')),
                ('description', models.TextField(verbose_name='成就描述')),
                ('icon', models.CharField(max_length=10, verbose_name='成就图标')),
                ('target_value', models.IntegerField(verbose_name='目标值')),
                ('current_value', models.IntegerField(default=0, verbose_name='当前值')),
                ('is_completed', models.BooleanField(default=False, verbose_name='是否完成')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '日记成就',
                'verbose_name_plural': '日记成就',
                'unique_together': {('user', 'name')},
                'ordering': ['-is_completed', '-current_value'],
            },
        ),
        migrations.CreateModel(
            name='DiaryTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='模板名称')),
                ('description', models.TextField(blank=True, verbose_name='模板描述')),
                ('questions', models.JSONField(default=list, verbose_name='问题列表')),
                ('category', models.CharField(max_length=50, blank=True, verbose_name='模板分类')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '日记模板',
                'verbose_name_plural': '日记模板',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DailyQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(verbose_name='问题内容')),
                ('category', models.CharField(max_length=50, blank=True, verbose_name='问题分类')),
                ('difficulty', models.CharField(choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难')], default='medium', max_length=10, verbose_name='难度等级')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '每日问题',
                'verbose_name_plural': '每日问题',
                'ordering': ['category', 'difficulty'],
            },
        ),
    ]
