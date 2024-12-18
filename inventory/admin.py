from django.contrib import admin
from .models import Supplier, Ingredient, MenuItem, Order

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'contact_person', 'email', 'phone_number', 'is_active', 'rating']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'email', 'phone_number']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier', 'stock_quantity', 'unit', 'minimum_stock_level', 'cost_per_unit', 'storage_type', 'expiry_date']
    list_filter = ['supplier', 'unit', 'storage_type']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_vegetarian', 'is_available', 'price', 'preparation_time_minutes']
    list_filter = ['category', 'is_vegetarian', 'is_available']
    search_fields = ['name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'menu_item', 'quantity', 'customer_name', 'order_date', 'status']
    list_filter = ['status', 'order_date']
    search_fields = ['customer_name', 'menu_item__name']
