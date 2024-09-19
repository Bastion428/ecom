from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_http_methods
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress
from django.contrib import messages


@require_POST
def billing_info(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    billing_form = PaymentForm()
    return render(request, "payment/billing_info.html", {'cart_products': cart_products, 'quantities': quantities,
                                                         'totals': totals, 'shipping_info': request.POST, "billing_form": billing_form})


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
