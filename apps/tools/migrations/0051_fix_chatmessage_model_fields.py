# Generated manually to fix ChatMessage model fields

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tools', '0050_fix_chatroom_heartlink_models'),
    ]

    operations = [
        # 1. 添加ChatMessage缺失的字段
        migrations.AddField(
            model_name='chatmessage',
            name='file_size',
            field=models.IntegerField(default=0, verbose_name='文件大小'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tools.chatmessage', verbose_name='回复消息'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='is_edited',
            field=models.BooleanField(default=False, verbose_name='是否编辑'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='是否删除'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        
        # 2. 修改现有字段以匹配模型定义
        migrations.AlterField(
            model_name='chatmessage',
            name='file_url',
            field=models.URLField(blank=True, verbose_name='文件链接'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='message_type',
            field=models.CharField(choices=[('text', '文本'), ('image', '图片'), ('file', '文件'), ('voice', '语音'), ('video', '视频'), ('system', '系统消息')], default='text', max_length=20, verbose_name='消息类型'),
        ),
        
        # 3. 创建MessageRead模型（如果不存在）
        migrations.CreateModel(
            name='MessageRead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.chatmessage', verbose_name='消息')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '消息已读记录',
                'verbose_name_plural': '消息已读记录',
                'indexes': [
                    models.Index(fields=['message', 'read_at'], name='tools_messageread_message_read_at_idx'),
                    models.Index(fields=['user', 'read_at'], name='tools_messageread_user_read_at_idx'),
                ],
                'unique_together': {('message', 'user')},
            },
        ),
        
        # 4. 添加read_by多对多关系
        migrations.AddField(
            model_name='chatmessage',
            name='read_by',
            field=models.ManyToManyField(related_name='chat_read_messages', through='tools.MessageRead', to=settings.AUTH_USER_MODEL, verbose_name='已读用户'),
        ),
    ]
