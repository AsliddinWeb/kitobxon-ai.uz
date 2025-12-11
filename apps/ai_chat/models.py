from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """Suhbat sessiyasi"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='Foydalanuvchi'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='Kitob'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chat sessiya'
        verbose_name_plural = 'Chat sessiyalar'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"


class Message(models.Model):
    """Xabar"""

    ROLE_CHOICES = [
        ('user', 'Foydalanuvchi'),
        ('assistant', 'AI'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Sessiya'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='Rol'
    )
    content = models.TextField(
        verbose_name='Xabar'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Xabar'
        verbose_name_plural = 'Xabarlar'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."