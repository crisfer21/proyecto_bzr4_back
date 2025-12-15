from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from usuarios.permisos import IsAdmin, IsAdminOrVendedor
from .models import Producto
from .serializers import ProductoSerializer

from rest_framework.filters import SearchFilter

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrVendedor]  

    filter_backends = [SearchFilter]
    search_fields = ['nombre', 'sku' ]