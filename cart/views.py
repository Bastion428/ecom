from django.shortcuts import render, get_object_or_404
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
# from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.contrib import messages


def cart_summary(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    return render(request, "cart_summary.html", {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})


@require_POST
def cart_add(request):
    cart = Cart(request)

    product_id = int(request.POST.get('product_id'))
    product_qty = int(request.POST.get('product_qty'))

    product = get_object_or_404(Product, id=product_id)

    result = cart.add(product=product, quantity=product_qty)
    if result:
        messages.success(request, "Product added to cart")

    response = JsonResponse({'qty': len(cart), 'result': result})
    return response


@require_http_methods(['DELETE'])
def cart_delete(request):
    cart = Cart(request)
    delete = QueryDict(request.body)

    product_id = int(delete.get('product_id'))
    cart.delete(product=product_id)

    return JsonResponse({'total': cart.cart_total(), 'qty': len(cart)})


@require_http_methods(['PUT'])
def cart_update(request):
    cart = Cart(request)
    put = QueryDict(request.body)

    product_id = int(put.get('product_id'))
    product_qty = int(put.get('product_qty'))

    cart.update(product=product_id, quantity=product_qty)

    response = JsonResponse({'total': cart.cart_total()})
    return response
