from .cart import Cart


def cart_count(request):
    cart = Cart(request)
    count = sum(int(item['quantity']) for _, item in cart.items())
    return {'cart_count': count}


def search_params(request):
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    return {'current_query': q, 'current_category': category}
