from django.db import models
from django.utils import timezone
from django.conf import settings
from contas.models import Usuario
from django.db.models.fields.json import JSONField # Importe o JSONField
from django.contrib.auth.models import User

# ----------------------------------------------------------------------
# MODEL - PACIENTE
# ----------------------------------------------------------------------
class Paciente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_paciente', null=True)

    nutricionista = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo':'NUTRI'})
    nome = models.CharField(max_length=150)
    idade = models.IntegerField()
    data_nascimento = models.DateField()
    endereco = models.CharField(max_length=255)
    numero_endereco = models.CharField(max_length=10, verbose_name='Nº') # Numero na mesma linha do endereço
    complemento = models.CharField(max_length=100, blank=True, null=True) # Pode ser nulo
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2, verbose_name='UF') # UF na mesma linha da cidade
    cep = models.CharField(max_length=20)
    celular = models.CharField(max_length=20)
    email = models.EmailField()
    motivo_consulta = models.TextField()
    senha_provisoria = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.nome
        
    # Recomendado: Método para calcular a idade no próprio modelo
    def calcular_idade(self):
        from datetime import date
        hoje = date.today()
        # Cálculo: Ano atual - Ano de nascimento - (1 se o aniversário ainda não ocorreu)
        return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
    
# ----------------------------------------------------------------------
# MODEL - AVALIAÇÃO ESTILO VIDA
# ----------------------------------------------------------------------
class AvaliacaoEstiloVida(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    profissao = models.CharField(max_length=100)
    mora_sozinha = models.BooleanField()
    fumo = models.BooleanField()
    bebida_alcoolica = models.BooleanField()
    ativ_fisica = models.BooleanField()
    tipo_atividade = models.CharField(max_length=100, blank=True, null=True)
    frequencia_atividade = models.CharField(max_length=50, blank=True, null=True)
    horario_atividade = models.CharField(max_length=50, blank=True, null= True)
    local_refeicoes = models.CharField(max_length=100)
    sozinho_refeicoes = models.BooleanField()
    quem_prepara_comida = models.CharField(max_length=50)
    horario_maior_fome = models.CharField(max_length=50)
    quem_faz_compras = models.CharField(max_length=50)
    horas_sono = models.FloatField()
    aversoes_alimentares = models.BooleanField()
    preferencias_alimentares = models.TextField()

# ----------------------------------------------------------------------
# MODEL - ASPECTOS CLINICOS 
# ----------------------------------------------------------------------
class AspectosClinicos(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)
    cirurgias = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    hipertensao = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    diabetes = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    problemas_cardiovasculares =models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    hipercolesterolemia = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    cancer = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    anemias = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])
    hipotiroidismo = models.CharField(max_length=10, choices=[('Sim','Sim'), ('Não','Não'),('Familiares','Familiares')])

# ----------------------------------------------------------------------
# MODEL - MEDICAMENTO
# ----------------------------------------------------------------------
class Medicamento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    dose = models.CharField(max_length=50)
    vezes_por_dia = models.CharField(max_length=50)

# ----------------------------------------------------------------------
# MODEL - FREQUENCIA CONSUMO
# ----------------------------------------------------------------------
# Definição das Choices para Frequência (Assumindo que está em models.py ou um arquivo de constants)
FREQUENCIA_CHOICES = [
    ('dia', 'Dia'), 
    ('semana', 'Semana'), 
    ('mês', 'Mês'), 
    ('eventualmente', 'Eventualmente'), 
    ('nunca', 'Nunca')
]

# Definição das Choices para Quantidade
QUANTIDADE_CHOICES = [
    ('1', '1'), 
    ('2', '2'), 
    ('3', '3'), 
    ('4', '4'), 
    ('5', '5'), 
    ('+5', '+5 ou mais') # Ajustei o rótulo para ser mais claro
]

# CLASSE COMPLETADA
class FrequenciaConsumo(models.Model): 
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    data_registro = models.DateTimeField(auto_now_add=True)
    
    # -----------------------------------------------------------
    # CAMPOS DE FREQUÊNCIA (CHARFIELD com choices)
    # -----------------------------------------------------------
    leite = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    queijo = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    frituras = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    arroz = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    massas = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    feijao_graos = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES) # Campo que estava truncado
    carne_boi = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    carne_frango = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    peixe = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    embutidos = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    enlatados = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    legumes = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    verduras = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    refrigerante = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    frutas = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    ovos = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    doces = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    adocante = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    cafe = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    cha = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    bolachas = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    
    # -----------------------------------------------------------
    # CAMPOS DE QUANTIDADE (CHARFIELD com choices)
    # -----------------------------------------------------------
    leite_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    queijo_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    frituras_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    arroz_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    massas_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    feijao_graos_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    carne_boi_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    carne_frango_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    peixe_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    embutidos_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    enlatados_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    legumes_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    verduras_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    refrigerante_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    frutas_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    ovos_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    doces_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    adocante_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    cafe_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    cha_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    bolachas_quantidade = models.CharField(max_length=10, choices=QUANTIDADE_CHOICES)
    
    def __str__(self):
        return f"Frequência de Consumo de {self.paciente.nome} em {self.data_registro.strftime('%Y-%m-%d')}"

# ----------------------------------------------------------------------
# MODEL - CONSULTA
# ----------------------------------------------------------------------
class Consulta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    nutricionista = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo':'NUTRI'})
    data_consulta = models.DateField(default=timezone.now)
    
    # Campos Antropométricos (apenas os do AntropometriaForm para referência)
    circunferencia_punho = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_cintura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_quadril = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_braco = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_abdome = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    circunferencia_coxa = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_tricipital = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dobra_subescapular = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Consulta de {self.paciente.nome} em {self.data_consulta}"

# ----------------------------------------------------------------------
# MODEL - REGISTRO ALIMENTAR
# ----------------------------------------------------------------------
# CLASSE RegistroAlimentar - Necessária para o Registro Alimentar
class RegistroAlimentar(models.Model):
    REFEICAO_CHOICES = [
        ('CM', 'Café da Manhã'),
        ('LM', 'Lanche da Manhã'),
        ('AL', 'Almoço'),
        ('LT', 'Lanche da Tarde'),
        ('JA', 'Jantar'),
        ('LN', 'Lanche da Noite/Ceia'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    data_registro = models.DateField(default=timezone.now)
    refeicao_tipo = models.CharField(max_length=2, choices=REFEICAO_CHOICES)
    hora = models.TimeField(null=True, blank=True)
    descricao_alimento = models.CharField(max_length=255)
    # DecimalField para a quantidade, permitindo vírgula (que é tratada na view)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unidade_medida = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.get_refeicao_tipo_display()} de {self.paciente.nome} em {self.data_registro}"
    
# ----------------------------------------------------------------------
# MODEL - REGISTRO DIARIO
# ----------------------------------------------------------------------
# O modelo que vai armazenar a lista (a "lista" que você mencionou)
class RegistroDiario(models.Model):
    # Relação com o paciente
    paciente = models.ForeignKey(
        'Paciente', 
        on_delete=models.CASCADE, 
        related_name='registros_diarios'
    )
    
    # Armazena a data em que o registro foi criado/salvo (a data para o link)
    data_registro = models.DateField(default=timezone.now)
    
    # Armazena a hora exata da inserção no sistema
    hora_registro = models.DateTimeField(default=timezone.now) 

    # O campo principal: armazena a lista de alimentos em formato JSON
    # Este campo guardará a estrutura que você está iterando no POST
    itens_consumidos = JSONField(default=list, blank=True) 
    
    class Meta:
        # Garante que cada paciente tenha apenas 1 registro por dia (ou ajuste se for mais de uma consulta)
        unique_together = ('paciente', 'data_registro')
        ordering = ['-data_registro']

    def __str__(self):
        return f"Registro de {self.paciente.nome} em {self.data_registro.strftime('%d/%m/%Y')}"