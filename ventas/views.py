from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from usuarios.permisos import IsAdminOrVendedor
from .models import Venta
from .serializers import VentaSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from usuarios.permisos import IsAdmin
from django.utils import timezone
from django.db.models import Sum

from rest_framework.permissions import AllowAny



class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendedor]




    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdmin])
    def reporte_dia(self, request):
        hoy = timezone.now().date()
        ventas = Venta.objects.filter(fecha__date=hoy)
        total = ventas.aggregate(total_dia=Sum('total'))['total_dia'] or 0

        return Response({
            "fecha": str(hoy),
            "total_vendido": total,
            "cantidad_ventas": ventas.count()
        })
