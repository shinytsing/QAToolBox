# Generated manually to add want features to ShipBao models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tools', '0064_auto_20250823_1526'),
    ]

    operations = [
        # 添加want_count字段到ShipBaoItem
        migrations.AddField(
            model_name='shipbaoitem',
            name='want_count',
            field=models.IntegerField(default=0, verbose_name='想要人数'),
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
        
        # 添加unique_together约束
        migrations.AlterUniqueTogether(
            name='shipbaowantitem',
            unique_together={('user', 'item')},
        ),
    ]
