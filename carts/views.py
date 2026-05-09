from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from goods.models import Product
from .cart import Cart


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('carts:cart_detail')



@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('carts:cart_detail')



def cart_detail(request):
    cart = Cart(request)
    return render(request, 'carts/detail.html', {'cart': cart})

