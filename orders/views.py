from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import OrderCreateForm
from carts.cart import Cart


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            if request.user.is_authenticated:
                order.user = request.user
                order.save()
            for item in cart:
                order.items.create(
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            # Очищаем корзину
            cart.clear()

            # Отправляем уведомление админу
            send_mail(
                subject=f'Новый заказ #{order.id} на сайте!',
                message=f'''
                Поступил новый заказ #{order.id}!
                
                Покупатель: {order.first_name} {order.last_name}
                Телефон: {order.phone}
                Email: {order.email}
                
                Адрес доставки:
                Страна: {order.country}
                Город: {order.city}
                Адрес: {order.address}
                Индекс: {order.postal_code}
                
                Способ доставки: {order.shipping_method}
                Итоговая сумма: {order.get_total_cost()} ₽
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )

            
            # Сохраняем номер заказа в сессии для страницы успешного заказа
            request.session['order_id'] = order.id
            
            return redirect('orders:order_created')

    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/create.html', {'cart': cart, 'form': form})


def order_created(request):
    order_id = request.session.get('order_id')
    order = None
    if order_id:
        from .models import Order
        order = Order.objects.get(id=order_id)
        del request.session['order_id']
    
    return render(request, 'orders/created.html', {'order': order})

