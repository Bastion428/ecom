from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def cart_summary(request):
    return render(request, "cart_summary.html", {})


@require_POST
def cart_add(request):
    cart = Cart(request)

    product_id = int(request.POST.get('product_id'))
    product = get_object_or_404(Product, id=product_id)

    cart.add(product=product)
    cart_quantity = len(cart)
    response = JsonResponse({'qty': cart_quantity})
    return response


def cart_delete(request):
    pass


def cart_update(request):
    pass
