# Generated manually to fix existing ChatMessage is_read values

from django.db import migrations


def set_default_is_read(apps, schema_editor):
    """为现有的ChatMessage记录设置is_read默认值"""
    db_alias = schema_editor.connection.alias
    
    # 使用原始SQL更新所有is_read为NULL的记录
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "UPDATE tools_chatmessage SET is_read = FALSE WHERE is_read IS NULL"
        )


def reverse_set_default_is_read(apps, schema_editor):
    """回滚操作 - 不做任何事情"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0052_fix_chatmessage_is_read_field'),
    ]

    operations = [
        migrations.RunPython(set_default_is_read, reverse_set_default_is_read),
    ]
