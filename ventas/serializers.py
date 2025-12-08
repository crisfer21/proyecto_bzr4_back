from rest_framework import serializers
from decimal import Decimal # Importante para cálculos monetarios precisos
from .models import Venta, DetalleVenta, SalesState
from productos.models import Producto
from usuarios.serializers import UserSerializer

class DetalleVentaSerializer(serializers.ModelSerializer):
    # aceptar IDs de producto desde el frontend y convertir a instancia Producto
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'subtotal']

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        # AGREGADOS: 'subtotal' e 'iva' para que se devuelvan en la respuesta JSON
        fields = ['id', 'fecha', 'vendedor', 'tipo_documento', 'subtotal', 'iva', 'total', 'detalles']
        # Los marcamos como read_only porque los calcularemos en el backend para seguridad
        read_only_fields = ('id', 'fecha', 'subtotal', 'iva', 'total')

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        # Creamos la venta vacía primero
        venta = Venta.objects.create(**validated_data)

        acumulado_subtotal = Decimal(0) # Usamos Decimal para precisión

        for detalle in detalles_data:
            producto = detalle['producto']
            cantidad = detalle['cantidad']
            
            # Verificamos si el frontend mandó el subtotal, si no lo calculamos
            subtotal_linea = detalle.get('subtotal')
            if subtotal_linea is None:
                subtotal_linea = producto.precio * cantidad
            
            # Convertimos a Decimal por seguridad si viene como float
            subtotal_linea = Decimal(subtotal_linea)

            # crear detalle asignando la venta
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                subtotal=subtotal_linea
            )
            acumulado_subtotal += subtotal_linea

        # --- LÓGICA DE CÁLCULO ACTUALIZADA ---
        # 1. Asignamos el subtotal (suma de los productos)
        venta.subtotal = acumulado_subtotal
        
        # 2. Calculamos IVA (19%)
        venta.iva = acumulado_subtotal * Decimal('0.19')
        
        # 3. Calculamos Total Final
        venta.total = venta.subtotal + venta.iva
        
        venta.save()
        return venta
    
class SalesStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesState
        fields = ('id', 'is_open', 'updated_at')
        read_only_fields = ('id', 'updated_at')