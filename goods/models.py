from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    icon = models.CharField(max_length=50, verbose_name='Иконка эмодзи', blank=True)
    slug = models.SlugField(unique=True)
    active = models.BooleanField(default=True, verbose_name='Показывать на сайте')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order']

    def __str__(self):
        return self.name     


class Product(models.Model):
    name = models.CharField(max_length=250, verbose_name='Название товара')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    image = models.ImageField(upload_to='goods/%Y/%m/%d/', verbose_name='Фото')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    stock = models.PositiveIntegerField(default=0, verbose_name='В наличии')
    weight = models.PositiveIntegerField(default=0, verbose_name='Вес в граммах')
    available = models.BooleanField(default=True, verbose_name='Доступен для заказа')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']

    def __str__(self):
        return self.name
    
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created']
        # Один пользователь — один отзыв на товар
        unique_together = ('product', 'author')

    def __str__(self):
        return f'{self.author} — {self.product.name} ({self.rating}★)'

