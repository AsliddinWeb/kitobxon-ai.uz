import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from apps.books.models import Book
from .models import ChatSession, Message, BookComparison, Recommendation
from .services.openai_service import AIService


@login_required
def chat_view(request, book_slug):
    """Kitob bilan chat sahifasi"""
    book = get_object_or_404(Book, slug=book_slug)

    session, created = ChatSession.objects.get_or_create(
        user=request.user,
        book=book
    )

    chat_messages = session.messages.all()

    context = {
        'book': book,
        'session': session,
        'messages': chat_messages,
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

        # AI javobini olish
        ai_service = AIService()
        ai_response = ai_service.chat_with_book(
            book=book,
            user_message=user_message
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
    """
    Foydalanuvchining barcha AI faoliyatlari tarixi:
    - Chat sessiyalari (kitob bilan suhbat)
    - Kitob taqqoslashlari
    - Kitob tavsiyalari
    """
    user = request.user

    # Chat sessiyalari (faqat xabarlari borlarini)
    chat_sessions = ChatSession.objects.filter(
        user=user,
        messages__isnull=False
    ).select_related('book', 'book__author').distinct()

    # Kitob taqqoslashlari
    comparisons = BookComparison.objects.filter(
        user=user
    ).select_related('book1', 'book2')

    # Kitob tavsiyalari
    recommendations = Recommendation.objects.filter(user=user)

    # Statistika
    stats = {
        'total_chats': chat_sessions.count(),
        'total_comparisons': comparisons.count(),
        'total_recommendations': recommendations.count(),
        'total_messages': Message.objects.filter(session__user=user).count(),
    }

    context = {
        'chat_sessions': chat_sessions[:10],
        'comparisons': comparisons[:10],
        'recommendations': recommendations[:10],
        'stats': stats,
    }
    return render(request, 'ai_chat/history.html', context)


# ============== KITOB TAQQOSLASH ==============

@login_required
def compare_view(request):
    """Kitoblarni taqqoslash sahifasi"""
    books = Book.objects.select_related('author').all()

    if request.method == 'POST':
        book1_id = request.POST.get('book1')
        book2_id = request.POST.get('book2')

        if book1_id and book2_id:
            if book1_id == book2_id:
                messages.error(request, "Iltimos, 2 ta turli kitob tanlang!")
            else:
                book1 = get_object_or_404(Book, id=book1_id)
                book2 = get_object_or_404(Book, id=book2_id)

                ai_service = AIService()

                # Taqqoslashni olish yoki yaratish
                comparison_obj, created = BookComparison.get_or_create_comparison(
                    user=request.user,
                    book1=book1,
                    book2=book2,
                    ai_service=ai_service
                )

                if created:
                    messages.success(request, "Taqqoslash muvaffaqiyatli yaratildi!")
                else:
                    messages.info(request, "Bu taqqoslash avval yaratilgan.")

                return redirect('ai_chat:comparison_detail', comparison_id=comparison_obj.id)

    context = {
        'books': books,
    }
    return render(request, 'ai_chat/compare.html', context)


@login_required
def comparison_detail_view(request, comparison_id):
    """Taqqoslash detallari sahifasi"""
    comparison = get_object_or_404(BookComparison, id=comparison_id)

    # Ko'rishlar sonini oshirish (faqat boshqa foydalanuvchilar uchun)
    if comparison.user != request.user:
        comparison.increment_views()

    context = {
        'comparison_obj': comparison,
        'comparison': comparison.comparison_html,
        'book1': comparison.book1,
        'book2': comparison.book2,
    }
    return render(request, 'ai_chat/comparison_detail.html', context)


@login_required
def my_comparisons_view(request):
    """Foydalanuvchining barcha taqqoslashlari"""
    comparisons = BookComparison.objects.filter(
        user=request.user
    ).select_related('book1', 'book2')

    context = {
        'comparisons': comparisons,
    }
    return render(request, 'ai_chat/my_comparisons.html', context)


@login_required
def delete_comparison_view(request, comparison_id):
    """Taqqoslashni o'chirish"""
    comparison = get_object_or_404(BookComparison, id=comparison_id, user=request.user)

    if request.method == 'POST':
        comparison.delete()
        messages.success(request, "Taqqoslash muvaffaqiyatli o'chirildi!")
        return redirect('ai_chat:my_comparisons')

    return redirect('ai_chat:comparison_detail', comparison_id=comparison_id)


# ============== KITOB TAVSIYA ==============

@login_required
def recommend_view(request):
    """AI kitob tavsiya sahifasi"""
    recommendation = None
    user_request = None

    # Foydalanuvchining oldingi tavsiyalari
    past_recommendations = Recommendation.objects.filter(user=request.user)[:5]

    if request.method == 'POST':
        user_request = request.POST.get('user_request', '').strip()

        if user_request:
            ai_service = AIService()
            response_html = ai_service.recommend_books(user_request)

            # Bazaga saqlash
            recommendation = Recommendation.objects.create(
                user=request.user,
                request_text=user_request,
                response_html=response_html
            )
        else:
            messages.error(request, "Iltimos, qanday kitob kerakligini yozing!")

    context = {
        'recommendation': recommendation,
        'user_request': user_request,
        'past_recommendations': past_recommendations,
    }
    return render(request, 'ai_chat/recommend.html', context)


@login_required
def delete_recommendation_view(request, pk):
    """Tavsiyani o'chirish"""
    recommendation = get_object_or_404(Recommendation, pk=pk, user=request.user)

    if request.method == 'POST':
        recommendation.delete()
        messages.success(request, "Tavsiya o'chirildi!")
        return redirect('ai_chat:history')

    return redirect('ai_chat:history')