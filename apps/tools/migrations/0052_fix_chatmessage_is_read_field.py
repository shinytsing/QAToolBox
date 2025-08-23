# Generated manually to fix ChatMessage is_read field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0051_fix_chatmessage_model_fields'),
    ]

    operations = [
        # 修改is_read字段，添加默认值
        migrations.AlterField(
            model_name='chatmessage',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='是否已读'),
        ),
    ]
