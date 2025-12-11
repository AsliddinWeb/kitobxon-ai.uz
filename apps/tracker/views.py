from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone

from apps.accounts.models import CustomUser
from apps.books.models import Book
from .models import ReadingSession, Achievement, UserAchievement, DailyStreak


@login_required
def dashboard_view(request):
    """Foydalanuvchi dashboard"""

    user = request.user

    # O'qish statistikasi
    reading_sessions = ReadingSession.objects.filter(user=user)
    total_pages = reading_sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0
    completed_books = reading_sessions.filter(completed=True).count()
    in_progress = reading_sessions.filter(completed=False).select_related('book')

    # Yutuqlar
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')

    # Streak
    streak = DailyStreak.objects.filter(user=user).order_by('-date')[:7]

    context = {
        'total_pages': total_pages,
        'completed_books': completed_books,
        'in_progress': in_progress,
        'user_achievements': user_achievements,
        'streak': streak,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def leaderboard_view(request):
    """Reyting jadvali"""

    # Top foydalanuvchilar
    top_users = CustomUser.objects.order_by('-points')[:20]

    # Foydalanuvchi o'rni
    user_rank = CustomUser.objects.filter(points__gt=request.user.points).count() + 1

    context = {
        'top_users': top_users,
        'user_rank': user_rank,
    }
    return render(request, 'tracker/leaderboard.html', context)


@login_required
def update_progress(request):
    """O'qish progressini yangilash (AJAX)"""

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        current_page = int(request.POST.get('current_page', 0))

        book = get_object_or_404(Book, id=book_id)

        session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book
        )

        # Yangi o'qilgan sahifalar
        new_pages = current_page - session.current_page
        if new_pages > 0:
            session.pages_read += new_pages

        session.current_page = current_page

        # Kitob tugatildimi
        if current_page >= book.pages:
            session.completed = True
            session.completed_at = timezone.now()
            request.user.total_books_read += 1
            request.user.save()

        session.save()

        # Kunlik streak yangilash
        today = timezone.now().date()
        daily, created = DailyStreak.objects.get_or_create(
            user=request.user,
            date=today
        )
        if new_pages > 0:
            daily.pages_read += new_pages
            daily.save()

        return JsonResponse({
            'success': True,
            'progress': session.progress_percentage
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def start_reading(request, book_slug):
    """Kitobni o'qishni boshlash"""

    book = get_object_or_404(Book, slug=book_slug)

    session, created = ReadingSession.objects.get_or_create(
        user=request.user,
        book=book
    )

    return JsonResponse({
        'success': True,
        'session_id': session.id,
        'current_page': session.current_page
    })