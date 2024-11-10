from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from ecom.decorators.required_methods import required_methods_redirect
from django.conf import settings
import time
import json
import stripe
from .models import Order, StripeOrder

stripe.api_key = settings.STRIPE_SECRET_KEY


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    time.sleep(5)
    # Grab info paypal sends
    paypal_obj = sender
    # Grab the invoice
    my_invoice = str(paypal_obj.invoice)

    # Match paypal invoice to the Order invoice
    my_order = Order.objects.get(invoice=my_invoice)
    my_order.paid = True
    my_order.save()


@csrf_exempt
@required_methods_redirect(allowed_methods='POST')
def stripe_webhook(request):
    time.sleep(5)
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_KEY
        )
    except ValueError as e:
        # Invalid payload
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        session = event.data.object
        my_invoice = session.metadata['invoice']

        my_order = Order.objects.get(invoice=my_invoice)
        my_order.paid = True
        my_order.save()

        stripe_order = StripeOrder(invoice=my_invoice, amount_paid=my_order.amount_paid)
        stripe_order.save()
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
