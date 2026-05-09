from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Количество товаров'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_image', 'name', 'slug', 'price', 
        'weight', 'stock', 'available', 'created'
    ]
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'weight', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    raw_id_fields = ['category']
    readonly_fields = ['created', 'updated']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Цена и доставка', {
            'fields': ('price', 'weight')
        }),
        ('Наличие', {
            'fields': ('stock', 'available', 'image')
        }),
        ('Системные поля', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return '-'
    product_image.short_description = 'Фото'
