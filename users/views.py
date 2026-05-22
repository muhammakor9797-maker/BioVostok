from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from .forms import RegisterForm
from orders.models import Order


class CustomLoginView(LoginView):
    template_name = 'users/login.html'


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')
    else:
        form = RegisterForm()
    return render(request, 'users/registration.html', {'form': form})


def setup_admin_view(request):
    """
    ВРЕМЕННЫЙ эндпоинт для создания суперпользователя на сервере Render.
    Перейти: https://biovostok.onrender.com/setup-admin/
    После использования УДАЛИТЬ этот код и запушть заново!
    """
    User = get_user_model()
    username = 'admin'
    password = 'REMOVED'
    email = 'admin@admin.com'
    
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        msg = f'SUPERUSER UPDATED: {username} / {password}'
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        msg = f'SUPERUSER CREATED: {username} / {password}'
    
    return HttpResponse(f'<h1>{msg}</h1><a href="/admin/">Go to Admin</a>')


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    total_orders = orders.count()
    total_spent = sum(order.get_total_cost() for order in orders)
    return render(request, 'users/profile.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
    })