from rest_framework import serializers
from .models import (
    Supplier, 
    Ingredient, 
    MenuItem, 
    Order, 
    SupplierCategory, 
    IngredientUnit, 
    StorageType, 
    MenuItemCategory, 
    OrderStatus
)

class SupplierSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display', 
        read_only=True
    )
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'category', 'category_display', 
            'contact_person', 'email', 'phone_number', 
            'address', 'is_active', 'rating'
        ]
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source='supplier.name', 
        read_only=True
    )
    unit_display = serializers.CharField(
        source='get_unit_display', 
        read_only=True
    )
    storage_type_display = serializers.CharField(
        source='get_storage_type_display', 
        read_only=True
    )
    
    class Meta:
        model = Ingredient
        fields = [
            'id', 'name', 'supplier', 'supplier_name', 
            'stock_quantity', 'unit', 'unit_display', 
            'minimum_stock_level', 'cost_per_unit', 
            'storage_type', 'storage_type_display', 
            'expiry_date', 'is_low_stock', 'is_expired'
        ]
        read_only_fields = ['id', 'is_low_stock', 'is_expired']

class MenuItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display', 
        read_only=True
    )
    ingredient_cost = serializers.SerializerMethodField()
    ingredient_availability = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 
            'category', 'category_display', 
            'is_vegetarian', 'is_available', 
            'price', 'recipe', 
            'preparation_time_minutes', 
            'ingredient_cost', 
            'ingredient_availability'
        ]
        read_only_fields = ['id', 'ingredient_cost', 'ingredient_availability']
    
    def get_ingredient_cost(self, obj):
        return obj.calculate_ingredient_cost()
    
    def get_ingredient_availability(self, obj):
        return obj.check_ingredient_availability()

class OrderSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(
        source='menu_item.name', 
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', 
        read_only=True
    )
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'menu_item', 'menu_item_name', 
            'quantity', 'customer_name', 
            'special_instructions', 'order_date', 
            'status', 'status_display', 
            'total_price'
        ]
        read_only_fields = ['id', 'order_date', 'total_price']
    
    def get_total_price(self, obj):
        return obj.calculate_total_price()

    def validate(self, data):
        # Custom validation for order creation
        menu_item = data.get('menu_item')
        if not menu_item.check_ingredient_availability():
            raise serializers.ValidationError(
                "Not enough ingredients to complete this order"
            )
        return data
