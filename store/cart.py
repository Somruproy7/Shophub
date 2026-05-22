class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, price, quantity=1):
        pid = str(product_id)
        if pid in self.cart:
            self.cart[pid]['quantity'] += quantity
        else:
            self.cart[pid] = {'quantity': quantity, 'price': str(price)}
        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def items(self):
        return self.cart.items()

    def total(self):
        total = 0
        for pid, data in self.cart.items():
            total += float(data['price']) * int(data['quantity'])
        return total

    def set_quantity(self, product_id, quantity):
        pid = str(product_id)
        if pid in self.cart:
            if int(quantity) <= 0:
                del self.cart[pid]
            else:
                self.cart[pid]['quantity'] = int(quantity)
            self.save()

