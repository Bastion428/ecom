from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from ecom.decorators.required_methods import required_methods_redirect
from django.contrib import messages
from django.core.paginator import Paginator
import datetime
from decimal import Decimal
# Stipe imports
import stripe
# Paypal imports
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid  # unique user id for duplicate orders

stripe.api_key = settings.STRIPE_SECRET_KEY


@staff_member_required(login_url='login')
def orders(request, pk):
    order = Order.objects.get(id=pk)
    items = OrderItem.objects.filter(order=pk)

    if request.POST:
        order = Order.objects.filter(id=pk)
        status = request.POST['shipping_status']
        if status == 'true':
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
        else:
            order.update(shipped=False, date_shipped=None)

        messages.success(request, "Shipping status updated")
        return redirect('orders', pk=pk)

    return render(request, 'payment/orders.html', {'order': order, 'items': items})


@staff_member_required(login_url=settings.LOGIN_URL)
def not_shipped_dash(request):
    if request.POST:
        num = request.POST['num']
        now = datetime.datetime.now()
        order = Order.objects.filter(id=num)
        order.update(shipped=True, date_shipped=now)

        messages.success(request, "Shipping status updated")
        return redirect('not_shipped_dash')

    orders = Order.objects.filter(shipped=False, paid=True)
    paginator = Paginator(orders, 10)

    page_num = request.GET.get('page')
    orders = paginator.get_page(page_num)

    return render(request, "payment/not_shipped_dash.html", {'orders': orders})


@staff_member_required(login_url=settings.LOGIN_URL)
def shipped_dash(request):
    if request.POST:
        num = request.POST['num']
        order = Order.objects.filter(id=num)
        order.update(shipped=False, date_shipped=None)

        messages.success(request, "Shipping status updated")
        return redirect('shipped_dash')

    orders = Order.objects.filter(shipped=True)
    paginator = Paginator(orders, 10)

    page_num = request.GET.get('page')
    orders = paginator.get_page(page_num)
    return render(request, "payment/shipped_dash.html", {'orders': orders})


def get_shipping(shipping_dict):
    # Create shipping address
    address1 = shipping_dict['shipping_address1']
    address2 = shipping_dict['shipping_address2']
    city = shipping_dict['shipping_city']
    state = shipping_dict['shipping_state']
    zip_code = shipping_dict['shipping_zipcode']
    country = shipping_dict['shipping_country']

    if not address2:
        return f"{address1}\n{city}, {state} {zip_code}\n{country}"

    return f"{address1}\n{address2}\n{city}, {state} {zip_code}\n{country}"


@required_methods_redirect(allowed_methods='POST')
def billing_info(request):
    my_shipping = request.POST
    request.session['my_shipping'] = my_shipping

    form = ShippingForm(request.POST)
    if not form.is_valid():
        for error in list(form.errors.values()):
            messages.error(request, error)
        return redirect('checkout')

    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    host = request.get_host()
    my_invoice = str(uuid.uuid4())
    request.session['my_invoice'] = my_invoice

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': totals,
        'item_name': 'Media Order',
        'no_shipping': '2',
        'invoice': my_invoice,
        'currency_code': 'USD',
        'notify_url': 'https://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url': 'https://{}{}'.format(host, reverse('payment_success')),
        'cancel_return': 'https://{}{}'.format(host, reverse('payment_failed')),
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict)
    shipping_address = get_shipping(my_shipping)

    billing_form = PaymentForm()
    # Create an order
    user = request.user if request.user.is_authenticated else None
    create_order = Order(user=user, full_name=my_shipping['shipping_full_name'], email=my_shipping['shipping_email'], shipping_address=shipping_address, amount_paid=totals, invoice=my_invoice)
    create_order.full_clean()
    create_order.save()

    # Add order items
    for product in cart_products:
        price = product.sale_price if product.is_sale else product.price
        quantity = quantities[str(product.id)]
        create_order_items = OrderItem(order=create_order, product=product, user=user, quantity=quantity, price=price)
        create_order_items.full_clean()
        create_order_items.save()

    # Delete items in cart from the database for logged in users
    cart.clear_cart_db()

    return render(request, "payment/billing_info.html", {'paypal_form': paypal_form, 'cart_products': cart_products, 'quantities': quantities,
                                                         'totals': totals, 'shipping_info': request.POST, "billing_form": billing_form})


def items_to_line_items(items, host):
    line_items = []
    for item in items:
        item_dict = {
            'price_data': {
                'currency': 'USD',
                'unit_amount_decimal': item.price * Decimal('100'),
                'product_data': {
                    'name': item.product.name,
                    # 'images': 'https://{}{}'.format(host + '/media/', item.product.image),
                },
            },
            'quantity': item.quantity,
        }
        line_items.append(item_dict)
    return line_items


@required_methods_redirect(allowed_methods='POST')
def process_order(request):
    # payment_form = PaymentForm(request.POST)

    # Delete items in cart
    # cart.clear_cart()

    my_invoice = request.session['my_invoice']
    try:
        order = Order.objects.get(invoice=my_invoice)
    except Order.DoesNotExist:
        messages.error(request, "There was an error processing your payment")
        return redirect('payment_failed')

    items = OrderItem.objects.filter(order=order.pk)
    host = request.get_host()
    line_items = items_to_line_items(items, host)

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        invoice=my_invoice,
        mode='payment',
        success_url='https://{}{}'.format(host, reverse('payment_success')),
        cancel_url='https://{}{}'.format(host, reverse('payment_failed')),
    )

    return redirect(checkout_session.url, code=303)


def payment_success(request):
    # Delete the browser cart (session variable)
    cart = Cart(request)
    cart.clear_cart_sess()

    return render(request, "payment/payment_success.html", {})


def payment_failed(request):
    return render(request, "payment/payment_failed.html", {})


@required_methods_redirect(allowed_methods='GET')
def checkout(request):
    cart = Cart(request)
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
