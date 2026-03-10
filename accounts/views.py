from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from transport.models import FavoriteRoute, FavoriteStop
from .forms import RegisterForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('transport:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to BakuGo, {user.username}!")
            return redirect('transport:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('transport:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/')
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out.")
    return redirect('transport:home')


@login_required
def profile_view(request):
    user = request.user
    favorite_routes = FavoriteRoute.objects.filter(user=user).select_related('route').order_by('-created_at')
    favorite_stops = FavoriteStop.objects.filter(user=user).select_related('stop').order_by('-created_at')

    return render(request, 'accounts/profile.html', {
        'user': user,
        'favorite_routes': favorite_routes,
        'favorite_stops': favorite_stops,
    })
