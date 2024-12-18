from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F

from .models import Supplier, Ingredient, MenuItem, Order, OrderStatus
from .serializers import (
    SupplierSerializer, 
    IngredientSerializer, 
    MenuItemSerializer, 
    OrderSerializer
)

from django.views.generic import TemplateView

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'rating']

    @action(detail=True, methods=['POST'])
    def deactivate(self, request, pk=None):
        """Custom action to deactivate a supplier"""
        supplier = self.get_object()
        supplier.is_active = False
        supplier.save()
        return Response({'status': 'supplier deactivated'})

    @action(detail=False, methods=['GET'])
    def low_rating_suppliers(self, request):
        """Retrieve suppliers with low ratings"""
        low_rating_suppliers = self.queryset.filter(rating__lt=3.0)
        serializer = self.get_serializer(low_rating_suppliers, many=True)
        return Response(serializer.data)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['supplier', 'unit', 'storage_type']
    search_fields = ['name']
    ordering_fields = ['stock_quantity', 'cost_per_unit', 'expiry_date']

    @action(detail=False, methods=['GET'])
    def low_stock_ingredients(self, request):
        """Retrieve ingredients with low stock"""
        low_stock = self.queryset.filter(stock_quantity__lte=F('minimum_stock_level'))
        serializer = self.get_serializer(low_stock, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def adjust_stock(self, request, pk=None):
        """Manually adjust ingredient stock"""
        ingredient = self.get_object()
        quantity = request.data.get('quantity', 0)
        
        try:
            quantity = float(quantity)
        except ValueError:
            return Response(
                {'error': 'Invalid quantity'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ingredient.stock_quantity += quantity
        ingredient.save()
        
        serializer = self.get_serializer(ingredient)
        return Response(serializer.data)

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_vegetarian', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'preparation_time_minutes']

    @action(detail=False, methods=['GET'])
    def unavailable_items(self, request):
        """Retrieve unavailable menu items"""
        unavailable = self.queryset.filter(is_available=False)
        serializer = self.get_serializer(unavailable, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def toggle_availability(self, request, pk=None):
        """Toggle menu item availability"""
        menu_item = self.get_object()
        menu_item.is_available = not menu_item.is_available
        menu_item.save()
        
        serializer = self.get_serializer(menu_item)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'menu_item', 'customer_name']
    search_fields = ['customer_name', 'menu_item__name']
    ordering_fields = ['order_date', 'total_price']

    @action(detail=False, methods=['GET'])
    def pending_orders(self, request):
        """Retrieve pending orders"""
        pending = self.queryset.filter(status='PEND')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        """Update order status"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(OrderStatus.choices):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def daily_sales(self, request):
        """Calculate daily sales"""
        from django.db.models import Sum
        from django.utils import timezone
        
        today = timezone.now().date()
        daily_sales = (
            self.queryset
            .filter(order_date__date=today, status='COMP')
            .annotate(total=F('menu_item__price') * F('quantity'))
            .aggregate(total_sales=Sum('total'))
        )
        
        return Response({'daily_sales': daily_sales['total_sales'] or 0})

class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add additional context data here if needed
        context['title'] = 'Restaurant Inventory Management System'
        return context
