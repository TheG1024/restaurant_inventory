from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)
    expiry_date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    recipe = models.JSONField()  # Store ingredient quantities as JSON
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Order(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order_date = models.DateTimeField(auto_now_add=True)
