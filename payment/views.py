from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from cart.cart import Cart
from .forms import ShippingForm
from .models import ShippingAddress


def payment_success(request):
    return render(request, "payment/payment_success.html", {})


@require_http_methods(['GET', 'POST'])
def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        if request.method == 'POST':
            shipping_form = ShippingForm(request.POST, instance=shipping_user)
        else:
            shipping_form = ShippingForm(instance=shipping_user)
    else:
        if request.method == 'POST':
            shipping_form = ShippingForm(request.POST)
        else:
            shipping_form = ShippingForm()

    return render(request, "payment/checkout.html", {'cart_products': cart_products, 'quantities': quantities,
                                                     'totals': totals, 'shipping_form': shipping_form})
