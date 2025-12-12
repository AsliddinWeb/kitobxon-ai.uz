from django.db import models
from django.conf import settings
import uuid


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


class BookComparison(models.Model):
    """Kitoblar taqqoslashlari"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_comparisons',
        verbose_name='Foydalanuvchi'
    )
    book1 = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='comparisons_as_book1',
        verbose_name='Birinchi kitob'
    )
    book2 = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='comparisons_as_book2',
        verbose_name='Ikkinchi kitob'
    )
    comparison_html = models.TextField(
        verbose_name='Taqqoslash HTML',
        help_text='AI tomonidan yaratilgan taqqoslash matni (HTML format)'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Ko\'rishlar soni'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Yangilangan vaqt'
    )

    class Meta:
        verbose_name = 'Kitoblar taqqoslashi'
        verbose_name_plural = 'Kitoblar taqqoslashlari'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['book1', 'book2']),
        ]

    def __str__(self):
        return f"{self.book1.title} vs {self.book2.title}"

    def increment_views(self):
        """Ko'rishlar sonini oshirish"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @classmethod
    def get_or_create_comparison(cls, user, book1, book2, ai_service):
        """
        Taqqoslashni olish yoki yangi yaratish.
        Agar avval taqqoslash bo'lgan bo'lsa, uni qaytaradi.
        """
        # Oldinroq mavjud taqqoslashni tekshirish (har ikki yo'nalishda)
        existing = cls.objects.filter(
            models.Q(book1=book1, book2=book2) | models.Q(book1=book2, book2=book1)
        ).first()

        if existing:
            # Ko'rishlar sonini oshirish
            existing.increment_views()
            return existing, False  # False = yangi yaratilmadi

        # Yangi taqqoslash yaratish
        comparison_html = ai_service.compare_books(book1, book2)

        new_comparison = cls.objects.create(
            user=user,
            book1=book1,
            book2=book2,
            comparison_html=comparison_html
        )

        return new_comparison, True  # True = yangi yaratildi
