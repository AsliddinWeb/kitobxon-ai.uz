from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from apps.books.models import Book
from apps.ai_chat.services.openai_service import AIService
from .models import Quiz, Question, QuizAttempt, UserAnswer


@login_required
def quiz_start(request, book_slug):
    """Test boshlash sahifasi"""

    book = get_object_or_404(Book, slug=book_slug)
    quiz = Quiz.objects.filter(book=book).first()

    context = {
        'book': book,
        'quiz': quiz,
    }
    return render(request, 'quiz/quiz_start.html', context)


@login_required
def generate_quiz(request, book_slug):
    """Quiz generatsiya qilish (AJAX)"""

    book = get_object_or_404(Book, slug=book_slug)

    # AI orqali savollar yaratish
    ai_service = AIService()
    questions_data = ai_service.generate_quiz(
        book_content=book.content_text or book.description,
        num_questions=5
    )

    if not questions_data:
        return JsonResponse({'error': 'Savollar yaratishda xatolik'}, status=500)

    # Quiz yaratish
    quiz, created = Quiz.objects.update_or_create(
        book=book,
        defaults={'title': f"{book.title} - Test"}
    )

    # Eski savollarni o'chirish
    quiz.questions.all().delete()

    # Yangi savollarni qo'shish
    for q_data in questions_data:
        options = q_data.get('options', ['', '', '', ''])
        Question.objects.create(
            quiz=quiz,
            question_text=q_data.get('question', ''),
            option_a=options[0] if len(options) > 0 else '',
            option_b=options[1] if len(options) > 1 else '',
            option_c=options[2] if len(options) > 2 else '',
            option_d=options[3] if len(options) > 3 else '',
            correct_answer=q_data.get('correct', 0),
            explanation=q_data.get('explanation', '')
        )

    return JsonResponse({'success': True, 'quiz_id': quiz.id})


@login_required
def take_quiz(request, quiz_id):
    """Testni yechish"""

    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    if request.method == 'POST':
        # Javoblarni tekshirish
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            total_questions=questions.count()
        )

        score = 0
        for question in questions:
            answer_key = f'question_{question.id}'
            selected = request.POST.get(answer_key)

            if selected is not None:
                selected = int(selected)
                is_correct = (selected == question.correct_answer)

                if is_correct:
                    score += 1

                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected,
                    is_correct=is_correct
                )

        attempt.score = score
        attempt.completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # Foydalanuvchi ballarini yangilash
        request.user.points += score * 10
        request.user.save()

        return redirect('quiz:result', attempt_id=attempt.id)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quiz/take_quiz.html', context)


@login_required
def quiz_result(request, attempt_id):
    """Test natijasi"""

    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = attempt.answers.select_related('question').all()

    context = {
        'attempt': attempt,
        'answers': answers,
    }
    return render(request, 'quiz/quiz_result.html', context)
