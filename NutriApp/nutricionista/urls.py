from django.urls import path
from . import views

# Define o namespace da aplicação. Isso é crucial para que você use
# {% url 'nutricionista:nutri_dashboard' %} em seus templates.
app_name = 'nutricionista' 

urlpatterns = [
    # ------------------ ROTAS GERAIS E CADASTRO ------------------
    path('dashboard/', views.dashboard_nutri, name='nutri_dashboard'),
    path('paciente/cadastrar/', views.cadastrar_paciente, name='cadastrar_paciente'),
    path('selecionar_paciente/', views.selecionar_paciente, name='selecionar_paciente'),
    path('selecionar_paciente_ajax/', views.selecionar_paciente_ajax, name='selecionar_paciente_ajax'),

    # ------------------ ROTAS DE AVALIAÇÃO DO PACIENTE (Dependem do paciente_id) ------------------

    # Avaliação de Estilo de Vida
    path('paciente/<int:paciente_id>/avaliacao-estilo-vida/', 
         views.avaliacao_estilo_vida, 
         name='avaliacao_estilo_vida'),
    
    # Registro de Aspectos Clínicos e Histórico
    path('paciente/<int:paciente_id>/aspectos-clinicos/', 
         views.aspectos_clinicos, 
         name='aspectos_clinicos'),
    
    # Registro de Medicamentos e Suplementos
    path('paciente/<int:paciente_id>/medicamentos/', 
         views.medicamento, # Mantendo o nome da view original
         name='registro_medicamento'),
    
    # Visualização da Frequência de Consumo (usando a view original)
    path('paciente/<int:paciente_id>/frequencia-alimentar/', 
         views.frequencia_alimentar, 
         name='frequencia_alimentar'),

    # ------------------ ROTAS DE CONSULTA E REGISTRO ------------------ 
     path('avaliacao/<int:paciente_id>/', views.avaliacao_antropometrica, name='avaliacao_antropometrica'),
     path('paciente/<int:paciente_id>/registro-alimentar/', views.registro_alimentar, name='registro_alimentar'),

     #--------------------ROTAS PARA RESULTADOS E MEDIDAS-----------------
     path(
        'paciente/<int:paciente_id>/resultados_medidas/',
    views.resultados_medidas_view,
    name='resultados_medidas'
    ),
]