from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser


class RegisterView(CreateView):
    """Ro'yxatdan o'tish"""

    model = CustomUser
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Ro'yxatdan muvaffaqiyatli o'tdingiz! Endi kirishingiz mumkin.")
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('books:home')
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """Kirish"""

    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"Xush kelibsiz, {form.get_user().username}!")
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('books:home')
        return super().dispatch(request, *args, **kwargs)


def logout_view(request):
    """Chiqish"""

    logout(request)
    messages.info(request, 'Tizimdan chiqdingiz.')
    return redirect('books:home')


@login_required
def profile_view(request):
    """Profil ko'rish va tahrirlash"""

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil yangilandi!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)