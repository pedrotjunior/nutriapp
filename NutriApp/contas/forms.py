from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import NutricionistaProfile
from .validators import validate_password_complexity 

# --- Formulário de Login (Mantido) ---
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

Usuario = get_user_model()

# --- Formulário de Cadastro de Nutricionista (Atualizado) ---
class NutricionistaCadastroForm(forms.ModelForm):
    
    # Validação de Senha (Mantido)
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Senha",
        validators=[validate_password_complexity], 
        help_text="A senha deve ter no mínimo 8 caracteres, com pelo menos uma letra maiúscula e um número."
    )
    confirmacao_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Senha"
    )

    endereco = forms.CharField(max_length=255, label="Rua/Avenida")
    numero = forms.CharField(max_length=10, label="Número") 
    complemento = forms.CharField(max_length=100, label = "Logadouro",required=False)
    uf = forms.CharField(max_length=2, label="UF", help_text="Ex: SP, RJ")
    cidade = forms.CharField(max_length=100, label="Cidade")
    celular = forms.CharField(max_length=20, label="Celular")
    crn = forms.CharField(max_length=20, label="CRN")

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha'] 
        labels = {
            'nome': 'Nome',
            'email': 'Email',
        }

    # Função clean(): Checa se a Senha e a Confirmação são idênticas (Mantido)
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmacao_senha = cleaned_data.get('confirmacao_senha')

        if senha and confirmacao_senha and senha != confirmacao_senha:
            self.add_error(
                'confirmacao_senha', 
                "As senhas digitadas não são idênticas. Por favor, verifique."
            )
        
        return cleaned_data
        
    def save(self, commit=True):
        """
        Salva o usuário e cria o perfil de nutricionista, incluindo os novos campos de endereço.
        """
        usuario = super().save(commit=False)
        usuario.tipo = 'NUTRI'
        usuario.set_password(self.cleaned_data['senha'])
        
        if commit:
            usuario.save()
            # Cria o perfil vinculado com os NOVOS CAMPOS
            NutricionistaProfile.objects.create(
                usuario=usuario,
                endereco=self.cleaned_data['endereco'],
                numero=self.cleaned_data['numero'],  # NOVOmakemigrations
                uf=self.cleaned_data['uf'],          # NOVO
                cidade=self.cleaned_data['cidade'],  # NOVO
                celular=self.cleaned_data['celular'],
                crn=self.cleaned_data['crn'],
                complemento=self.cleaned_data.get('complemento', '')
            )
        return usuario
