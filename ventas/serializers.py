from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from .models import Boleta, Factura, DetalleVenta, SalesState
from productos.models import Producto

# -----------------------------------------------------------------------------
# SERIALIZER DE DETALLE
# -----------------------------------------------------------------------------
class DetalleVentaSerializer(serializers.ModelSerializer):
    # Agregamos precio_unitario como write_only porque no existe en el modelo DetalleVenta,
    # pero lo necesitamos para calcular el subtotal si viene del frontend.
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    
    class Meta:
        model = DetalleVenta
        # Quitamos 'precio_unitario' de fields de lectura porque no está en la DB
        fields = ["producto", "cantidad", "subtotal", "precio_unitario"]
        read_only_fields = ["subtotal"] # El subtotal lo calcula el backend

# -----------------------------------------------------------------------------
# SERIALIZER DE BOLETA
# -----------------------------------------------------------------------------
class BoletaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Boleta
        # Quitamos "cliente" porque no existe en el modelo Boleta
        fields = [
            "id", "fecha", "vendedor", "numero_boleta",
            "total_neto", "total_iva", "total_final", "detalles"
        ]
        read_only_fields = ["fecha", "total_neto", "total_iva", "total_final", "vendedor"]

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles")
        
        # Obtenemos el usuario del contexto (request.user)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['vendedor'] = request.user

        with transaction.atomic():
            # 1. Crear la Boleta
            boleta = Boleta.objects.create(**validated_data)

            total_neto = Decimal(0)

            # 2. Procesar Detalles
            for detalle in detalles_data:
                producto = detalle["producto"]
                cantidad = detalle["cantidad"]
                precio = detalle["precio_unitario"]
                
                # Opcional: Validar que el precio coincida con producto.precio si no permites cambios manuales
                
                subtotal = Decimal(cantidad) * Decimal(precio)
                total_neto += subtotal
                
                # IMPORTANTE: Usamos 'boleta=boleta' (no venta=boleta)
                DetalleVenta.objects.create(
                    boleta=boleta,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal=subtotal
                )

            # 3. Cálculos Finales (usando Decimal)
            # IVA 19%
            iva = total_neto * Decimal('0.19')
            total_final = total_neto + iva

            boleta.total_neto = total_neto
            boleta.total_iva = iva
            boleta.total_final = total_final
            boleta.save()
            
            return boleta

# -----------------------------------------------------------------------------
# SERIALIZER DE FACTURA
# -----------------------------------------------------------------------------
class FacturaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Factura
        # Quitamos "cliente" genérico, dejamos los datos específicos de factura
        fields = [
            "id", "fecha", "vendedor", "numero_factura",
            "rut_cliente", "razon_social", "giro", "direccion",
            "total_neto", "total_iva", "total_final", "detalles"
        ]
        read_only_fields = ["fecha", "total_neto", "total_iva", "total_final", "vendedor"]

    def create(self, validated_data):
        detalles_data = validated_data.pop("detalles")
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['vendedor'] = request.user

        with transaction.atomic():
            factura = Factura.objects.create(**validated_data)

            total_neto = Decimal(0)

            for detalle in detalles_data:
                producto = detalle["producto"]
                cantidad = detalle["cantidad"]
                precio = detalle["precio_unitario"]

                subtotal = Decimal(cantidad) * Decimal(precio)
                total_neto += subtotal
                
                # IMPORTANTE: Usamos 'factura=factura'
                DetalleVenta.objects.create(
                    factura=factura,
                    producto=producto,
                    cantidad=cantidad,
                    subtotal=subtotal
                )

            iva = total_neto * Decimal('0.19')
            total_final = total_neto + iva

            factura.total_neto = total_neto
            factura.total_iva = iva
            factura.total_final = total_final
            factura.save()
            
            return factura

# -----------------------------------------------------------------------------
# SERIALIZER DE ESTADO
# -----------------------------------------------------------------------------
class SalesStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesState
        fields = ('id', 'is_open', 'updated_at')
        read_only_fields = ('id', 'updated_at')