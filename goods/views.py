from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def index(request):
    """Главная страница"""
    return render(request, 'index.html', {})


def catalog(request):
    """Список всех товаров каталоге"""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    context = {
        'title': 'Каталог товаров',
        'products': products,
        'categories': categories,
    }
    return render(request, 'goods/catalog.html', context)


def product_detail(request, product_slug):
    """Страница отдельного товара"""
    product = get_object_or_404(Product, slug=product_slug, available=True)

    context = {
        'title': product.name,
        'product': product,
    }
    return render(request, 'goods/product.html', context)

from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.objects.filter(available=True)
    
    def lastmod(self, obj):
        return obj.updated
    

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()
    

sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap
}


def sitemap_view(request):
    """Генерирует sitemap.xml автоматически"""
    from django.contrib.sitemaps import views
    return views.sitemap(request, sitemaps)
