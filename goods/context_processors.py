from .models import Category


def cart(request):
    from carts.cart import Cart
    return {
        'cart': Cart(request)
    }

def categories(request):
    return {
        'categories': Category.objects.filter(active=True).order_by('order')
    }