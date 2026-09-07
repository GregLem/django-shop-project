
from django.contrib.auth.models import User 
from django.db import models


def user_avatar_directory_path(instance: "Profile", filename: str) -> str:
    return f"users/user_{instance.user.pk}/avatars/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=200, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(
        upload_to=user_avatar_directory_path,
        null=True,
        blank=True,
        verbose_name="Аватар"
    )
    
    def __str__(self):
        return self.user.username