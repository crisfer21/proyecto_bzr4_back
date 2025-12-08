"""
URL configuration for tienda project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

# Vistas
from productos.views import ProductoViewSet
# Quitamos VentaViewSet porque no existe en tu views.py actual
from ventas.views import BoletaViewSet, FacturaViewSet, SalesStateViewSet
from usuarios.views import UserViewSet, CustomTokenObtainPairView

# Configuración del Router
router = routers.DefaultRouter()

# Productos
router.register('productos', ProductoViewSet)

# Usuarios
router.register('usuarios', UserViewSet)

# Ventas
# 'basename' es obligatorio porque SalesStateViewSet no tiene un queryset directo en la clase
router.register(r'state', SalesStateViewSet, basename='sales-state')
router.register(r'boletas', BoletaViewSet, basename='boleta')
router.register(r'facturas', FacturaViewSet, basename='factura')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticación JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    
    # API Principal
    path('api/', include(router.urls)),
]

# Configuración para servir imágenes en modo DEBUG (Desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)