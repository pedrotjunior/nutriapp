from django.urls import path
from . import views

app_name = 'paciente'

urlpatterns = [
    path('dashboard/', views.dashboard_paciente, name='paciente_dashboard'),
    path('grafico/', views.grafico_evolucao_paciente, name='grafico_evolucao_paciente'),
]
