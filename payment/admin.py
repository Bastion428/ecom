from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem, StripeOrder


admin.site.register(ShippingAddress)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(StripeOrder)


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    inlines = [OrderItemInline]


class StripeOrderAdmin(admin.ModelAdmin):
    model = StripeOrder
    readonly_fields = ["date_ordered", "invoice", "date_ordered"]


admin.site.unregister(Order)
admin.site.unregister(StripeOrder)
admin.site.register(Order, OrderAdmin)
admin.site.register(StripeOrder, StripeOrderAdmin)
