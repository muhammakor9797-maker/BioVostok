import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings


class Command(BaseCommand):
    help = 'Загружает начальные данные товаров и категорий'

    def handle(self, *args, **options):
        from goods.models import Product, Category
        
        # Базовые категории
        categories_data = [
            {'name': 'Травяные сборы', 'icon': '🌿', 'slug': 'travyanye-sbory', 'order': 1},
            {'name': 'Натуральные масла', 'icon': '🫒', 'slug': 'naturalnye-masla', 'order': 2},
            {'name': 'Мед и продукты пчеловодства', 'icon': '🍯', 'slug': 'med-i-produkty-pchelovodstva', 'order': 3},
            {'name': 'Лечебные грязи', 'icon': '🏔️', 'slug': 'lechebnye-gryazi', 'order': 4},
            {'name': 'Витамины и БАДы', 'icon': '💊', 'slug': 'vitaminy-i-bady', 'order': 5},
            {'name': 'Фиточаи', 'icon': '🍵', 'slug': 'fitochai', 'order': 6},
        ]

        for cat_data in categories_data:
            if not Category.objects.filter(slug=cat_data['slug']).exists():
                Category.objects.create(**cat_data)
                self.stdout.write(f'Категория создана: {cat_data["name"]}')
            else:
                self.stdout.write(f'Категория уже есть: {cat_data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Всего категорий: {Category.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Всего товаров: {Product.objects.count()}'))