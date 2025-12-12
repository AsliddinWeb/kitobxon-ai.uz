from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.books.models import Book
from apps.ai_chat.services.openai_service import AIService
from .models import Summary


@login_required
def summary_view(request, book_slug):
    """Kitob summarisi sahifasi"""

    book = get_object_or_404(Book, slug=book_slug)
    summary = Summary.objects.filter(book=book).first()

    context = {
        'book': book,
        'summary': summary,
    }
    return render(request, 'summarizer/summary.html', context)


@login_required
def generate_summary(request, book_slug):
    """Summary generatsiya qilish (AJAX)"""

    book = get_object_or_404(Book, slug=book_slug)

    # AI orqali summary yaratish
    ai_service = AIService()
    summary_text = ai_service.generate_summary(book=book)

    # Saqlash
    summary, created = Summary.objects.update_or_create(
        book=book,
        defaults={
            'content': summary_text,
            'user': request.user
        }
    )

    return JsonResponse({
        'success': True,
        'summary': summary_text
    })