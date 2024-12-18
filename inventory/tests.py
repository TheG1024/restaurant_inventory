from django.test import TestCase
from django.core.exceptions import ValidationError
import re
from .models import Supplier, Ingredient, MenuItem, Order, RecipeItem
from django.utils import timezone

class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            name="Test Supplier",
            email="valid@email.com",
            rating=4.5
        )

    def test_supplier_clean_method(self):
        # Test invalid email
        self.supplier.email = "invalid-email"
        with self.assertRaises(ValidationError):
            self.supplier.clean()
        
        # Test invalid rating
        self.supplier.email = "valid@email.com"
        self.supplier.rating = 6
        with self.assertRaises(ValidationError):
            self.supplier.clean()

class IngredientModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.ingredient = Ingredient.objects.create(
            name="Test Ingredient", 
            supplier=self.supplier, 
            stock_quantity=100, 
            unit="Gram",
            cost_per_unit=2.50,
            minimum_stock_level=10,
            storage_type="DRY_STORAGE",
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )

    def test_ingredient_str_method(self):
        self.assertEqual(str(self.ingredient), "Test Ingredient (100.00 Gram)")

    def test_is_expired(self):
        # Test not expired
        self.assertFalse(self.ingredient.is_expired())

        # Test expired
        self.ingredient.expiry_date = timezone.now().date() - timezone.timedelta(days=1)
        self.assertTrue(self.ingredient.is_expired())

    def test_is_low_stock(self):
        # Test not low stock
        self.assertFalse(self.ingredient.is_low_stock())

        # Test low stock
        self.ingredient.stock_quantity = 5
        self.assertTrue(self.ingredient.is_low_stock())

class MenuItemModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.ingredient = Ingredient.objects.create(
            name="Test Ingredient", 
            supplier=self.supplier, 
            stock_quantity=10, 
            unit="Gram",
            cost_per_unit=2.50,
            minimum_stock_level=5,
            storage_type="DRY_STORAGE",
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        self.menu_item = MenuItem.objects.create(
            name="Test Menu Item", 
            price=15.00,
            is_available=True,
            preparation_time_minutes=15
        )
        # Create a recipe item with insufficient stock
        RecipeItem.objects.create(
            menu_item=self.menu_item, 
            ingredient=self.ingredient, 
            quantity=100  # More than available stock
        )

    def test_menu_item_str_method(self):
        self.assertEqual(str(self.menu_item), "Test Menu Item ($15.00)")

    def test_check_ingredient_availability(self):
        self.assertFalse(self.menu_item.check_ingredient_availability())

class OrderModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name="Test Supplier")
        self.ingredient = Ingredient.objects.create(
            name="Test Ingredient", 
            supplier=self.supplier, 
            stock_quantity=10, 
            unit="Gram",
            cost_per_unit=2.50,
            minimum_stock_level=5,
            storage_type="DRY_STORAGE",
            expiry_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        self.menu_item = MenuItem.objects.create(
            name="Test Menu Item", 
            price=15.00,
            is_available=True,
            preparation_time_minutes=15
        )
        RecipeItem.objects.create(
            menu_item=self.menu_item, 
            ingredient=self.ingredient, 
            quantity=100  # More than available stock
        )

    def test_save_method_with_insufficient_stock(self):
        order = Order(
            menu_item=self.menu_item, 
            quantity=1
        )
        with self.assertRaises(ValidationError):
            order.save()
