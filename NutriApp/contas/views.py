from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from .forms import LoginForm, NutricionistaCadastroForm

class UsuarioLoginView(LoginView):
    template_name = 'contas/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user
        if user.tipo == 'NUTRI':
             return reverse_lazy('nutricionista:nutri_dashboard')  # ✅ corrigido
        elif user.tipo == 'PACIENTE':
            return reverse_lazy('paciente_dashboard')
        elif user.tipo == 'ADMIN':
            return reverse_lazy('admin:index')
class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy('login')

def esqueci_senha(request):
    return render(request, 'contas/esqueci_senha.html')

Usuario = get_user_model()

def cadastrar_nutricionista(request):
    if request.method == 'POST':
        form = NutricionistaCadastroForm(request.POST)
        print(">>> Dados recebidos:", request.POST)# Debug
        
        if form.is_valid():
            form.save() # Salva o usuário e o perfil
            
            # 1. REMOVIDO: login(request, usuario) - Não faz mais login automático
            
            messages.success(request, "Cadastro realizado com sucesso! Faça login com suas novas credenciais.")
            
            # 2. ALTERADO: Redireciona para a página de login
            return redirect('login') 
            
        else:
            print(">>> Formulário inválido:", form.errors)
    else:
        form = NutricionistaCadastroForm()
    
    return render(request, 'contas/cadastrar_nutricionista.html', {'form': form})