from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from usuarios.permisos import IsAdminOrVendedor
from .models import Venta, Boleta, Factura, SalesState
from .serializers import BoletaSerializer, FacturaSerializer, SalesStateSerializer
from rest_framework.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.response import Response
from usuarios.permisos import IsAdmin
from django.utils import timezone
from django.db.models import Sum
from django.db import transaction

from rest_framework.permissions import AllowAny


class SalesStateViewSet(viewsets.ViewSet):
    """
    Endpoints:
    - POST /sales/state/open/   -> abrir
    - POST /sales/state/close/  -> cerrar
    - GET  /sales/state/current/-> estado actual
    """
    ##def get_permissions(self):
        # Ajusta permisos; si no quieres permiso, retorna []
        ##return [IsJefe()]

    @action(detail=False, methods=['post'])
    def open(self, request):
        opened, obj = SalesState.open()
        if not opened:
            return Response({"detail": "Las ventas ya están abiertas."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SalesStateSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def close(self, request):
        closed, obj = SalesState.close()
        if not closed:
            return Response({"detail": "Las ventas ya están cerradas."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(SalesStateSerializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def current(self, request):
        obj = SalesState.current()
        return Response(SalesStateSerializer(obj).data, status=status.HTTP_200_OK)

    
class BoletaViewSet(viewsets.ModelViewSet):
    queryset = Boleta.objects.all()
    serializer_class = BoletaSerializer


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer



