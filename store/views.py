from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Order, OrderItem, Address
from .forms import AddressForm, UserRegistrationForm, ProfileForm, UserUpdateForm
from .cart import Cart
from . import mongo
from types import SimpleNamespace

import razorpay
from django.conf import settings


def _enrich_product(p):
    """Fill in friendly placeholder details when data is missing, based on title."""
    title = getattr(p, 'title', '') or ''
    base = (title.split()[0] if title else 'Generic')
    if not getattr(p, 'brand', None):
        p.brand = base
    if not getattr(p, 'maker', None):
        p.maker = f"{base} Labs"
    if not getattr(p, 'distributor', None):
        p.distributor = f"{base} Distributors"
    if not getattr(p, 'category', None):
        p.category = 'General'
    if not getattr(p, 'highlights', None):
        p.highlights = [
            f"Premium {base} build",
            "Tested for quality and reliability",
            "Best value in its class",
        ]
    if not getattr(p, 'warranty_months', None):
        p.warranty_months = 12
    if not getattr(p, 'ship_eta_days', None):
        p.ship_eta_days = 3
    return p


def home(request):
    # Read products from MongoDB only with optional search/category filters.
    q = request.GET.get('q')
    category = request.GET.get('category')
    m_products = mongo.get_products(limit=None, q=q, category=category)
    objs = []
    for m in m_products:
        p = SimpleNamespace()
        p.id = m.get('_id')
        p.title = m.get('title')
        p.slug = m.get('slug')
        p.description = m.get('description')
        p.price = m.get('price')
        # image.url expected in templates
        img_url = m.get('image_url')
        p.image = SimpleNamespace(url=img_url) if img_url else None
        p.available = m.get('available', True)
        objs.append(p)
    products_for_template = objs

    cart = Cart(request)
    cart_count = sum(int(item['quantity']) for _, item in cart.items())

    return render(request, 'store/home.html', {
        'products': products_for_template,
        'cart_count': cart_count,
        'current_query': q or '',
        'current_category': category or '',
    })


def product_detail(request, slug):
    # Prefer Mongo lookup
    mprod = mongo.get_product_by_slug(slug)
    if mprod:
        # convert mongo doc to a simple object the template can use
        p = SimpleNamespace()
        p.id = mprod.get('_id')
        p.title = mprod.get('title')
        p.slug = mprod.get('slug')
        p.description = mprod.get('description')
        p.price = mprod.get('price')
        if mprod.get('image_url'):
            p.image = SimpleNamespace(url=mprod.get('image_url'))
        else:
            p.image = None
        p.available = mprod.get('available', True)
        # optional fields for details table
        p.brand = mprod.get('brand')
        p.maker = mprod.get('maker')
        p.distributor = mprod.get('distributor')
        p.category = mprod.get('category')
        p = _enrich_product(p)
        return render(request, 'store/product_detail.html', {'product': p})

    product = get_object_or_404(Product, slug=slug)
    # normalize ORM product to have the same attributes
    p = SimpleNamespace()
    p.id = getattr(product, 'id', None)
    p.title = product.title
    p.slug = product.slug
    p.description = product.description
    p.price = product.price
    p.image = product.image if getattr(product, 'image', None) else None
    p.available = getattr(product, 'available', True)
    p.brand = getattr(product, 'brand', None)
    p.maker = getattr(product, 'maker', None)
    p.distributor = getattr(product, 'distributor', None)
    p.category = getattr(product.category, 'name', None) if getattr(product, 'category', None) else None
    return render(request, 'store/product_detail.html', {'product': p})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.add(product_id, product.price)
    messages.success(request, f'Added {product.title} to cart')
    return redirect('store:cart')


@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.clear()
    cart.add(product_id, product.price)
    return redirect('store:checkout')


@login_required
def cart_view(request):
    cart = Cart(request)
    items = []
    from .models import Product
    for pid, data in cart.items():
        try:
            product = Product.objects.get(pk=pid)
        except Product.DoesNotExist:
            continue
        items.append({'product': product, 'quantity': data['quantity'], 'price': data['price']})
    total = cart.total()
    return render(request, 'store/cart.html', {'items': items, 'total': total})


@login_required
def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('store:cart')


@login_required
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('store:cart')


@login_required
def update_cart_quantity(request, product_id):
    """POST endpoint. Accepts 'action' in POST: 'inc', 'dec', or 'set' with 'quantity'.
    Returns JSON with new quantity and new total.
    """
    from django.http import JsonResponse
    cart = Cart(request)
    action = request.POST.get('action')
    try:
        if action == 'inc':
            # increase by 1
            current = int(cart.cart.get(str(product_id), {}).get('quantity', 0))
            cart.set_quantity(product_id, current + 1)
        elif action == 'dec':
            current = int(cart.cart.get(str(product_id), {}).get('quantity', 0))
            cart.set_quantity(product_id, max(0, current - 1))
        elif action == 'set':
            q = int(request.POST.get('quantity', 0))
            cart.set_quantity(product_id, q)
        else:
            return JsonResponse({'error': 'invalid action'}, status=400)

        from .models import Product
        try:
            product = Product.objects.get(pk=product_id)
            new_qty = int(cart.cart.get(str(product_id), {}).get('quantity', 0))
            new_total = cart.total()
            return JsonResponse({'quantity': new_qty, 'total': new_total})
        except Product.DoesNotExist:
            return JsonResponse({'error': 'product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def checkout(request):
    cart = Cart(request)
    if not cart.items():
        messages.info(request, 'Your cart is empty')
        return redirect('store:home')

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            # create order
            order = Order.objects.create(user=request.user, address=address, total=cart.total(), payment_method='cod')
            for pid, data in cart.items():
                product = Product.objects.get(pk=pid)
                OrderItem.objects.create(order=order, product=product, quantity=data['quantity'], price=data['price'])
            # persist to Mongo as well (signals also do this; explicit call for immediate consistency)
            try:
                mongo.save_order(order)
            except Exception:
                pass
            cart.clear()
            messages.success(request, 'Order placed successfully (COD)')
            order_id = getattr(order, 'id', None)
            return redirect('store:order_detail', order_id=order_id)
    else:
        form = AddressForm()

    return render(request, 'store/checkout.html', {'form': form, 'total': cart.total()})


@login_required
def razorpay_create_order(request):
    cart = Cart(request)
    client = razorpay.Client(auth=(getattr(settings, 'RAZOR_KEY_ID', ''), getattr(settings, 'RAZOR_KEY_SECRET', '')))
    amount = int(cart.total() * 100)
    razor_order = getattr(client, 'order').create({'amount': amount, 'currency': 'INR', 'payment_capture': '1'})
    # Save order and redirect to payment page (not fully implemented)
    return render(request, 'store/razorpay_payment.html', {'razor_order': razor_order, 'amount': amount})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('store:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store:home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('store:home')


@login_required
def profile_view(request):
    # Ensure profile exists
    from .models import Profile
    Profile.objects.get_or_create(user=request.user)

    # Default address instance (first or new)
    addr_instance = Address.objects.filter(user=request.user).first()

    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        aform = AddressForm(request.POST, instance=addr_instance)
        if uform.is_valid() and pform.is_valid() and aform.is_valid():
            uform.save()
            p = pform.save(commit=False)
            p.user = request.user
            p.save()
            addr = aform.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, 'Profile updated')
            return redirect('store:profile')
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileForm(instance=getattr(request.user, 'profile', None))
        aform = AddressForm(instance=addr_instance)

    # User's orders list
    my_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'uform': uform, 'pform': pform, 'aform': aform, 'orders': my_orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def order_edit(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if order.paid:
        messages.info(request, 'Paid orders cannot be edited')
        return redirect('store:order_detail', order_id=order.id)

    # Edit address inline (create or use existing)
    if request.method == 'POST':
        # Update address fields from POST if present
        addr = order.address or Address(user=request.user)
        addr.full_name = request.POST.get('full_name', addr.full_name)
        addr.line1 = request.POST.get('line1', addr.line1)
        addr.line2 = request.POST.get('line2', addr.line2 or '')
        addr.city = request.POST.get('city', addr.city)
        addr.state = request.POST.get('state', addr.state or '')
        addr.postal_code = request.POST.get('postal_code', addr.postal_code)
        addr.country = request.POST.get('country', addr.country)
        addr.save()
        order.address = addr

        # Update item quantities (fields named quantity_<item.id>)
        new_total = 0
        for item in order.items.all():
            field = f'quantity_{item.id}'
            try:
                q = int(request.POST.get(field, item.quantity))
                q = max(0, q)
            except (TypeError, ValueError):
                q = item.quantity
            if q == 0:
                item.delete()
                continue
            item.quantity = q
            item.save()
            new_total += (item.price * q)

        # Recompute total based on current items
        if new_total == 0:
            # if no items remain, keep total 0
            order.total = 0
        else:
            order.total = new_total
        order.save()

        # Mirror to Mongo for reads
        try:
            mongo.save_order(order)
        except Exception:
            pass

        messages.success(request, 'Order updated')
        return redirect('store:order_detail', order_id=order.id)

    return render(request, 'store/order_edit.html', {'order': order})


from django.views.decorators.http import require_POST
from django.http import JsonResponse


@require_POST
def chatbot_message(request):
    """Lightweight rule-based chatbot endpoint.
    Supports:
    - cheapest products
    - best products
    - site/about help
    - guided order placement collecting Address fields and placing COD order from current cart
    """
    text = (request.POST.get('message') or '').strip().lower()

    # Helpers to format product suggestions
    def product_list_reply(items):
        lines = []
        for p in items:
            title = p.get('title') if isinstance(p, dict) else getattr(p, 'title', '')
            slug = p.get('slug') if isinstance(p, dict) else getattr(p, 'slug', '')
            price = p.get('price') if isinstance(p, dict) else getattr(p, 'price', 0)
            url = request.build_absolute_uri(reverse('store:product_detail', kwargs={'slug': slug})) if slug else ''
            lines.append(f"- {title} (₹{price}) → {url}")
        return "\n".join(lines) if lines else "No products found."

    # Intent: about/site
    if any(k in text for k in ['about', 'website', 'what can', 'shophub']):
        reply = (
            "I'm ShopHub Assistant. I can show you the cheapest or best products, "
            "help with checkout by collecting your address, and answer basic site questions. "
            "Try typing: 'cheapest', 'best', or 'place order'."
        )
        return JsonResponse({'reply': reply})

    # Intent: cheapest products
    if 'cheap' in text or 'lowest' in text:
        prods = mongo.get_products(limit=None)
        try:
            prods_sorted = sorted(prods, key=lambda x: x.get('price', 0))[:5]
        except Exception:
            prods_sorted = []
        return JsonResponse({'reply': "Here are some of the cheapest picks:\n" + product_list_reply(prods_sorted)})

    # Intent: best products (use highest price as simple proxy)
    if 'best' in text or 'top' in text or 'premium' in text:
        prods = mongo.get_products(limit=None)
        try:
            prods_sorted = sorted(prods, key=lambda x: x.get('price', 0), reverse=True)[:5]
        except Exception:
            prods_sorted = []
        return JsonResponse({'reply': "Top premium picks:\n" + product_list_reply(prods_sorted)})

    # Guided order placement
    if 'place order' in text or 'checkout' in text or 'buy for me' in text:
        if not request.user.is_authenticated:
            login_url = reverse('store:login')
            return JsonResponse({'reply': f"Please log in first: {login_url}"})

        cart = Cart(request)
        if not cart.items():
            return JsonResponse({'reply': "Your cart is empty. Add some products first."})

        session_key = 'bot_order'
        state = request.session.get(session_key, {})
        # define required fields and prompts
        fields = [
            ('full_name', 'Please provide your full name.'),
            ('line1', 'Provide address line 1.'),
            ('city', 'Which city?'),
            ('state', 'State (optional, say skip to leave blank).'),
            ('postal_code', 'Postal code?'),
            ('country', 'Country?'),
        ]

        # If message looks like key: value, capture it
        if ':' in text:
            key = text.split(':', 1)[0].strip().replace(' ', '_')
            val = text.split(':', 1)[1].strip()
            if key in [f[0] for f in fields]:
                if val and val != 'skip':
                    state[key] = val
                elif key in state:
                    del state[key]

        # Find next missing
        for key, prompt in fields:
            if not state.get(key):
                request.session[session_key] = state
                return JsonResponse({'reply': prompt + " You can answer like: '" + key.replace('_', ' ') + ": <your answer>'"})

        # All collected → create address + order
        addr = Address(user=request.user,
                       full_name=state.get('full_name'),
                       line1=state.get('line1'),
                       line2=state.get('line2') or '',
                       city=state.get('city'),
                       state=state.get('state') or '',
                       postal_code=state.get('postal_code'),
                       country=state.get('country'))
        addr.save()
        order = Order.objects.create(user=request.user, address=addr, total=cart.total(), payment_method='cod')
        for pid, data in cart.items():
            try:
                product = Product.objects.get(pk=pid)
                OrderItem.objects.create(order=order, product=product, quantity=data['quantity'], price=data['price'])
            except Product.DoesNotExist:
                continue
        try:
            mongo.save_order(order)
        except Exception:
            pass
        cart.clear()
        request.session.pop(session_key, None)
        order_url = request.build_absolute_uri(reverse('store:order_detail', kwargs={'order_id': order.id}))
        return JsonResponse({'reply': f"Done! Order placed successfully. View your order: {order_url}"})

    # Default fallback
    return JsonResponse({'reply': "I can help with: 'cheapest', 'best', 'place order', or 'about'."})
