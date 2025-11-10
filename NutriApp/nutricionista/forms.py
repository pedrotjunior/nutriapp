from django import forms
from datetime import datetime
from django.contrib.auth import get_user_model
from .models import (
    Paciente, 
    AvaliacaoEstiloVida, 
    AspectosClinicos, 
    Medicamento, 
    FrequenciaConsumo,
    Consulta,
)

# Lista de tuplas (valor_a_salvar, rótulo_a_mostrar)
ESTADOS_BRASILEIROS = (
   ('', 'UF'), # Opção inicial/placeholder
    ('AC', 'AC'),
    ('AL', 'AL'),
    ('AP', 'AP'),
    ('AM', 'AM'),
    ('BA', 'BA'),
    ('CE', 'CE'),
    ('DF', 'DF'),
    ('ES', 'ES'),
    ('GO', 'GO'),
    ('MA', 'MA'),
    ('MT', 'MT'),
    ('MS', 'MS'),
    ('MG', 'MG'),
    ('PA', 'PA'),
    ('PB', 'PB'),
    ('PR', 'PR'),
    ('PE', 'PE'),
    ('PI', 'PI'),
    ('RJ', 'RJ'),
    ('RN', 'RN'),
    ('RS', 'RS'),
    ('RO', 'RO'),
    ('RR', 'RR'),
    ('SC', 'SC'),
    ('SP', 'SP'),
    ('SE', 'SE'),
    ('TO', 'TO'),
)

class PacienteForm(forms.ModelForm):
    uf = forms.ChoiceField(
        choices=ESTADOS_BRASILEIROS,
        initial='SP',
        label='',
    )

    class Meta:
        model = Paciente
        
        # CORREÇÃO CRUCIAL: Adicione 'user' à lista de exclusão!
        exclude = ['nutricionista', 'idade', 'user'] 
        
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'numero_endereco': forms.TextInput(attrs={'placeholder': 'Nº'}),
        }
        
        labels = {
            'data_nascimento': 'Data de Nascimento',
            'motivo_consulta': 'Motivo da Consulta',
            'numero_endereco': ' ', 
            'complemento': 'Complemento',
            'cidade': 'Cidade',
            'uf': ' ',
        }

class SelecaoPacienteForm(forms.Form):
    # O campo de seleção deve ser um ModelChoiceField se estiver linkado a um modelo
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.none(),
        label="Selecione o Paciente"
    )

    def __init__(self, *args, **kwargs):
        # 1. Tenta extrair o 'user' dos kwargs (passado pela view)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # 2. Se o usuário estiver presente, filtra a queryset
        if user is not None:
            # Filtra Pacientes onde o campo 'nutricionista' é o usuário logado
            self.fields['paciente'].queryset = Paciente.objects.filter(
                nutricionista=user
            ).order_by('nome')

# Formulário Avaliação de Estilo de Vida
class AvaliacaoEstiloVidaForm(forms.ModelForm):
    SIM_NAO = [
        (True, "Sim"),
        (False, "Não"),
    ]

    mora_sozinha = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Mora sozinha?")
    fumo = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Fuma?")
    bebida_alcoolica = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Consome bebida alcoólica?")
    ativ_fisica = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Pratica atividade física?")
    sozinho_refeicoes = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Faz refeições sozinho(a)?")
    aversoes_alimentares = forms.ChoiceField(choices=SIM_NAO, widget=forms.RadioSelect, label="Tem aversões alimentares?")

    class Meta:
        model = AvaliacaoEstiloVida
        fields = [
            "profissao",
            "mora_sozinha",
            "fumo",
            "bebida_alcoolica",
            "ativ_fisica",
            "tipo_atividade",
            "frequencia_atividade",
            "horario_atividade",
            "local_refeicoes",
            "sozinho_refeicoes",
            "quem_prepara_comida",
            "horario_maior_fome",
            "quem_faz_compras",
            "horas_sono",
            "aversoes_alimentares",
            "preferencias_alimentares",
        ]

# Formulário Aspectos Clínicos
class AspectosClinicosForm(forms.ModelForm):
    class Meta:
        model = AspectosClinicos
        fields = ['cirurgias','hipertensao','diabetes','problemas_cardiovasculares',
                  'hipercolesterolemia','cancer','anemias','hipotiroidismo']

# Formulário Medicamento
class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nome','dose','vezes_por_dia']

User = get_user_model()

class AntropometriaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = [
            'circunferencia_punho',
            'circunferencia_cintura',
            'circunferencia_quadril',
            'circunferencia_braco',
            'circunferencia_abdome',
            'circunferencia_coxa',
            'dobra_tricipital',
            'dobra_subescapular',
            'observacoes',
            'peso',
            'altura',
        ]

class FrequenciaConsumoForm(forms.ModelForm):
    class Meta:
        model = FrequenciaConsumo
        # O campo 'paciente' será preenchido na view, então exclua-o do formulário.
        fields = ['leite', 'queijo', 'frituras', 'arroz', 'massas', 'feijao_graos',
                  'carne_boi', 'carne_frango', 'peixe', 'embutidos', 'enlatados',
                  'legumes', 'verduras', 'refrigerante', 'frutas', 'ovos', 'doces', 
                  'adocante', 'cafe','cha', 'bolachas','leite_quantidade','queijo_quantidade',
                  'frituras_quantidade','arroz_quantidade','massas_quantidade','feijao_graos_quantidade',
                  'carne_boi_quantidade','carne_frango_quantidade','peixe_quantidade','embutidos_quantidade',
                  'enlatados_quantidade','legumes_quantidade','verduras_quantidade','refrigerante_quantidade',
                  'frutas_quantidade','ovos_quantidade','doces_quantidade','adocante_quantidade','cafe_quantidade',
                  'cha_quantidade','bolachas_quantidade',
        ] # <--- Inclua todos os campos de frequência aqui
        

