from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, CustomTokenObtainPairView

# Router específico de usuarios
router = routers.DefaultRouter()

router.register('usuarios', UserViewSet)

urlpatterns = [
    # Rutas del router (api/usuarios/...)
    path('', include(router.urls)),

    # Rutas de Autenticación (api/auth/...)
    # Nota: Las moví aquí para que estén agrupadas con la app de usuarios
    path('auth/login/', CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('auth/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
]