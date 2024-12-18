from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
import re
from django.utils import timezone

class SupplierCategory(models.TextChoices):
    PRODUCE = 'PROD', _('Produce')
    MEAT = 'MEAT', _('Meat')
    DAIRY = 'DAIRY', _('Dairy')
    BAKERY = 'BAKE', _('Bakery')
    OTHER = 'OTHER', _('Other')

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=5, 
        choices=SupplierCategory.choices, 
        default=SupplierCategory.OTHER
    )
    contact_person = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Business rating and reliability tracking
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)
        ],
        default=3.0
    )
    
    def clean(self):
        # Add validation for email and rating
        if self.email and not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValidationError("Invalid email format")
        
        if self.rating is not None and (self.rating < 0 or self.rating > 5):
            raise ValidationError("Rating must be between 0 and 5")
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class IngredientUnit(models.TextChoices):
    KILOGRAM = 'KG', _('Kilogram')
    GRAM = 'G', _('Gram')
    LITER = 'L', _('Liter')
    MILLILITER = 'ML', _('Milliliter')
    PIECE = 'PC', _('Piece')

class StorageType(models.TextChoices):
    REFRIGERATED = 'COLD', _('Refrigerated')
    FROZEN = 'FROZ', _('Frozen')
    DRY_STORAGE = 'DRY', _('Dry Storage')
    ROOM_TEMP = 'ROOM', _('Room Temperature')

class Ingredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(
        'Supplier', 
        on_delete=models.PROTECT,
        related_name='ingredients'
    )
    
    # Inventory Tracking
    stock_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(
        max_length=3, 
        choices=IngredientUnit.choices, 
        default=IngredientUnit.GRAM
    )
    
    # Advanced Tracking
    minimum_stock_level = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=10.0
    )
    cost_per_unit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    
    # Storage and Expiry
    storage_type = models.CharField(
        max_length=4, 
        choices=StorageType.choices, 
        default=StorageType.DRY_STORAGE
    )
    expiry_date = models.DateField(
        null=True,  # Allow null values
        blank=True,  # Allow blank in forms
        default=None  # Optional default
    )
    
    def is_low_stock(self):
        """
        Check if the ingredient stock is below minimum level
        """
        return self.stock_quantity <= self.minimum_stock_level
    
    def is_expired(self):
        """
        Check if the ingredient is expired
        """
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()
    
    def __str__(self):
        return f"{self.name} ({self.stock_quantity:.2f} {self.get_unit_display()})"

class MenuItemCategory(models.TextChoices):
    APPETIZER = 'APP', _('Appetizer')
    MAIN_COURSE = 'MAIN', _('Main Course')
    DESSERT = 'DESS', _('Dessert')
    BEVERAGE = 'BEV', _('Beverage')

class MenuItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Categorization
    category = models.CharField(
        max_length=4, 
        choices=MenuItemCategory.choices, 
        default=MenuItemCategory.MAIN_COURSE
    )
    
    # Dietary and Availability
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    
    # Pricing and Ingredients
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    recipe = models.ManyToManyField(
        'Ingredient',
        through='RecipeItem',
        related_name='menu_items'
    )
    
    # Preparation Details
    preparation_time_minutes = models.PositiveIntegerField(
        validators=[MaxValueValidator(120)],
        help_text="Estimated preparation time in minutes",
        null=True,  # Allow null values
        blank=True  # Allow blank in forms
    )
    
    def calculate_ingredient_cost(self):
        total_cost = 0
        for recipe_item in self.recipe_items.all():
            total_cost += recipe_item.ingredient.cost_per_unit * recipe_item.quantity
        return total_cost
    
    def check_ingredient_availability(self):
        """
        Check if all required ingredients are available in sufficient quantity
        """
        for recipe_item in self.recipe_items.all():
            ingredient = recipe_item.ingredient
            required_quantity = recipe_item.quantity
            
            # Check if ingredient stock is less than required quantity
            if ingredient.stock_quantity < required_quantity:
                return False
        return True
    
    def __str__(self):
        return f"{self.name} (${self.price:.2f})"

class RecipeItem(models.Model):
    """
    Represents an ingredient used in a menu item with its required quantity
    """
    menu_item = models.ForeignKey(
        'MenuItem', 
        on_delete=models.CASCADE, 
        related_name='recipe_items'
    )
    ingredient = models.ForeignKey(
        'Ingredient', 
        on_delete=models.CASCADE,
        related_name='recipe_items'
    )
    quantity = models.FloatField(default=0)

    def __str__(self):
        return f"{self.ingredient.name} for {self.menu_item.name}"

    class Meta:
        unique_together = ('menu_item', 'ingredient')
        verbose_name_plural = "Recipe Items"

class OrderStatus(models.TextChoices):
    PENDING = 'PEND', _('Pending')
    PREPARING = 'PREP', _('Preparing')
    READY = 'READY', _('Ready')
    COMPLETED = 'COMP', _('Completed')
    CANCELLED = 'CANC', _('Cancelled')

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Order Details
    menu_item = models.ForeignKey(
        MenuItem, 
        on_delete=models.PROTECT,
        related_name='orders'
    )
    quantity = models.PositiveIntegerField(default=1)
    
    # Customer and Timing
    customer_name = models.CharField(max_length=100, blank=True)
    special_instructions = models.TextField(blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    
    # Status Tracking
    status = models.CharField(
        max_length=9, 
        choices=OrderStatus.choices, 
        default=OrderStatus.PENDING
    )
    
    def calculate_total_price(self):
        return self.menu_item.price * self.quantity
    
    def reduce_ingredient_stock(self):
        if self.status == OrderStatus.COMPLETED:
            for recipe_item in self.menu_item.recipe_items.all():
                ingredient = recipe_item.ingredient
                required_quantity = recipe_item.quantity
                
                ingredient.stock_quantity -= required_quantity * self.quantity
                ingredient.save()
    
    def save(self, *args, **kwargs):
        # Validate ingredient availability before saving
        menu_item = self.menu_item
        
        # Check if menu item is available
        if not menu_item.is_available:
            raise ValidationError("Menu item is not available")
        
        # Check ingredient availability
        if not menu_item.check_ingredient_availability():
            raise ValidationError("Insufficient ingredient stock")
        
        # Reduce ingredient stock if order is valid
        for recipe_item in menu_item.recipe_items.all():
            ingredient = recipe_item.ingredient
            required_quantity = recipe_item.quantity
            
            ingredient.stock_quantity -= required_quantity
            ingredient.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.id} - {self.menu_item.name} x{self.quantity}"
