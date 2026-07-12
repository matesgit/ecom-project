from django.db import models
import uuid
from django.contrib.auth.models import User


class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to="brands/", null=True, blank=True)

    def __str__(self):
        return self.name

class Perfume(models.Model):
    MEN = 'M'
    WOMEN = 'W'
    UNISEX = 'U'

    PERFUME_TYPE_CHOICES = [
        (MEN, 'Men'),
        (WOMEN, 'Women'),
        (UNISEX, 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='perfumes')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='perfumes/', null=True, blank=True)

    # ✅ CORRECT quantity field
    quantity = models.PositiveIntegerField(default=0)

    perfume_type = models.CharField(
        max_length=1,
        choices=PERFUME_TYPE_CHOICES,
        default=UNISEX
    )

    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_perfume_type_display()})"

    # ✅ stock helpers
    @property
    def in_stock(self):
        return self.quantity > 0

    @property
    def stock_status(self):
        if self.quantity == 0:
            return "Out of stock"
        elif self.quantity <= 10:
            return "Low stock"
        return "In stock"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    guest_id = models.UUIDField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.guest_id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    perfume = models.ForeignKey('Perfume', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'perfume')

    def __str__(self):
        if self.cart.user:
            return f"{self.quantity}x {self.perfume.name} in {self.cart.user.username}'s cart"
        return f"{self.quantity}x {self.perfume.name} in Guest {self.cart.guest_id}'s cart"

    @property
    def subtotal(self):
        return self.perfume.price * self.quantity



class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    guest_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)

    # Billing info
    full_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    perfume = models.ForeignKey(Perfume, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.perfume.price * self.quantity
        super().save(*args, **kwargs)
