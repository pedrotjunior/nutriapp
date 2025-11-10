from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from decimal import Decimal # Importação correta para o tipo de dados
from datetime import date
import secrets
from contas.models import NutricionistaProfile
from django.db import transaction, IntegrityError
from django.db.models import Max
from .forms import (
    PacienteForm, 
    AvaliacaoEstiloVidaForm, 
    AspectosClinicosForm, 
    MedicamentoForm, 
    FrequenciaConsumoForm, 
    SelecaoPacienteForm,
    AntropometriaForm,
)
from .models import (
    Paciente, 
    RegistroDiario,
    RegistroAlimentar,
    Consulta,
    AvaliacaoEstiloVida,
    AspectosClinicos
)
from contas.models import Usuario # Assumindo Usuario está no app 'contas'

# Obtém o modelo de usuário (contas_usuario)
Usuario = get_user_model() 

# ----------------------------------------------------------------------
# FUNÇÃO DASHBOARD NUTRI
# ----------------------------------------------------------------------
@login_required 
def dashboard_nutri(request):
    # Aqui você coloca a lógica para o painel do nutricionista
    context = {} 
    return render(request, 'nutricionista/dashboard_nutri.html', context)

# ----------------------------------------------------------------------
# FUNÇÃO CADASTRAR PACIENTE
# ----------------------------------------------------------------------
@login_required(login_url='login')
def cadastrar_paciente(request):
    """Cadastra um novo paciente e seu usuário, enviando credenciais por e-mail."""

    if request.method == 'POST':
        form = PacienteForm(request.POST)

        if form.is_valid():
            # --- 1. PREPARAÇÃO DE DADOS ---
            data_nascimento = form.cleaned_data['data_nascimento']
            email_paciente = form.cleaned_data['email']
            nome_paciente = form.cleaned_data['nome']

            # Cálculo da Idade (Mantido)
            hoje = date.today()
            idade_calculada = hoje.year - data_nascimento.year - \
                              ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

            # Geração da Senha Provisória (Mantido)
            senha_provisoria = secrets.token_urlsafe(10)

            # Usar transaction.atomic para garantir atomicidade
            try:
                with transaction.atomic(): # Início da Transação Atômica

                    paciente_instance = form.save(commit=False)
                    paciente_instance.nutricionista = request.user
                    paciente_instance.idade = idade_calculada

                    # --- 2. SALVAR Usuário (contas_usuario) ---
                    # CRUCIAL: Captura o objeto do usuário recém-criado
                    novo_usuario = Usuario.objects.create(
                        email=email_paciente,
                        nome=nome_paciente,
                        password=make_password(senha_provisoria),
                        tipo='PACIENTE',
                        is_active=True,
                    )

                    # --- 3. VINCULAR E SALVAR Paciente (nutricionista_paciente) ---
                    # CORREÇÃO: Atribui o objeto Usuario recém-criado ao campo 'user' do Paciente
                    paciente_instance.user = novo_usuario
                    paciente_instance.save() # Salva a instância do Paciente com a FK 'user' preenchida
                
                # O bloco 'with transaction.atomic():' terminou, e as alterações foram commitadas
                # Se uma exceção tivesse ocorrido, tudo teria sido revertido.

                # --- 4. ENVIO DE EMAIL (Fora da Transação) ---
                # A lógica de email é um efeito colateral, é melhor mantê-la fora da transação.
                try:
                    assunto = 'Bem-vindo(a) ao NutriApp - Seus dados de acesso'
                    mensagem = f"""
Olá {nome_paciente},

Seu cadastro foi realizado com sucesso pelo seu nutricionista.
Abaixo estão seus dados de acesso ao sistema:

Email (Login): {email_paciente}
Senha Provisória: {senha_provisoria}

Acesse o sistema e troque sua senha.
[Insira aqui a URL da sua página de login]

Atenciosamente,
Sua Equipe NutriApp
"""
                    send_mail(
                        assunto,
                        mensagem,
                        settings.DEFAULT_FROM_EMAIL,
                        [email_paciente],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Erro ao enviar email: {e}") 
                    # Considerar se um erro de e-mail deve reverter o cadastro.
                    # No código atual, não reverte, o que é comum.

                # --- 5. FEEDBACK e NOVO FORMULÁRIO ---
                messages.success(request, f"Paciente {nome_paciente} cadastrado com sucesso! Credenciais enviadas por e-mail.")
                return redirect('nutricionista:cadastrar_paciente')

            except Exception as e:
                # Esta exceção captura falhas na criação do Usuário ou Paciente.
                # A transação.atomic garante o rollback automático.
                messages.error(request, "Erro ao criar usuário ou paciente. O e-mail pode já estar em uso ou houve um erro no banco de dados.")
                print(f"Erro ao criar usuário/paciente: {e}")
                return render(request, 'nutricionista/cadastrar_paciente.html', {'form': form}) 
            
        else:
            # Formulário inválido, re-renderiza com erros
            return render(request, 'nutricionista/cadastrar_paciente.html', {'form': form})
            
    else:
        # Método GET
        form = PacienteForm()
    
    return render(request, 'nutricionista/cadastrar_paciente.html', {'form': form})

# ----------------------------------------------------------------------
# FUNÇÃO SELECIONAR PACIENTE
# ----------------------------------------------------------------------
@login_required
def selecionar_paciente(request):
    user = request.user
    pacientes = Paciente.objects.filter(nutricionista=user)
    paciente_selecionado = request.session.get('paciente_nome', None)
    return render(request, 'nutricionista/selecionar_paciente.html', {
        'pacientes': pacientes,
        'paciente_selecionado': paciente_selecionado
    })

# ----------------------------------------------------------------------
# FUNÇÃO SELECIONAR PACIENTE AJAX
# ----------------------------------------------------------------------
@login_required
def selecionar_paciente_ajax(request):
    """Recebe o ID do paciente e guarda em sessão (chamado via JavaScript)."""
    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        paciente = get_object_or_404(Paciente, id=paciente_id)

        request.session['paciente_id'] = paciente.id
        request.session['paciente_nome'] = paciente.nome

        return JsonResponse({
            'status': 'ok',
            'paciente_nome': paciente.nome
        })
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

# ----------------------------------------------------------------------
# FUNLÇAO AVALIAÇÃO ESTILO DE VIDA
# ----------------------------------------------------------------------
@login_required
def avaliacao_estilo_vida(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, nutricionista=request.user)
    avaliacao_existente = AvaliacaoEstiloVida.objects.filter(paciente=paciente).first()
    form = AvaliacaoEstiloVidaForm(request.POST or None, instance=avaliacao_existente)

    salvo = False  # Flag para indicar se salvou

    if request.method == 'POST':
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.paciente = paciente
            avaliacao.save()
            salvo = True  # Ativa o alerta no template

    return render(request, 'nutricionista/avaliacao_estilo_vida.html', {
        'form': form,
        'paciente': paciente,
        'salvo': salvo,
    })

# ----------------------------------------------------------------------
# FUNÇÃO - ASPECTOS CLÍNICOS
# ----------------------------------------------------------------------
@login_required
def aspectos_clinicos(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id, nutricionista=request.user)
    aspectos_existente = AspectosClinicos.objects.filter(paciente=paciente).first()
    form = AspectosClinicosForm(request.POST or None, instance=aspectos_existente)

    if request.method == 'POST' and form.is_valid():
        aspecto = form.save(commit=False)
        aspecto.paciente = paciente
        aspecto.save()

        return HttpResponse("""
            <script>
                alert("Aspectos clínicos salvos no banco de dados!");
                setTimeout(() => { window.location.href = '/nutricionista/selecionar_paciente/'; }, 2000);
            </script>
        """)

    return render(request, 'nutricionista/aspectos_clinicos.html', {
        'form': form,
        'paciente': paciente,
    })
# ----------------------------------------------------------------------
# FUNÇÃO - MEDICAMENTO
# ----------------------------------------------------------------------
@login_required
@login_required
def medicamento(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = MedicamentoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        med = form.save(commit=False)
        med.paciente = paciente
        med.save()

        return HttpResponse("""
            <script>
                alert("Medicamentos/Suplementos salvos no banco de dados!");
                setTimeout(() => { window.location.href = '/nutricionista/selecionar_paciente/'; }, 2000);
            </script>
        """)

    return render(request, 'nutricionista/medicamento.html', {'form': form, 'paciente': paciente})
# ----------------------------------------------------------------------
# FUNÇÃO - FREQUENCIA CONSUMO VIEW
# ----------------------------------------------------------------------
@login_required
def frequencia_consumo_view(request, paciente_id): 
    """Visualiza a frequência de consumo alimentar já cadastrada (Rota original do 'urls.py' antigo)."""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    # ATENÇÃO: Implemente aqui a lógica para buscar e exibir a Frequência de Consumo
    
    # Exemplo: Buscando o último registro
    # frequencia = FrequenciaConsumo.objects.filter(paciente=paciente).last()
    
    context = {
        'paciente': paciente,
        # 'frequencia': frequencia 
    }
    
    # Rota original de renderização
    return render(request, 'nutricionista/frequencia_consumo.html', context)

# View rebatizada de registro_do_dia para registro_alimentar (GET/POST)

# ----------------------------------------------------------------------
# FUNÇÃO - FREQUENCIA ALIMENTAR
# ----------------------------------------------------------------------
def frequencia_alimentar(request, paciente_id):
    """
    Cadastra a frequência de consumo alimentar (mantendo a lógica original).
    Ao salvar, mostra um alert e redireciona em 2 segundos para a página de seleção de paciente.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = FrequenciaConsumoForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        frequencia = form.save(commit=False)
        frequencia.paciente = paciente 
        frequencia.save()

        # ✅ Mostra alerta e redireciona após 2 segundos
        return HttpResponse("""
            <script>
                alert("Frequência alimentar salva no banco de dados com sucesso!");
                setTimeout(() => {
                    window.location.href = '/nutricionista/selecionar_paciente/';
                }, 2000);
            </script>
        """)

    # --- Lógica dos campos agrupados (field_trios) ---
    field_trios = [
        ('Leite', form['leite'], form['leite_quantidade']),
        ('Queijo', form['queijo'], form['queijo_quantidade']),
        ('Frituras', form['frituras'], form['frituras_quantidade']),
        ('Arroz', form['arroz'], form['arroz_quantidade']),
        ('Massas', form['massas'], form['massas_quantidade']),
        ('Feijão/Grãos', form['feijao_graos'], form['feijao_graos_quantidade']), 
        ('Carne Boi', form['carne_boi'], form['carne_boi_quantidade']), 
        ('Carne Frango', form['carne_frango'], form['carne_frango_quantidade']), 
        ('Peixe', form['peixe'], form['peixe_quantidade']),
        ('Embutidos', form['embutidos'], form['embutidos_quantidade']), 
        ('Enlatados', form['enlatados'], form['enlatados_quantidade']),
        ('Legumes', form['legumes'], form['legumes_quantidade']),
        ('Verduras', form['verduras'], form['verduras_quantidade']), 
        ('Refrigerante', form['refrigerante'], form['refrigerante_quantidade']),
        ('Frutas', form['frutas'], form['frutas_quantidade']), 
        ('Ovos', form['ovos'], form['ovos_quantidade']),
        ('Doces', form['doces'], form['doces_quantidade']),
        ('Adoçante', form['adocante'], form['adocante_quantidade']),
        ('Café', form['cafe'], form['cafe_quantidade']),
        ('Chá', form['cha'], form['cha_quantidade']),
        ('Bolachas', form['bolachas'], form['bolachas_quantidade']),
    ]

    context = {
        'form': form, 
        'paciente': paciente,
        'field_trios': field_trios,
        'titulo': 'Frequência Alimentar'
    }
    return render(request, 'nutricionista/frequencia_alimentar.html', context)

# ----------------------------------------------------------------------
# FUNÇÃO - avaliação antropometrica
# ----------------------------------------------------------------------
@login_required
def avaliacao_antropometrica(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        form = AntropometriaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.paciente = paciente
            consulta.nutricionista = request.user
            consulta.save()
            messages.success(request, "Avaliação Antropométrica salva com sucesso. Consulta finalizada!")
            return redirect('nutricionista:nutri_dashboard')
        messages.error(request, "Erro ao salvar Avaliação Antropométrica.")
    else:
        form = AntropometriaForm()

    context = {
        'paciente': paciente,
        'titulo': 'Avaliação Antropométrica',
        'form': form,
    }
    return render(request, 'nutricionista/avaliacao_antropometrica.html', context)

# ----------------------------------------------------------------------
# FUNÇÃO - REGISTRO ALIMENTAR
# ----------------------------------------------------------------------
@login_required
def registro_alimentar(request, paciente_id): 
    # Tenta buscar o paciente
    try:
        paciente = get_object_or_404(Paciente, pk=paciente_id)
    except Paciente.DoesNotExist:
        messages.error(request, "Paciente não encontrado.")
        return redirect('nutricionista:selecionar_paciente')
        
    if request.method == 'POST':
        
        # --- DEBUG 1: IMPRIMIR TODOS OS DADOS POST RECEBIDOS ---
        print("\n--- DADOS POST RECEBIDOS NO SERVIDOR ---")
        for key, value in request.POST.items():
            print(f"POST Key: {key} | Value: '{value}'")
        print("----------------------------------------\n")
        # --------------------------------------------------------
        
        REFEICAO_PREFIXOS = {
            'cm': 'CM', 'lm': 'LM', 'al': 'AL', 'lt': 'LT', 'ja': 'JA', 'ln': 'LN'
        }
        
        form_data = request.POST
        lista_de_itens_do_dia = [] 

        try:
            # Garante que o bloco de salvamento é atômico
            with transaction.atomic():
                
                itens_processados_count = 0
                
                for html_prefix, model_code in REFEICAO_PREFIXOS.items():
                    for i in range(1, 101):
                        
                        # Constrói os nomes dos campos
                        index_suffix = f"_{html_prefix}_{i}"
                        hora_key = f"hora{index_suffix}"
                        quantidade_key = f"quantidade{index_suffix}"
                        descricao_key = f"descricao{index_suffix}"
                        unidade_key = f"unidade{index_suffix}"
                        
                        descricao_valor = form_data.get(descricao_key)
                        
                        # Se o campo de descrição não foi enviado, pare a iteração desta refeição
                        if descricao_valor is None:
                            break
                        
                        # Se o campo está vazio, pule este item
                        if not descricao_valor.strip():
                            continue 
                            
                        # Obtém outros valores
                        hora_valor = form_data.get(hora_key) or None
                        quantidade_valor = form_data.get(quantidade_key)
                        unidade_valor = form_data.get(unidade_key) or None

                        quantidade_salvamento = None
                        
                        # Tenta converter a quantidade
                        if quantidade_valor:
                            try:
                                # Usamos float pois JSONField armazena números float por padrão, não Decimals
                                quantidade_salvamento = float(quantidade_valor.replace(',', '.'))
                            except Exception:
                                quantidade_salvamento = None 
                        
                        # --- DEBUG 2: IMPRIMIR VALORES ANTES DE TENTAR SALVAR ---
                        print(f"✅ TENTATIVA DE SALVAMENTO (Key: {descricao_key}): Refeição={model_code}, Descrição='{descricao_valor.strip()}', Qtd='{quantidade_salvamento}', Unidade='{unidade_valor}', Hora='{hora_valor}'")
                        # -------------------------------------------------------------
                        
                        # Se o item é válido, adiciona à lista JSON
                        item_alimento = {
                            'refeicao_tipo': model_code,
                            'hora': hora_valor,
                            'descricao_alimento': descricao_valor.strip(),
                            'quantidade': quantidade_salvamento,
                            'unidade_medida': unidade_valor,
                        }
                        lista_de_itens_do_dia.append(item_alimento)
                        itens_processados_count += 1
                
                # CRIA OU ATUALIZA O ÚNICO REGISTRO DIÁRIO
                RegistroDiario.objects.update_or_create(
                    paciente=paciente,
                    data_registro=timezone.now().date(),
                    defaults={
                        'itens_consumidos': lista_de_itens_do_dia,
                        'hora_registro': timezone.now()
                    }
                )

                messages.success(request, f"Sucesso! {itens_processados_count} itens de registro alimentar do dia foram salvos.")
                return redirect('nutricionista:selecionar_paciente') 

        # -------------------------------------------------------------------------------------
        # BLOCAS DE EXCEÇÃO (CORRIGIDOS)
        # -------------------------------------------------------------------------------------

        except IntegrityError as e: # Fecha o try: na linha 344 com except
             messages.error(request, f"Erro de Integridade do Banco de Dados. Detalhes: {e}.")
             print(f"\n🛑 ERRO CRÍTICO DE INTEGRIDADE (IntegrityError): {e}\n")
             
             # Re-renderiza o formulário com a mensagem de erro
             context = {
                'paciente': paciente,
                'titulo': 'Registro Alimentar do Dia',
                'paciente_id': paciente_id,
             }
             return render(request, 'nutricionista/registro_alimentar.html', context)
             
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado ao salvar. Detalhe: {e}")
            print(f"\n🛑 ERRO INESPERADO (Outro Exception): {e}\n")
            
            # Re-renderiza o formulário com a mensagem de erro
            context = {
                'paciente': paciente,
                'titulo': 'Registro Alimentar do Dia',
                'paciente_id': paciente_id,
            }
            return render(request, 'nutricionista/registro_alimentar.html', context)
        
    # O código abaixo está no nível de indentação da função e é executado para requisições GET
    # -------------------------------------------------------------------------------------
    
    # Busca o registro do dia atual para pré-preencher o formulário no GET
    hoje = timezone.now().date()
    registro_hoje = None
    try:
        # Se você estiver usando o novo modelo RegistroDiario
        registro_hoje = RegistroDiario.objects.get(paciente=paciente, data_registro=hoje)
        # Se você estivesse usando o modelo RegistroAlimentar item por item, a lógica seria diferente
    except RegistroDiario.DoesNotExist:
        pass # Não faz nada, registro_hoje é None

    context = {
        'paciente': paciente,
        'titulo': 'Registro Alimentar do Dia',
        'paciente_id': paciente_id,
        'registro_hoje': registro_hoje, # Usado no template para carregar dados
    }
    return render(request,'nutricionista/registro_alimentar.html', context)

# ----------------------------------------------------------------------
# FUNÇÃO - MOSTRAR O RESULTADO DAS MEDIDAS
# ----------------------------------------------------------------------
def resultados_medidas_view(request, paciente_id):
    """
    Exibe a comparação de medidas entre a primeira e a última consulta do paciente.
    Se houver apenas uma consulta, mostra apenas essa, e deixa a coluna da segunda vazia.
    """
    paciente = get_object_or_404(Paciente, id=paciente_id)
    consultas = Consulta.objects.filter(paciente=paciente).order_by('data_consulta')

    if not consultas.exists():
        # Nenhuma consulta cadastrada
        return render(request, 'nutricionista/resultados_medidas.html', {
            'paciente': paciente,
            'dados_medidas': None,
            'comparacao_peso': None,
        })

    primeira = consultas.first()
    ultima = consultas.last()

    # Caso só exista uma consulta, não há "última" diferente
    possui_duas_consultas = consultas.count() > 1

    # --- Comparação de peso ---
    comparacao_peso = {
        'primeiro_peso': primeira.peso,
        'ultimo_peso': ultima.peso if possui_duas_consultas else None,
        'mensagem': '',
        'cor': ''
    }

    if possui_duas_consultas:
        diferenca = ultima.peso - primeira.peso
        if diferenca > 0:
            comparacao_peso['mensagem'] = f"O paciente ganhou {diferenca:.2f} kg."
            comparacao_peso['cor'] = 'text-danger'
        elif diferenca < 0:
            comparacao_peso['mensagem'] = f"O paciente perdeu {abs(diferenca):.2f} kg."
            comparacao_peso['cor'] = 'text-success'
        else:
            comparacao_peso['mensagem'] = "O peso se manteve estável."
            comparacao_peso['cor'] = 'text-secondary'
    else:
        comparacao_peso['mensagem'] = "Apenas uma consulta registrada até o momento."
        comparacao_peso['cor'] = 'text-secondary'

    # --- Campos para comparar ---
    campos = [
        ('altura', 'Altura'),
        ('circunferencia_braco', 'Circunferência do Braço'),
        ('circunferencia_cintura', 'Circunferência da Cintura'),
        ('circunferencia_abdome', 'Circunferência do Abdômen'),
        ('circunferencia_quadril', 'Circunferência do Quadril'),
        ('circunferencia_coxa', 'Circunferência da Coxa'),
        ('circunferencia_punho', 'Circunferência do Punho'),
        ('dobra_tricipital', 'Dobra Cutânea Tricipital'),
        ('dobra_subescapular', 'Dobra Cutânea Subescapular'),
    ]

    dados_medidas = []
    for campo, nome in campos:
        valor_primeira = getattr(primeira, campo, None)
        valor_ultima = getattr(ultima, campo, None) if possui_duas_consultas else None

        if possui_duas_consultas:
            diferenca = (valor_ultima or 0) - (valor_primeira or 0)
            if diferenca > 0:
                mensagem = "Aumentou"
                cor = "text-danger"
            elif diferenca < 0:
                mensagem = "Diminuiu"
                cor = "text-success"
            else:
                mensagem = "Sem alteração"
                cor = "text-secondary"
        else:
            mensagem = "Aguardando próxima consulta"
            cor = "text-secondary"

        dados_medidas.append({
            'nome': nome,
            'penultimo_valor': valor_primeira,
            'ultimo_valor': valor_ultima,
            'mensagem': mensagem,
            'cor': cor
        })

    return render(request, 'nutricionista/resultados_medidas.html', {
        'paciente': paciente,
        'dados_medidas': dados_medidas,
        'comparacao_peso': comparacao_peso,
        'data_primeira': primeira.data_consulta,
        'data_ultima': ultima.data_consulta if possui_duas_consultas else None,
        'possui_duas_consultas': possui_duas_consultas,
    })