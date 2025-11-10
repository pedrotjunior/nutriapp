from django.urls import path
from . import views


app_name = 'paciente'

urlpatterns = [
    # Dashboard principal do paciente (redireciona para o perfil por enquanto)
    path('dashboard/', views.paciente_dashboard, name='paciente_dashboard'),
    
    # Visualização de dados de perfil, lista de registros e informações gerais
    path('meus-dados/', views.visualizar_dados, name='paciente_dados'),
    
    # Força a troca de senha provisória
    path('trocar-senha/', views.TrocarSenhaProvisoriaView.as_view(), name='trocar_senha_provisoria'),
    
    # Visualização dos resultados antropométricos do paciente logado
    # Sem necessidade de paciente_id, pois usa o usuário logado
    path('meus-resultados-medidas/', views.resultados_medidas, name='resultados_medidas'),
    
    # Detalhe de um registro diário específico
    path('registro/<int:registro_id>/detalhe/', views.detalhe_registro_diario, name='detalhe_registro_diario'),
]