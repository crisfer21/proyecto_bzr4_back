from rest_framework import serializers
from .models import Venta, DetalleVenta
from productos.models import Producto  # ajusta el import si tu app/producto se llama distinto

class DetalleVentaSerializer(serializers.ModelSerializer):
    # aceptar IDs de producto desde el frontend y convertir a instancia Producto
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = DetalleVenta
        # NO incluir 'venta' aquí (será asignado automáticamente)
        fields = ['producto', 'cantidad', 'subtotal']

class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True)

    class Meta:
        model = Venta
        # 'total' lo calculamos nosotros; 'id' y 'fecha' son read-only
        fields = ['id', 'fecha', 'total', 'detalles']
        read_only_fields = ('id', 'fecha', 'total')

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        # crear la venta inicialmente (total 0, lo actualizamos luego)
        venta = Venta.objects.create(**validated_data)

        total = 0
        for detalle in detalles_data:
            producto = detalle['producto']         # ya es instancia Producto por PrimaryKeyRelatedField
            cantidad = detalle['cantidad']
            # usa el subtotal enviado si viene; si no, lo calculamos con precio del producto
            subtotal = detalle.get('subtotal')
            if subtotal is None:
                subtotal = producto.precio * cantidad

            # crear detalle asignando la venta
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                subtotal=subtotal
            )
            total += subtotal

        venta.total = total
        venta.save()
        return venta
