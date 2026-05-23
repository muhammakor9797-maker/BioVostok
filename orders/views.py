import logging
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import OrderCreateForm
from carts.cart import Cart

logger = logging.getLogger(__name__)


def send_telegram_notification(order):
    """Отправляет уведомление о новом заказе в Telegram"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    items_list = "\n".join([
        f"  • {item.product.name} x{item.quantity} = {item.get_cost()} ₽"
        for item in order.items.all()
    ])
    
    message = f"""
🆕 <b>Новый заказ #{order.id}!</b>

👤 <b>Покупатель:</b>
  {order.first_name} {order.last_name}
  📞 {order.phone}
  📧 {order.email}

📍 <b>Адрес доставки:</b>
  {order.country}, {order.city}
  {order.address}
  📮 {order.postal_code}

🚚 <b>Способ доставки:</b> {order.shipping_method}

📦 <b>Товары:</b>
{items_list}

💰 <b>Итоговая сумма:</b> {order.get_total_cost()} ₽
"""
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }
    
    try:
        response = requests.post(url, data=data, timeout=5)
        if not response.ok:
            logger.error(f"Telegram API error: {response.text}")
    except Exception:
        logger.exception("Ошибка отправки уведомления в Telegram")


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

            # Отправляем в Telegram
            send_telegram_notification(order)
            
            # Отправляем email (если получится - хорошо, если нет - не критично)
            try:
                send_mail(
                    subject=f'Новый заказ #{order.id} на сайте!',
                    message=f'''
                    Поступил новый заказ #{order.id}!                    
                    Покупатель: {order.first_name} {order.last_name}
                    Телефон: {order.phone}
                    Email: {order.email}
                    Итоговая сумма: {order.get_total_cost()} ₽
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL, settings.ORDERS_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass  # Email не обязателен, Telegram важнее

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
