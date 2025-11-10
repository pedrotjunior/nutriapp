from django.urls import path
from django.shortcuts import redirect
# Importa as views padrão de autenticação do Django
from django.contrib.auth import views as auth_views
# Mantém a importação da sua view customizada de cadastro
from .views import cadastrar_nutricionista

# Define o namespace da aplicação (CRÍTICO para evitar colisões e para referências no settings.py)
app_name = 'contas'

urlpatterns = [
    # Rota de Index (Redireciona para o login)
    path('', lambda request: redirect('login')),
    
    # ----------------------------------------------------
    # AUTENTICAÇÃO
    # ----------------------------------------------------
    
    # Login (Usando a view padrão do Django)
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html' # Use o template HTML que você criou para o formulário de login
    ), name='login'),

    # Logout (Usando a view padrão do Django)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Cadastro de Nutricionista (Mantendo sua view customizada)
    path('cadastrar-nutricionista/', cadastrar_nutricionista, name='cadastrar_nutricionista'),

    # ----------------------------------------------------
    # FLUXO DE REDEFINIÇÃO DE SENHA (PASSWORD RESET)
    # ----------------------------------------------------
    
    # 1. Solicitação de E-mail para redefinição
    path('esqueci-senha/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html', # Template com o formulário de e-mail
        email_template_name='registration/password_reset_email.html', 
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/contas/esqueci-senha/enviado/'
    ), name='password_reset'),

    # 2. Confirmação de Envio do E-mail
    path('esqueci-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html' # Template de confirmação
    ), name='password_reset_done'),

    # 3. Troca de Senha (URL acessada através do link no e-mail)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html', # Template para o novo formulário de senha
        success_url='/contas/esqueci-senha/completo/'
    ), name='password_reset_confirm'),

    # 4. Confirmação de que a troca foi concluída
    path('esqueci-senha/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html' # Template final de sucesso
    ), name='password_reset_complete'),
]
