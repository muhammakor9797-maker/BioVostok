import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Загружает товары из дампа при деплое'

    def handle(self, *args, **options):
        dump_path = 'data_dump.json'
        if not os.path.exists(dump_path):
            self.stdout.write('Файл data_dump.json не найден')
            return

        with open(dump_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Загружаем только goods
        from django.core import serializers
        goods_data = [d for d in data if 'goods' in d.get('model', '')]
        
        if not goods_data:
            self.stdout.write('Нет данных товаров для загрузки')
            return

        for obj_data in goods_data:
            model = apps.get_model(obj_data['model'])
            pk = obj_data['pk']
            fields = obj_data['fields']
            
            if model.objects.filter(pk=pk).exists():
                model.objects.filter(pk=pk).update(**fields)
                self.stdout.write(f'Обновлён: {obj_data["model"]} #{pk}')
            else:
                model.objects.create(pk=pk, **fields)
                self.stdout.write(f'Создан: {obj_data["model"]} #{pk}')

        self.stdout.write(self.style.SUCCESS(f'Загружено {len(goods_data)} записей товаров'))