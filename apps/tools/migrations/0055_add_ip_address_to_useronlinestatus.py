# Generated manually to add ip_address field to UserOnlineStatus

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0053_fix_existing_chatmessage_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='useronlinestatus',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址'),
        ),
    ]
