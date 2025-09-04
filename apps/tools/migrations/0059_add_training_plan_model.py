# Generated manually for TrainingPlan model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tools', '0058_add_missing_data_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='计划名称')),
                ('mode', models.CharField(default='五分化', max_length=50, verbose_name='训练模式')),
                ('cycle_weeks', models.IntegerField(default=8, verbose_name='周期(周)')),
                ('week_schedule', models.JSONField(default=list, verbose_name='周安排')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('visibility', models.CharField(
                    choices=[('private', '私有'), ('public', '公开')], 
                    default='private', 
                    max_length=10, 
                    verbose_name='可见性'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '训练计划',
                'verbose_name_plural': '训练计划',
                'ordering': ['-updated_at'],
                'indexes': [
                    models.Index(fields=['user', 'is_active'], name='tools_trainingplan_user_active_idx'),
                ],
            },
        ),
    ]
