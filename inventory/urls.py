from django.urls import path, include
from rest_framework import routers
from .views import SupplierViewSet, IngredientViewSet, MenuItemViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'menuitems', MenuItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
