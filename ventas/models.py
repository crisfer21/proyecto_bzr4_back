from django.db import models
from productos.models import Producto
from django.utils import timezone 
from django.db import transaction 
from django.conf import settings
    
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    # Agregamos subtotal (neto) e IVA para desglosar el pago
    vendedor = models.CharField(max_length=100, blank=True)
    tipo_documento = models.CharField(max_length=20, blank= True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.pk} - Total: {self.total}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    # Este subtotal se refiere a (precio_producto * cantidad) de esa línea
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

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