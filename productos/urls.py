from django.urls import path, include
from rest_framework import routers
from .views import ProductoViewSet

# Router específico de productos
router = routers.DefaultRouter()
router.register('productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]