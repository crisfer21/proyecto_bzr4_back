from django.db import models
from django.utils import timezone 
from django.db import transaction 
from django.conf import settings
from productos.models import Producto
from usuarios.models import User

    
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="%(class)s_ventas")
    total_neto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        abstract = True


    def __str__(self):
        return f"Venta #{self.pk} - Total: {self.total_final}"
    
class Boleta(Venta):
    numero_boleta = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Boleta {self.numero_boleta} - {self.total_final}"


class Factura(Venta):
    numero_factura = models.CharField(max_length=20, unique=True)
    rut_cliente = models.CharField(max_length=12)
    razon_social = models.CharField(max_length=200)
    giro = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.razon_social}"


# Detalle de cada venta
class DetalleVenta(models.Model):
    # Relación polimórfica: puede ser Boleta o Factura
    # Para simplificar, se puede usar una ForeignKey a cada tipo
    boleta = models.ForeignKey(Boleta, on_delete=models.CASCADE, related_name="detalles", null=True, blank=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name="detalles", null=True, blank=True)

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x {self.cantidad} = {self.subtotal}"



from django.db import models

class SesionCaja(models.Model):
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sesión {self.id} - {'ABIERTA' if not self.fecha_cierre else 'CERRADA'}"