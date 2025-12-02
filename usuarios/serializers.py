from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    # Encriptar contraseña automáticamente
    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Datos del usuario
        user_data = {
            "id": self.user.id,
            "username": self.user.username,
            "role": self.user.role,
        }

        # Agregamos al response
        data["user"] = user_data

        return data
