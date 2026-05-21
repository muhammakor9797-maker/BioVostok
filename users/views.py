from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
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