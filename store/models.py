from django.db import models
from django.contrib.auth.models import User


# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default='Description not available')
    price = models.FloatField()
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name


# CartItem Model
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_total(self):
        return self.product.price * self.quantity


# Cart Model
class Cart(models.Model):
    cart_items = models.ManyToManyField(CartItem, blank=True)  # Removed null=True, blank=True is enough
    total = models.FloatField(default=0.0)
    total_items = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Cart ID: {self.id}'

    def add_to_cart(self, product_id):
        product = Product.objects.get(id=product_id)

        # Try to find the existing cart item or create one
        cart_item, created = CartItem.objects.get_or_create(product=product)

        # If the item already exists, update the quantity
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Add to the cart
        self.cart_items.add(cart_item)

        # Update cart total and item count
        self.total += product.price
        self.total_items += 1
        self.save()

    def remove_from_cart(self, product_id):
        product = Product.objects.get(id=product_id)
        cart_item = CartItem.objects.get(product=product)

        # Remove the item from the cart
        self.cart_items.remove(cart_item)

        # Decrease the total and total items accordingly
        self.total -= cart_item.get_total()
        self.total_items -= cart_item.quantity
        self.save()

        # Now delete the CartItem
        cart_item.delete()

    def clear_cart(self):
        self.cart_items.clear()
        self.total = 0.0
        self.total_items = 0
        self.save()

    def get_cart_items(self):
        return self.cart_items.all()


# Order Model
class Order(models.Model):
    items = models.ManyToManyField(Product)
    total = models.FloatField()
    total_items = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order ID: {self.id}'

    def place_order(self, cart):
        # Calculate total and total_items
        self.total = cart.total
        self.total_items = cart.total_items

        # Save the order to get an id
        self.save()

        # Add the cart items to the order
        for cart_item in cart.cart_items.all():
            self.items.add(cart_item.product)

        # Save again to update the items field after adding
        self.save()

        # Clear the cart
        cart.clear_cart()


# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, null=True, blank=True)
    orders = models.ManyToManyField(Order)

    def __str__(self):
        return self.user.username

    def place_order(self):
        # Ensure the customer has a cart
        if not self.cart:
            return None  # No cart to place the order from

        # Create a new order from the cart
        order = Order()
        order.place_order(self.cart)

        # Add the created order to the customer orders
        self.orders.add(order)

        # Clear the cart after the order is placed
        self.cart = None  # Remove the cart after the order
        self.save()

        return order