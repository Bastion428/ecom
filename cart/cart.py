from store.models import Product, Profile


class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request

        cart = self.session.get('session_key')

        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def db_add(self, product_id, quantity):
        id = str(product_id)
        qty = int(quantity)

        if id not in self.cart or self.cart[id] < qty:
            self.cart[product_id] = qty
            self.session.modified = True

    def add(self, product, quantity):
        product_id = str(product.id)

        result = False
        if product_id not in self.cart:
            self.cart[product_id] = int(quantity)
            self.session.modified = True
            result = True
            self.carty_update()

        return result

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
        self.carty_update()

    def delete(self, product):
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            self.carty_update()

    def clear(self):
        del self.session['session_key']
        self.cart = {}
        self.session.modified = True
        self.carty_update()

    def carty_update(self):
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=carty)
