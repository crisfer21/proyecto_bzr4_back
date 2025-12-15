from django.urls import path, include
from rest_framework import routers
from .views import BoletaViewSet, FacturaViewSet, GestionCajaView, AbrirCajaView, CerrarCajaView, OpcionesFiltroView, ReporteVentasView

# Router específico de ventas
router = routers.DefaultRouter()
router.register(r'boletas', BoletaViewSet, basename='boleta')
router.register(r'facturas', FacturaViewSet, basename='factura')

urlpatterns = [
    # Rutas del router (api/boletas/, api/facturas/)
    path('', include(router.urls)),

    path('filtros-reporte/', OpcionesFiltroView.as_view(), name='filtros-reporte'),

    path('reporte-ventas/', ReporteVentasView.as_view(), name='reporte-ventas'),

    # Rutas manuales de Caja (api/caja/...)
    path('caja/estado/', GestionCajaView.as_view(), name='caja-estado'),
    path('caja/abrir/', AbrirCajaView.as_view(), name='caja-abrir'),
    path('caja/cerrar/', CerrarCajaView.as_view(), name='caja-cerrar'),
]