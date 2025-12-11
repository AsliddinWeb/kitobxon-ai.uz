import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.books.models import Book
from .models import ChatSession, Message
from .services.openai_service import AIService


@login_required
def chat_view(request, book_slug):
    """Kitob bilan chat sahifasi"""

    book = get_object_or_404(Book, slug=book_slug)

    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        book=book
    )

    messages = session.messages.all()

    context = {
        'book': book,
        'session': session,
        'messages': messages,
    }
    return render(request, 'ai_chat/chat.html', context)


@login_required
@require_POST
def send_message(request):
    """Xabar yuborish (AJAX)"""

    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': "Xabar bo'sh bo'lmasligi kerak"}, status=400)

        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        book = session.book

        # Foydalanuvchi xabarini saqlash
        Message.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        # Chat tarixini olish
        history = list(session.messages.values('role', 'content'))

        # AI javobini olish
        ai_service = AIService()
        ai_response = ai_service.chat_with_book(
            book_content=book.content_text or book.description,
            user_message=user_message,
            chat_history=history[:-1]
        )

        # AI javobini saqlash
        Message.objects.create(
            session=session,
            role='assistant',
            content=ai_response
        )

        return JsonResponse({
            'success': True,
            'response': ai_response
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def clear_chat(request, session_id):
    """Chat tarixini tozalash"""

    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    session.messages.all().delete()

    return redirect('ai_chat:chat', book_slug=session.book.slug)


@login_required
def chat_history(request):
    """Foydalanuvchi chat tarixi"""

    sessions = ChatSession.objects.filter(user=request.user).select_related('book')

    context = {
        'sessions': sessions,
    }
    return render(request, 'ai_chat/history.html', context)