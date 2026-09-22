from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from courses.models import Enrollment
from .forms import RegistrationForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to SkillForge! Your account is ready.')
            return redirect('accounts:dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            if user.is_staff:
                return redirect('accounts:dashboard')
            return redirect('home')
    else:
        form = LoginForm(request)
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
@never_cache
def dashboard(request):
    enrollments = Enrollment.objects.all().select_related('course')
    total_enrolled = enrollments.count()
    total_completed = enrollments.filter(completed=True).count()
    avg_progress = 0
    if total_enrolled:
        avg_progress = sum(e.progress for e in enrollments) // total_enrolled

    greeting = 'Good evening'
    hour = timezone.localtime().hour
    if hour < 12:
        greeting = 'Good morning'
    elif hour < 18:
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    context = {
        'enrollments': enrollments,
        'total_enrolled': total_enrolled,
        'total_completed': total_completed,
        'avg_progress': avg_progress,
        'greeting': greeting,
    }
    return render(request, 'dashboard.html', context)
