from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory.views import (
    SupplierViewSet, 
    IngredientViewSet, 
    MenuItemViewSet, 
    OrderViewSet,
    LandingPageView
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
