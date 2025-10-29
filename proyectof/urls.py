from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('productos/', include('productos.urls')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path("produccion/", include("produccion.urls")),
    path('kardex/', include('kardex.urls')),
    path('clientes/', include('clientes.urls')),

    # Home simple: redirige a login o lista de usuarios
    path('', lambda request: redirect('accounts:users_list') if request.user.is_authenticated else redirect('accounts:login')),
]
