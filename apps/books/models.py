from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Kitob kategoriyasi"""

    name = models.CharField(
        max_length=100,
        verbose_name='Kategoriya nomi'
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text='Emoji yoki icon class'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Tavsif'
    )

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    """Muallif"""

    name = models.CharField(
        max_length=200,
        verbose_name='Ism'
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Biografiya'
    )
    photo = models.ImageField(
        upload_to='authors/',
        blank=True,
        null=True,
        verbose_name='Rasm'
    )
    birth_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tug'ilgan yili"
    )

    class Meta:
        verbose_name = 'Muallif'
        verbose_name_plural = 'Mualliflar'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(models.Model):
    """Kitob modeli"""

    LANGUAGE_CHOICES = [
        ('uzbek', "O'zbek"),
        ('russian', 'Rus'),
        ('english', 'Ingliz'),
    ]

    # Asosiy ma'lumotlar
    title = models.CharField(
        max_length=300,
        verbose_name='Kitob nomi'
    )
    slug = models.SlugField(
        unique=True,
        blank=True
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name='Muallif'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='Kategoriya'
    )
    description = models.TextField(
        verbose_name='Tavsif'
    )

    # Fayllar
    cover = models.ImageField(
        upload_to='covers/',
        verbose_name='Muqova'
    )
    pdf_file = models.FileField(
        upload_to='books/',
        blank=True,
        null=True,
        verbose_name='PDF fayl'
    )

    # Qo'shimcha ma'lumotlar
    pages = models.PositiveIntegerField(
        default=0,
        verbose_name='Sahifalar soni'
    )
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default='uzbek',
        verbose_name='Til'
    )
    published_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Nashr yili'
    )

    # AI uchun
    content_text = models.TextField(
        blank=True,
        verbose_name='Kitob matni (AI uchun)'
    )

    # Statistika
    views = models.PositiveIntegerField(
        default=0,
        verbose_name="Ko'rishlar"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Tavsiya etilgan'
    )

    # Vaqt
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kitob'
        verbose_name_plural = 'Kitoblar'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])