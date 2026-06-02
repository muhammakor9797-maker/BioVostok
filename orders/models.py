from django.conf import settings
from django.db import models
from goods.models import Product


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название доставки')
    icon = models.CharField(max_length=50, verbose_name='Иконка', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость')
    min_days = models.PositiveIntegerField(verbose_name='Мин срок дней')
    max_days = models.PositiveIntegerField(verbose_name='Макс срок дней')
    available_worldwide = models.BooleanField(default=False, verbose_name='Доступно по всему миру')
    active = models.BooleanField(default=True, verbose_name='Включено')

    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'
        ordering = ['price']

    def __str__(self):
        return self.name


class Order(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    address = models.CharField(max_length=250, verbose_name='Адрес')
    postal_code = models.CharField(max_length=20, verbose_name='Почтовый индекс')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT, verbose_name='Способ доставки')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False, verbose_name='Оплачено')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created']

    def __str__(self):
        return f'Заказ №{self.id}'

    def get_total_cost(self):
        items_cost = sum(item.get_cost() for item in self.items.all())
        shipping_price = self.shipping_method.price if self.shipping_method else 0
        return items_cost + shipping_price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

