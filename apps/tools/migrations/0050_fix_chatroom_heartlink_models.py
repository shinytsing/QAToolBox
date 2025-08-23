# Generated manually to fix chatroom and heartlink models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0049_featureflag_systemconfiguration_systemlog_and_more'),
    ]

    operations = [
        # 1. 为ChatRoom添加缺失的字段
        migrations.AddField(
            model_name='chatroom',
            name='ended_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='结束时间'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='max_members',
            field=models.IntegerField(default=100, verbose_name='最大成员数'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='is_encrypted',
            field=models.BooleanField(default=False, verbose_name='是否加密'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='last_activity',
            field=models.DateTimeField(auto_now=True, verbose_name='最后活动时间'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='房间名称'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='description',
            field=models.TextField(blank=True, verbose_name='描述'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='room_type',
            field=models.CharField(choices=[('private', '私聊'), ('group', '群聊'), ('public', '公开'), ('system', '系统')], default='private', max_length=20, verbose_name='房间类型'),
        ),
        
        # 2. 修改ChatRoom的room_id字段长度
        migrations.AlterField(
            model_name='chatroom',
            name='room_id',
            field=models.CharField(blank=True, max_length=100, unique=True, verbose_name='房间ID'),
        ),
        
        # 3. 修改ChatRoom的status字段选择
        migrations.AlterField(
            model_name='chatroom',
            name='status',
            field=models.CharField(choices=[('waiting', '等待匹配'), ('active', '活跃'), ('ended', '已结束'), ('inactive', '非活跃'), ('archived', '已归档'), ('deleted', '已删除')], default='active', max_length=20, verbose_name='状态'),
        ),
        
        # 4. 修改HeartLinkRequest的chat_room字段为可选
        migrations.AlterField(
            model_name='heartlinkrequest',
            name='chat_room',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='heart_link_requests', to='tools.chatroom', verbose_name='聊天室'),
        ),
    ]
