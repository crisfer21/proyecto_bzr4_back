from django.db import models

class Producto(models.Model):
    sku = models.CharField(max_length= 12, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
