from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from usuarios.permisos import IsAdminOrVendedor, IsAdmin, IsVendedor
from .models import Boleta, Factura
from .serializers import BoletaSerializer, FacturaSerializer

from rest_framework.response import Response
from django.utils import timezone

from django.contrib.auth import get_user_model

from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from decimal import Decimal

from rest_framework.permissions import AllowAny

from rest_framework.views import APIView

from .models import SesionCaja



    
class BoletaViewSet(viewsets.ModelViewSet):
    queryset = Boleta.objects.all()
    serializer_class = BoletaSerializer


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer


class GestionCajaView(APIView):
    # GET: caja/estado/
    def get(self, request):
        # ¿Existe alguna sesión sin fecha de cierre?
        esta_abierta = SesionCaja.objects.filter(fecha_cierre__isnull=True).exists()
        return Response({"caja_abierta": esta_abierta})

class AbrirCajaView(APIView):
    # POST: caja/abrir/
    permission_classes = [AllowAny]
    def post(self, request):
        # Si ya está abierta, no hacemos nada
        if SesionCaja.objects.filter(fecha_cierre__isnull=True).exists():
            return Response({"detail": "Ya estaba abierta"}, status=status.HTTP_400_BAD_REQUEST)

        # Creamos el registro (la fecha se pone sola automática)
        SesionCaja.objects.create()
        return Response({"detail": "Caja abierta"}, status=status.HTTP_201_CREATED)
    
class CerrarCajaView(APIView):
    # POST: caja/cerrar/
    def post(self, request):
        # Buscamos la sesión activa
        sesion = SesionCaja.objects.filter(fecha_cierre__isnull=True).first()

        if not sesion:
            return Response({"detail": "No hay caja abierta"}, status=status.HTTP_400_BAD_REQUEST)

        # Cerramos poniendo la hora actual
        sesion.fecha_cierre = timezone.now()
        sesion.save()

        return Response({"detail": "Caja cerrada"}, status=status.HTTP_200_OK)
    



User = get_user_model()

class OpcionesFiltroView(APIView):
    def get(self, request):
        # 1. Obtener lista de usuarios que son vendedores (puedes filtrar por grupo o is_staff)
        vendedores = User.objects.filter(role='vendedor', is_active=True).values('id', 'username', 'first_name', 'last_name')
        
        # 2. Opcional: Obtener fechas donde hubo ventas (para bloquear días vacíos en el calendario)
        # Esto une fechas de boletas y facturas y elimina duplicados
        fechas_boletas = Boleta.objects.values_list('fecha__date', flat=True)
        fechas_facturas = Factura.objects.values_list('fecha__date', flat=True)
        # Set elimina duplicados y ordenamos
        dias_con_ventas = sorted(list(set(fechas_boletas) | set(fechas_facturas)))

        return Response({
            "vendedores": list(vendedores),
            "dias_disponibles": dias_con_ventas 
        })



class ReporteVentasView(APIView):
    def get(self, request):
        # 1. Obtener parámetros
        vendedor_id = request.query_params.get('vendedor_id')
        fecha = request.query_params.get('fecha')

        qs_boletas = Boleta.objects.all()
        qs_facturas = Factura.objects.all()

        # 2. Filtros (Vendedor y Fecha)
        if vendedor_id:
            qs_boletas = qs_boletas.filter(vendedor_id=vendedor_id)
            qs_facturas = qs_facturas.filter(vendedor_id=vendedor_id)

        if fecha:
            qs_boletas = qs_boletas.filter(fecha__date=fecha)
            qs_facturas = qs_facturas.filter(fecha__date=fecha)

        # 3. Agregación para BOLETAS (Solo totales, sin lista detallada)
        reporte_boletas = qs_boletas.aggregate(
            cantidad=Count('id'),
            total_neto=Coalesce(Sum('total_neto'), Decimal('0.00')),
            total_iva=Coalesce(Sum('total_iva'), Decimal('0.00')),
            total_final=Coalesce(Sum('total_final'), Decimal('0.00'))
        )

        # 4. Agregación para FACTURAS (Totales generales de facturas)
        reporte_facturas_totales = qs_facturas.aggregate(
            cantidad=Count('id'),
            total_neto=Coalesce(Sum('total_neto'), Decimal('0.00')),
            total_iva=Coalesce(Sum('total_iva'), Decimal('0.00')),
            total_final=Coalesce(Sum('total_final'), Decimal('0.00'))
        )

        # 5. LISTA DETALLADA DE FACTURAS
        # Usamos .values() para traer solo los campos necesarios y mejorar rendimiento
        lista_facturas = qs_facturas.values(
            'numero_factura', 
            'total_neto', 
            'total_iva', 
            'total_final'
        ).order_by('numero_factura') # Opcional: ordenar por número

        # 6. Construir Respuesta
        data = {
            "metadata": {
                "vendedor": vendedor_id if vendedor_id else "Todos",
                "fecha": fecha if fecha else "Histórico"
            },
            
            # Sección Boletas (Solo resumen)
            "resumen_boletas": {
                "cantidad_boletas": reporte_boletas['cantidad'],
                "suma_neto": reporte_boletas['total_neto'],
                "suma_iva": reporte_boletas['total_iva'],
                "suma_total": reporte_boletas['total_final']
            },

            # Sección Facturas (Resumen + Detalle)
            "facturas": {
                "resumen": {
                    "cantidad_facturas": reporte_facturas_totales['cantidad'],
                    "suma_neto": reporte_facturas_totales['total_neto'],
                    "suma_iva": reporte_facturas_totales['total_iva'],
                    "suma_total": reporte_facturas_totales['total_final']
                },
                # Aquí está la lista solicitada
                "detalle_lista": list(lista_facturas)
            }
        }

        return Response(data)