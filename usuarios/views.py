from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from usuarios.permisos import IsAdmin

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    - Lista usuarios: solo admin
    - Crear usuarios: solo admin
    - Editar usuarios: solo admin
    - Eliminar usuarios: solo admin
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
