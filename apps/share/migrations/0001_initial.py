# Generated manually for share app

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('wechat', '微信'), ('weibo', '微博'), ('douyin', '抖音'), ('xiaohongshu', '小红书'), ('qq', 'QQ'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter'), ('facebook', 'Facebook'), ('telegram', 'Telegram'), ('whatsapp', 'WhatsApp'), ('email', '邮件'), ('link', '链接'), ('qrcode', '二维码')], max_length=20, verbose_name='分享平台')),
                ('page_url', models.URLField(verbose_name='分享页面URL')),
                ('page_title', models.CharField(max_length=200, verbose_name='页面标题')),
                ('share_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='分享时间')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('user_agent', models.TextField(blank=True, verbose_name='用户代理')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='用户')),
            ],
            options={
                'verbose_name': '分享记录',
                'verbose_name_plural': '分享记录',
                'ordering': ['-share_time'],
            },
        ),
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(verbose_name='原始URL')),
                ('short_code', models.CharField(max_length=10, unique=True, verbose_name='短链接代码')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('image_url', models.URLField(blank=True, verbose_name='图片URL')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('click_count', models.PositiveIntegerField(default=0, verbose_name='点击次数')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否激活')),
            ],
            options={
                'verbose_name': '分享链接',
                'verbose_name_plural': '分享链接',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ShareAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='日期')),
                ('platform', models.CharField(choices=[('wechat', '微信'), ('weibo', '微博'), ('douyin', '抖音'), ('xiaohongshu', '小红书'), ('qq', 'QQ'), ('linkedin', 'LinkedIn'), ('twitter', 'Twitter'), ('facebook', 'Facebook'), ('telegram', 'Telegram'), ('whatsapp', 'WhatsApp'), ('email', '邮件'), ('link', '链接'), ('qrcode', '二维码')], max_length=20, verbose_name='平台')),
                ('share_count', models.PositiveIntegerField(default=0, verbose_name='分享次数')),
                ('click_count', models.PositiveIntegerField(default=0, verbose_name='点击次数')),
            ],
            options={
                'verbose_name': '分享分析',
                'verbose_name_plural': '分享分析',
                'unique_together': {('date', 'platform')},
                'ordering': ['-date'],
            },
        ),
    ]
