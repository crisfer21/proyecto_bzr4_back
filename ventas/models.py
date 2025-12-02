from django.db import models
from productos.models import Producto  # importa el modelo ya existente

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # usa el modelo existente
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
