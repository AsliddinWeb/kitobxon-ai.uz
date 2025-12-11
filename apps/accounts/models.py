from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Kengaytirilgan foydalanuvchi modeli"""

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Bio'
    )
    reading_goal = models.PositiveIntegerField(
        default=20,
        verbose_name="Kunlik o'qish maqsadi (sahifa)"
    )
    total_books_read = models.PositiveIntegerField(
        default=0,
        verbose_name="Jami o'qilgan kitoblar"
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        verbose_name='Joriy streak'
    )
    points = models.PositiveIntegerField(
        default=0,
        verbose_name='Ballar'
    )

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.username

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'