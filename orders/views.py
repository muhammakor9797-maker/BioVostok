import json
import logging
import urllib.request
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import OrderCreateForm
from carts.cart import Cart

logger = logging.getLogger(__name__)


def send_telegram_notification(order):
    """Отправляет уведомление о новом заказе в Telegram (через urllib - легче)"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    items_list = "\n".join([
        f"  • {item.product.name} x{item.quantity} = {item.get_cost()} ₽"
        for item in order.items.all()
    ])
    
    message = (
        f"🆕 <b>Новый заказ #{order.id}!</b>\n\n"
        f"👤 <b>Покупатель:</b>\n"
        f"  {order.first_name} {order.last_name}\n"
        f"  📞 {order.phone}\n"
        f"  📧 {order.email}\n\n"
        f"📍 <b>Адрес доставки:</b>\n"
        f"  {order.country}, {order.city}\n"
        f"  {order.address}\n"
        f"  📮 {order.postal_code}\n\n"
        f"🚚 <b>Способ доставки:</b> {order.shipping_method}\n\n"
        f"📦 <b>Товары:</b>\n"
        f"{items_list}\n\n"
        f"💰 <b>Итоговая сумма:</b> {order.get_total_cost()} ₽"
    )
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                logger.error(f"Telegram API error: {response.read().decode()}")
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

            # Отправляем уведомление в Telegram
            send_telegram_notification(order)

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
