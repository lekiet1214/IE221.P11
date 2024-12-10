from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import RegistrationForm
from .models import *


# Create your views here.

def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/home.html', context)


def product(request, id):
    product = Product.objects.get(id=id)
    context = {'product': product}
    return render(request, 'store/product.html', context)


def add_to_cart(request, id):
    # Get session cart
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    try:
        cart.add_to_cart(id)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def remove_from_cart(request, product_id):
    # Get session cart
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
        cart.remove_from_cart(product_id)
    return redirect('cart')


def cart(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = None
    products = cart.cart_items.all()
    context = {'cart_items': products, 'cart_total': cart.total}
    return render(request, 'store/cart.html', context)


@login_required
def checkout(request):
    # Ensure the customer exists (create if not)
    customer, created = Customer.objects.get_or_create(user=request.user)

    # If the user doesn't have a cart, redirect to home
    if not customer.cart:
        # Get session cart
        cart_id = request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            customer.cart = cart
            customer.save()
        else:
            return redirect('home')

    cart = customer.cart
    cart_items = cart.cart_items.all()

    # If no items in the cart, redirect to cart page
    if not cart_items:
        return redirect('cart')

    # Handle POST request when the user submits the order form
    if request.method == 'POST':
        # Capture form data
        name = request.POST.get('name')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment')

        # Create the order
        order = Order()
        order.total = cart.total
        order.total_items = cart.total_items
        order.save()

        # Add items to the order
        for item in cart.cart_items.all():
            order.items.add(item.product)

        # Link the order to the customer
        customer.orders.add(order)

        context = {
            'cart_items': cart_items,
            'cart_total': cart.total,
            'total_items': cart.total_items,
        }

        # Clear the cart after the order is placed
        cart.clear_cart()

        # Redirect to order summary page or success page
        return render(request, 'store/checkout_success.html', context)

    # Pass order details to the checkout page
    context = {
        'cart_items': cart_items,
        'cart_total': cart.total,
        'total_items': cart.total_items,
    }

    return render(request, 'store/checkout.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('home')  # Redirect to the home page after successful registration
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    orders = customer.orders.all()
    context = {'orders': orders}
    return render(request, 'store/profile.html', context)

def search_products(request):
    query = request.GET.get('q', '')  # Get the search term from the query parameter
    products = Product.objects.filter(name__icontains=query) if query else []
    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'store/search.html', context)
