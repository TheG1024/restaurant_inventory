from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, IngredientViewSet, MenuItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
