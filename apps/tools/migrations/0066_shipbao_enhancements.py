# Generated manually for ShipBao enhancements
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tools', '0065_shipbao_want_features'),
    ]

    operations = [
        # 为ShipBaoItem添加want_count字段（如果不存在）
        migrations.AddField(
            model_name='shipbaoitem',
            name='want_count',
            field=models.IntegerField(default=0, verbose_name='想要人数'),
            preserve_default=True,
        ),
        
        # 创建ShipBaoWantItem模型
        migrations.CreateModel(
            name='ShipBaoWantItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True, verbose_name='留言')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='想要时间')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='want_users', to='tools.shipbaoitem', verbose_name='商品')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '商品想要记录',
                'verbose_name_plural': '商品想要记录',
                'ordering': ['-created_at'],
            },
        ),
        
        # 创建ShipBaoFavorite模型（如果不存在）
        migrations.CreateModel(
            name='ShipBaoFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.shipbaoitem', verbose_name='商品')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '商品收藏',
                'verbose_name_plural': '商品收藏',
                'ordering': ['-created_at'],
            },
        ),
        
        # 创建ChatNotification模型
        migrations.CreateModel(
            name='ChatNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.chatmessage', verbose_name='消息')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tools.chatroom', verbose_name='聊天室')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '聊天通知',
                'verbose_name_plural': '聊天通知',
                'ordering': ['-created_at'],
            },
        ),
        
        # 添加unique_together约束
        migrations.AlterUniqueTogether(
            name='shipbaowantitem',
            unique_together={('user', 'item')},
        ),
        
        migrations.AlterUniqueTogether(
            name='shipbaofavorite',
            unique_together={('user', 'item')},
        ),
        
        # 添加索引
        migrations.AddIndex(
            model_name='chatnotification',
            index=models.Index(fields=['user', 'is_read'], name='tools_chatno_user_id_c8d123_idx'),
        ),
        
        migrations.AddIndex(
            model_name='chatnotification',
            index=models.Index(fields=['room', 'is_read'], name='tools_chatno_room_id_f9e456_idx'),
        ),
    ]
