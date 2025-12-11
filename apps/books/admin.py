from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.html import format_html
from .models import Book, Category, Author


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'birth_year', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'pages', 'content_status', 'is_featured', 'created_at']
    list_filter = ['category', 'language', 'is_featured', 'created_at']
    search_fields = ['title', 'author__name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured']
    readonly_fields = ['views', 'created_at', 'updated_at', 'ai_generate_button']

    fieldsets = (
        ('Asosiy', {
            'fields': ('title', 'slug', 'author', 'category', 'description')
        }),
        ('Fayllar', {
            'fields': ('cover', 'pdf_file')
        }),
        ("Qo'shimcha", {
            'fields': ('pages', 'language', 'published_year', 'is_featured')
        }),
        ('AI Content', {
            'fields': ('ai_generate_button', 'content_text'),
            'description': 'PDF yoki description asosida AI content yaratish'
        }),
        ('Statistika', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_status(self, obj):
        """Content mavjudligini ko'rsatish"""
        if obj.content_text:
            length = len(obj.content_text)
            return format_html(
                '<span style="color: green;">✅ {} belgi</span>',
                length
            )
        return format_html('<span style="color: red;">❌ Bo\'sh</span>')

    content_status.short_description = 'AI Content'

    def ai_generate_button(self, obj):
        """AI Generate tugmasi"""
        if obj.pk:
            return format_html(
                '<a class="button" href="{}generate-content/" style="padding: 10px 20px; background: #059669; color: white; '
                'text-decoration: none; border-radius: 5px; font-weight: bold;">'
                '🤖 AI bilan Content Yaratish</a>'
                '<p style="margin-top: 10px; color: #666; font-size: 12px;">'
                'PDF fayl yoki description asosida kitob contentini avtomatik yaratadi</p>',
                f'/admin/books/book/{obj.pk}/'
            )
        return "Avval kitobni saqlang"

    ai_generate_button.short_description = 'AI Generate'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:book_id>/generate-content/',
                self.admin_site.admin_view(self.generate_content_view),
                name='book-generate-content',
            ),
        ]
        return custom_urls + urls

    def generate_content_view(self, request, book_id):
        """AI orqali content yaratish"""
        book = get_object_or_404(Book, pk=book_id)

        try:
            from apps.ai_chat.services.openai_service import AIService
            ai_service = AIService()

            # PDF mavjud bo'lsa - undan text olish
            source_text = ""
            if book.pdf_file:
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(book.pdf_file.path)
                    pdf_text = ""
                    for page in reader.pages[:50]:  # Birinchi 50 sahifa
                        pdf_text += page.extract_text() + "\n"
                    source_text = pdf_text[:15000]  # Max 15000 belgi
                except Exception as e:
                    source_text = book.description
            else:
                source_text = book.description

            # AI orqali content yaratish
            content = ai_service.generate_book_content(
                title=book.title,
                author=book.author.name,
                source_text=source_text
            )

            # Saqlash
            book.content_text = content
            book.save()

            messages.success(request, f'✅ "{book.title}" uchun AI content muvaffaqiyatli yaratildi!')

        except Exception as e:
            messages.error(request, f'❌ Xatolik: {str(e)}')

        return redirect(f'/admin/books/book/{book_id}/change/')