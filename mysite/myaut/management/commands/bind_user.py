
from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=1)  # Получаем пользователя с id=1
        group, created = Group.objects.get_or_create(name='profile_manager', )
        permission_profile = Permission.objects.get(codename='view_profile',)  # Получаем разрешение
        permission_logentry = Permission.objects.get(codename='view_logentry',)  # Получаем разрешение

          # Добавляем разрешение в группу
        group.permissions.add(permission_profile)

        # Присоединение пользователя к группе
        user.groups.add(group)

        # Связать пользователя напрямую с разрешением
        user.user_permissions.add(permission_logentry)

        group.save()
        user.save()