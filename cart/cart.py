from store.models import Product


class Cart():
    def __init__(self, request):
        self.session = request.session

        cart = self.session.get('session_key')

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        if product_id not in self.cart:
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = 0

        for product in products:
            if product.is_sale:
                total += (product.sale_price * self.cart[str(product.id)])
            else:
                total += (product.price * self.cart[str(product.id)])

        return total

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products

    # Gets quantities for each product in the cart
    def get_quants(self):
        return self.cart

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        self.cart[product_id] = product_qty

        self.session.modified = True
        return self.cart

    def delete(self, product):
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True

        return self.cart
