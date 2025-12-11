from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Book, Category, Author


def home_view(request):
    """Bosh sahifa"""

    featured_books = Book.objects.filter(is_featured=True)[:6]
    latest_books = Book.objects.all()[:8]
    categories = Category.objects.all()[:6]

    context = {
        'featured_books': featured_books,
        'latest_books': latest_books,
        'categories': categories,
    }
    return render(request, 'books/home.html', context)


def book_list_view(request):
    """Barcha kitoblar ro'yxati"""

    books = Book.objects.select_related('author', 'category').all()
    categories = Category.objects.all()

    # Qidiruv
    query = request.GET.get('q')
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(description__icontains=query)
        )

    # Kategoriya filter
    category_slug = request.GET.get('category')
    if category_slug:
        books = books.filter(category__slug=category_slug)

    context = {
        'books': books,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    }
    return render(request, 'books/book_list.html', context)


def book_detail_view(request, slug):
    """Kitob tafsilotlari"""

    book = get_object_or_404(Book, slug=slug)
    book.increment_views()

    # O'xshash kitoblar
    related_books = Book.objects.filter(
        category=book.category
    ).exclude(id=book.id)[:4]

    # Reading session (agar foydalanuvchi login bo'lsa)
    reading_session = None
    if request.user.is_authenticated:
        from apps.tracker.models import ReadingSession
        reading_session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book
        )

    context = {
        'book': book,
        'related_books': related_books,
        'reading_session': reading_session,
    }
    return render(request, 'books/book_detail.html', context)


def category_list_view(request):
    """Kategoriyalar ro'yxati"""

    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    return render(request, 'books/category_list.html', context)


def category_detail_view(request, slug):
    """Kategoriya bo'yicha kitoblar"""

    category = get_object_or_404(Category, slug=slug)
    books = Book.objects.filter(category=category)

    context = {
        'category': category,
        'books': books,
    }
    return render(request, 'books/category_detail.html', context)


def author_detail_view(request, slug):
    """Muallif sahifasi"""

    author = get_object_or_404(Author, slug=slug)
    books = author.books.all()

    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'books/author_detail.html', context)
