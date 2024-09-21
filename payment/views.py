from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from store.models import Product


@require_POST
def billing_info(request):
    form = ShippingForm(request.POST)
    if not form.is_valid():
        for error in list(form.errors.values()):
            messages.error(request, error)
        return redirect('checkout')

    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    request.session['my_shipping'] = request.POST
    billing_form = PaymentForm()
    return render(request, "payment/billing_info.html", {'cart_products': cart_products, 'quantities': quantities,
                                                         'totals': totals, 'shipping_info': request.POST, "billing_form": billing_form})


@require_POST
def process_order(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    # payment_form = PaymentForm(request.POST)
    my_shipping = request.session.get('my_shipping')

    # Create shipping address from session info
    address1 = my_shipping['shipping_address1']
    address2 = my_shipping['shipping_address2']
    city = my_shipping['shipping_city']
    state = my_shipping['shipping_state']
    zip_code = my_shipping['shipping_zipcode']
    country = my_shipping['shipping_country']
    shipping_address = f"{address1}\n{address2}\n{city} {state} {zip_code}\n{country}"

    # Gather rest of order info
    full_name = my_shipping['shipping_full_name']
    email = my_shipping['shipping_email']
    amount_paid = totals

    # Create an order
    user = request.user if request.user.is_authenticated else None
    create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
    create_order.full_clean()
    create_order.save()

    # Add order items
    for product in cart_products:
        price = product.sale_price if product.is_sale else product.price
        quantity = quantities[str(product.id)]
        create_order_items = OrderItem(order=create_order, product=product, user=user, quantity=quantity, price=price)
        create_order_items.save()

    # Delete items in cart
    cart.clear()

    messages.success(request, "Order Placed")
    return redirect('home')


def payment_success(request):
    return render(request, "payment/payment_success.html", {})


@require_GET
def checkout(request):
    cart = Cart(request)
    print(request.method)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(instance=shipping_user)
    else:
        shipping_form = ShippingForm()

    return render(request, "payment/checkout.html", {'cart_products': cart_products, 'quantities': quantities,
                                                     'totals': totals, 'shipping_form': shipping_form})
