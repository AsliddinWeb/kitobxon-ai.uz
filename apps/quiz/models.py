from django.db import models
from django.conf import settings


class Quiz(models.Model):
    """Test"""

    book = models.ForeignKey(
        'books.Book',
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name='Kitob'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Test nomi'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Testlar'

    def __str__(self):
        return self.title


class Question(models.Model):
    """Savol"""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Test'
    )
    question_text = models.TextField(
        verbose_name='Savol'
    )
    option_a = models.CharField(
        max_length=300,
        verbose_name='A variant'
    )
    option_b = models.CharField(
        max_length=300,
        verbose_name='B variant'
    )
    option_c = models.CharField(
        max_length=300,
        verbose_name='C variant'
    )
    option_d = models.CharField(
        max_length=300,
        verbose_name='D variant'
    )
    correct_answer = models.IntegerField(
        choices=[(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')],
        verbose_name="To'g'ri javob"
    )
    explanation = models.TextField(
        blank=True,
        verbose_name='Tushuntirish'
    )

    class Meta:
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'

    def __str__(self):
        return self.question_text[:50]


class QuizAttempt(models.Model):
    """Test urinishi"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name='Foydalanuvchi'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Test'
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name='Ball'
    )
    total_questions = models.PositiveIntegerField(
        default=0,
        verbose_name='Jami savollar'
    )
    completed = models.BooleanField(
        default=False,
        verbose_name='Tugatildi'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Test urinishi'
        verbose_name_plural = 'Test urinishlari'

    @property
    def percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.percentage}%)"


class UserAnswer(models.Model):
    """Foydalanuvchi javobi"""

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Urinish'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Savol'
    )
    selected_answer = models.IntegerField(
        verbose_name='Tanlangan javob'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="To'g'ri"
    )

    class Meta:
        verbose_name = 'Foydalanuvchi javobi'
        verbose_name_plural = 'Foydalanuvchi javoblari'

    def __str__(self):
        return f"{self.attempt.user.username} - {self.question}"
