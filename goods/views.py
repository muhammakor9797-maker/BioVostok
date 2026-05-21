from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .forms import ReviewForm  # импорт формы


def index(request):
    """Главная страница"""
    return render(request, 'index.html', {})


def catalog(request):
    """Список всех товаров каталоге"""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)


    context = {
        'title': 'Каталог товаров',
        'products': products,
        'categories': categories,
    }
    return render(request, 'goods/catalog.html', context)


def product_detail(request, product_slug):
    """Страница отдельного товара"""
    product = get_object_or_404(Product, slug=product_slug, available=True)
    reviews = product.reviews.all()

    # Проверяем, есть ли уже отзыв от текущего пользователя (ДО проверки POST)
    user_has_review = False
    if request.user.is_authenticated:
        user_has_review = product.reviews.filter(author=request.user).exists()

    # Форма для отзыва
    form = ReviewForm()
    if request.method == 'POST' and request.user.is_authenticated and not user_has_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.author = request.user
            review.save()
            return redirect('product_detail', product_slug=product.slug)

    context = {
        'title': product.name,
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_has_review': user_has_review,
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
