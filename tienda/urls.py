"""
URL configuration for tienda project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Incluimos las URLs de cada app bajo el prefijo 'api/'
    # Django buscará coincidencias en orden.
    
    path('api/', include('usuarios.urls')),
    path('api/', include('productos.urls')),
    path('api/', include('ventas.urls')),
]