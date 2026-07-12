from django.contrib import admin
from .models import *
from django.utils.html import format_html


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'price',
        'quantity',
        'colored_stock_status',
        'perfume_type',
    )

    list_filter = ('brand', 'perfume_type')
    search_fields = ('name',)
    list_editable = ('quantity',)

    def colored_stock_status(self, obj):
        if obj.quantity == 0:
            color = 'red'
            text = 'OUT OF STOCK'
        elif obj.quantity <= 10:
            color = 'orange'
            text = 'LOW STOCK'
        else:
            color = 'green'
            text = 'IN STOCK'

        return format_html(
            '<b style="color:{};">{}</b>',
            color,
            text
        )

    colored_stock_status.short_description = "Stock Status"

from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    """Inline display of cart items within the Cart admin"""
    model = CartItem
    extra = 0  # Don't show extra empty forms
    readonly_fields = ('added_at', 'subtotal')
    fields = ('perfume', 'quantity', 'subtotal', 'added_at')
    
    def subtotal(self, obj):
        return f"${obj.subtotal}"
    subtotal.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_owner', 'total_items', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'guest_id')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'total_price')
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Owner Information', {
            'fields': ('user', 'guest_id')
        }),
        ('Cart Summary', {
            'fields': ('total_items', 'total_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def cart_owner(self, obj):
        """Display cart owner - either username or guest ID"""
        if obj.user:
            return f"👤 {obj.user.username}"
        return f"👻 Guest ({str(obj.guest_id)[:8]}...)"
    cart_owner.short_description = 'Owner'
    
    def total_items(self, obj):
        """Display total items with icon"""
        count = obj.total_items
        return f"🛒 {count} item{'s' if count != 1 else ''}"
    total_items.short_description = 'Total Items'
    
    def total_price(self, obj):
        """Display total price formatted"""
        return f"💰 ${obj.total_price}"
    total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('perfume_name', 'cart_owner', 'quantity', 'subtotal_display', 'added_at')
    list_filter = ('added_at', 'cart__user')
    search_fields = ('perfume__name', 'cart__user__username', 'cart__guest_id')
    readonly_fields = ('added_at', 'subtotal_display')
    
    fieldsets = (
        ('Cart Item Details', {
            'fields': ('cart', 'perfume', 'quantity')
        }),
        ('Additional Info', {
            'fields': ('subtotal_display', 'added_at')
        }),
    )
    
    def perfume_name(self, obj):
        """Display perfume name"""
        return obj.perfume.name
    perfume_name.short_description = 'Perfume'
    
    def cart_owner(self, obj):
        """Display who owns this cart item"""
        if obj.cart.user:
            return f"👤 {obj.cart.user.username}"
        return f"👻 Guest ({str(obj.cart.guest_id)[:8]}...)"
    cart_owner.short_description = 'Cart Owner'
    
    def subtotal_display(self, obj):
        """Display subtotal formatted"""
        return f"${obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# Order admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'guest_id', 'total', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'created_at', 'user')
    list_editable = ('is_completed',)
    search_fields = ('user__username', 'guest_id')
    inlines = [OrderItemInline]