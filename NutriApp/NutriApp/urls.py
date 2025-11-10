from django.urls import path, include
from django.contrib import admin
from django.shortcuts import redirect
from contas.views import UsuarioLoginView, UsuarioLogoutView, cadastrar_nutricionista, esqueci_senha

urlpatterns = [
    path('admin/', admin.site.urls),
    
     # Rotas de login/logout e página inicial
    path('login/', UsuarioLoginView.as_view(), name='login'),
    path('logout/', UsuarioLogoutView.as_view(), name='logout'),
    path('', lambda request: redirect('login')),
    
    # Cadastro e recuperação de senha
    path('cadastrar-nutricionista/', cadastrar_nutricionista, name='cadastrar_nutricionista'),
    path('esqueci-senha/', esqueci_senha, name='esqueci_senha'),
    
    # Apps principais
    path('nutricionista/', include('nutricionista.urls', namespace='nutricionista')),
    path('paciente/', include('paciente.urls', namespace='paciente')),
]

