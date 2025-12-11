from django.db import models
from django.conf import settings


class Summary(models.Model):
    """Kitob summarisi"""

    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='summaries',
        verbose_name='Kitob'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='summaries',
        null=True,
        blank=True,
        verbose_name='Foydalanuvchi'
    )
    content = models.TextField(
        verbose_name='Summary matni'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summarylar'
        ordering = ['-created_at']

    def __str__(self):
        return f"Summary: {self.book.title}"