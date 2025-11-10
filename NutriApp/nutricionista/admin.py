from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Consulta


class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'nutricionista', 'data_consulta')
    search_fields = ('paciente__nome',)
    list_filter = ('nutricionista', 'data_consulta')


# ✅ registra o modelo Consulta normalmente
admin.site.register(Consulta, ConsultaAdmin)

# ⚠️ Garante que o User esteja registrado com o admin padrão do Django
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# ✅ re-registra com o UserAdmin padrão (com o botão "Alterar senha")
admin.site.register(User, UserAdmin)