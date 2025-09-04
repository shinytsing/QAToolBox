# Generated manually to fix missing fields in LifeDiaryEntry model

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0055_add_ip_address_to_useronlinestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifediaryentry',
            name='entry_type',
            field=models.CharField(
                choices=[
                    ('text', '文字'),
                    ('image', '图片'),
                    ('voice', '语音'),
                    ('template', '模板'),
                    ('quick', '快记'),
                ],
                default='text',
                max_length=20,
                verbose_name='记录类型'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='diary/images/',
                verbose_name='图片'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='voice_text',
            field=models.TextField(
                blank=True,
                verbose_name='语音转文字'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='voice_file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='diary/voice/',
                verbose_name='语音文件'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='template_name',
            field=models.CharField(
                blank=True,
                max_length=100,
                verbose_name='模板名称'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='question_answer',
            field=models.JSONField(
                default=dict,
                verbose_name='问题回答'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='daily_question',
            field=models.TextField(
                blank=True,
                verbose_name='每日问题'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='hobby_category',
            field=models.CharField(
                blank=True,
                max_length=50,
                verbose_name='爱好分类'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='word_count',
            field=models.IntegerField(
                default=0,
                verbose_name='字数'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='reading_time',
            field=models.IntegerField(
                default=0,
                verbose_name='阅读时间(分钟)'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='is_private',
            field=models.BooleanField(
                default=False,
                verbose_name='是否私密'
            ),
        ),
        migrations.AddField(
            model_name='lifediaryentry',
            name='auto_saved',
            field=models.BooleanField(
                default=False,
                verbose_name='自动保存'
            ),
        ),
        migrations.AlterField(
            model_name='lifediaryentry',
            name='mood',
            field=models.CharField(
                choices=[
                    ('😊', '开心'),
                    ('😐', '平静'),
                    ('😢', '难过'),
                    ('🥳', '兴奋'),
                    ('😴', '疲惫'),
                    ('🤔', '思考'),
                    ('😍', '感动'),
                    ('😤', '愤怒'),
                ],
                max_length=10,
                verbose_name='心情'
            ),
        ),
        migrations.AlterField(
            model_name='lifediaryentry',
            name='tags',
            field=models.JSONField(
                default=list,
                verbose_name='标签'
            ),
        ),
        migrations.AlterField(
            model_name='lifediaryentry',
            name='question_answers',
            field=models.JSONField(
                default=list,
                verbose_name='问题回答'
            ),
        ),
    ]
