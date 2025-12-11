from django.db import models
from django.conf import settings


class ReadingSession(models.Model):
    """O'qish sessiyasi"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reading_sessions',
        verbose_name='Foydalanuvchi'
    )
    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='reading_sessions',
        verbose_name='Kitob'
    )
    pages_read = models.PositiveIntegerField(
        default=0,
        verbose_name="O'qilgan sahifalar"
    )
    current_page = models.PositiveIntegerField(
        default=0,
        verbose_name='Joriy sahifa'
    )
    completed = models.BooleanField(
        default=False,
        verbose_name='Tugatildi'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "O'qish sessiyasi"
        verbose_name_plural = "O'qish sessiyalari"
        unique_together = ['user', 'book']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    @property
    def progress_percentage(self):
        if self.book.pages == 0:
            return 0
        return round((self.current_page / self.book.pages) * 100)


class Achievement(models.Model):
    """Yutuq"""

    CONDITION_CHOICES = [
        ('books_read', "O'qilgan kitoblar soni"),
        ('streak_days', 'Streak kunlar'),
        ('total_pages', 'Jami sahifalar'),
        ('quiz_score', 'Test ballari'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Yutuq nomi'
    )
    description = models.TextField(
        verbose_name='Tavsif'
    )
    icon = models.CharField(
        max_length=50,
        verbose_name='Icon (emoji)'
    )
    points = models.PositiveIntegerField(
        default=10,
        verbose_name='Ball'
    )
    condition_type = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICES,
        verbose_name='Shart turi'
    )
    condition_value = models.PositiveIntegerField(
        verbose_name='Shart qiymati'
    )

    class Meta:
        verbose_name = 'Yutuq'
        verbose_name_plural = 'Yutuqlar'

    def __str__(self):
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """Foydalanuvchi yutuqlari"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Foydalanuvchi'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        verbose_name='Yutuq'
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Foydalanuvchi yutuqi'
        verbose_name_plural = 'Foydalanuvchi yutuqlari'
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class DailyStreak(models.Model):
    """Kunlik streak"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_streaks',
        verbose_name='Foydalanuvchi'
    )
    date = models.DateField(
        verbose_name='Sana'
    )
    pages_read = models.PositiveIntegerField(
        default=0,
        verbose_name="O'qilgan sahifalar"
    )

    class Meta:
        verbose_name = 'Kunlik streak'
        verbose_name_plural = 'Kunlik streaklar'
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"