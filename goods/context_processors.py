from .models import Category
from django.conf import settings
from django.utils.translation import get_language

def languages(request):
    return {
        'LANGUAGES': settings.LANGUAGES,
        'SELECTED_LANGUAGE': get_language(),
    }


def cart(request):
    from carts.cart import Cart
    return {
        'cart': Cart(request)
    }

def categories(request):
    return {
        'categories': Category.objects.filter(active=True).order_by('order')
    }
