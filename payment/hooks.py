from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
import time
from .models import Order


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    time.sleep(5)
    # Grab info paypal sends
    # paypal_obj = sender
    # Grab the invoice
    # my_invoice = str(paypal_obj.invoice)

    # Match paypal invoice to the Order invoice
    # my_order = Order.objects.get(invoice=my_invoice)
    # my_order.paid = True
    # my_order.save()
