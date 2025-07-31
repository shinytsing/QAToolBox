from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserRole

@receiver(post_save, sender=User)
def create_user_role(sender, instance, created, **kwargs):
    """当创建新用户时，自动创建用户角色"""
    if created:
        UserRole.objects.create(user=instance, role='user')

@receiver(post_save, sender=User)
def save_user_role(sender, instance, **kwargs):
    """保存用户角色"""
    try:
        instance.role.save()
    except UserRole.DoesNotExist:
        UserRole.objects.create(user=instance, role='user') 