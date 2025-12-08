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


class SalesState(models.Model):
    """
    Singleton simple que guarda el estado global de ventas.
    Usamos pk=1 como única fila esperada; get_or_create(pk=1) lo garantiza.
    """
    is_open = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estado de ventas"
        verbose_name_plural = "Estado de ventas"

    def __str__(self):
        return "ABIERTO" if self.is_open else "CERRADO"

    @classmethod
    def _ensure_singleton(cls):
        # Crea la fila si no existe (sin lock). Luego la bloqueamos con select_for_update cuando haga falta.
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'is_open': False})
        return obj

    @classmethod
    def open(cls):
        """
        Intenta abrir las ventas.
        Devuelve (True, instance) si abrió; (False, instance) si ya estaba abierto.
        """
        cls._ensure_singleton()
        with transaction.atomic():
            # bloquea la fila para evitar race conditions
            obj = cls.objects.select_for_update().get(pk=1)
            if obj.is_open:
                return False, obj
            obj.is_open = True
            obj.updated_at = timezone.now()
            obj.save()
            return True, obj

    @classmethod
    def close(cls):
        """
        Intenta cerrar las ventas.
        Devuelve (True, instance) si cerró; (False, instance) si ya estaba cerrado.
        """
        cls._ensure_singleton()
        with transaction.atomic():
            obj = cls.objects.select_for_update().get(pk=1)
            if not obj.is_open:
                return False, obj
            obj.is_open = False
            obj.updated_at = timezone.now()
            obj.save()
            return True, obj

    @classmethod
    def current(cls):
        """
        Devuelve la instancia (si existe) o crea la singleton si no.
        """
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'is_open': False})
        return obj