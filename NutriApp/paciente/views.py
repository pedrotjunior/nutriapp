from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from nutricionista.models import Paciente # Você vai precisar importar o modelo Paciente aqui
from django.contrib.auth.views import PasswordChangeView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from decimal import Decimal # Importação correta para o tipo de dados

# ----------------------------------------------------------------------
# FUNÇÃO - PACIENTE DASHBOARD
# ----------------------------------------------------------------------
@login_required
def paciente_dashboard(request):
    # Garante que apenas usuários do tipo PACIENTE acessem
    if request.user.tipo != 'PACIENTE':
        return redirect('login') 

    # Busca o perfil do paciente para usar no template
    paciente = get_object_or_404(Paciente, user=request.user)
    
    # Verifica se a senha é provisória e força a troca
    if paciente.senha_provisoria:
        return redirect('trocar_senha_provisoria') 

    return render(request, 'paciente/visualizar_dados.html', {'paciente': paciente})

# ----------------------------------------------------------------------
# FUNÇÃO - TROCAR A SENHA PROVISORIA
# ----------------------------------------------------------------------
# Você pode usar um decorator para garantir que apenas o paciente logado acesse
@method_decorator(login_required, name='dispatch')
class TrocarSenhaProvisoriaView(PasswordChangeView):
    # O template que você precisa criar (trocar_senha_provisoria.html)
    template_name = 'paciente/trocar_senha_provisoria.html' 
    
    # URL para onde ir após a troca bem-sucedida (o dashboard do paciente)
    success_url = reverse_lazy('visualizar_dados') 
    
    # Opcional: Adicione lógica para verificar se o usuário é PACIENTE aqui
    def dispatch(self, request, *args, **kwargs):
        if request.user.tipo != 'PACIENTE':
            return redirect('login') 
        return super().dispatch(request, *args, **kwargs)
    
# ----------------------------------------------------------------------
# FUNÇÃO - VISUALIZADOR DADOS
# ----------------------------------------------------------------------
@login_required
def visualizar_dados(request):
    """
    View placeholder para a página de visualização de dados do paciente.
    """
    # Garante que apenas usuários do tipo PACIENTE acessem (Boa prática de segurança)
    if request.user.tipo != 'PACIENTE':
        return redirect('login') 

    # TODO: Implementar a lógica para buscar e exibir os dados do paciente
    
    # Por enquanto, retorna um template vazio para que o servidor inicie.
    return render(request, 'paciente/visualizar_dados.html', {})


# Certifique-se de que todas as outras views referenciadas nas URLs estão aqui:
# def paciente_dashboard(request): ...
# class TrocarSenhaProvisoriaView(PasswordChangeView): ...

# ----------------------------------------------------------------------
# FUNÇÃO - RESULTADOS MEDIDAS
# ----------------------------------------------------------------------
@login_required
def resultados_medida_paciente(request, paciente_id):
    # Garante que o objeto Paciente existe
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    context = {
        # O objeto 'paciente' é passado, permitindo usar {{ paciente.id }} ou {{ paciente.nome }} no template
        'paciente': paciente,
        'titulo': 'Resultados das Medidas Antropométricas',
    }
    
    # CORREÇÃO: Renderiza o template de resultados_medidas
    # (Se você ainda não criou esse arquivo, crie 'nutricionista/resultados_medidas.html')
    return render(request, 'nutricionista/resultados_medidas.html', context)


@login_required
def detalhe_registro_diario(request, registro_id):
    registro = get_object_or_404(RegistroDiario, pk=registro_id)
    
    # A lista de itens é acessada diretamente!
    lista_alimentos = registro.itens_consumidos 
    
    context = {
        'registro': registro,
        'paciente': registro.paciente, # O objeto paciente está aqui
        'lista_alimentos': lista_alimentos, 
    }
    return render(request, 'nutricionista/detalhe_registro_diario.html', context)

# ----------------------------------------------------------------------
# FUNÇÃO - MEDIDAS-COMPARAÇÃO
# ----------------------------------------------------------------------
# Define as categorias de medição para a lógica de comparação
MEDIDAS_COMPARACAO = [
    # Ganhando massa (Aumento é bom, aparece em azul/verde)
    {'campo': 'circunferencia_punho', 'nome': 'Punho', 'tipo': 'ganho_bom'},
    {'campo': 'circunferencia_braco', 'nome': 'Braço', 'tipo': 'ganho_bom'}, 
    {'campo': 'circunferencia_coxa', 'nome': 'Coxa', 'tipo': 'ganho_bom'}, 
    
    # Perda de medida (Diminuição é bom, aparece em azul/verde)
    {'campo': 'circunferencia_cintura', 'nome': 'Cintura', 'tipo': 'perda_boa'},
    {'campo': 'circunferencia_quadril', 'nome': 'Quadril', 'tipo': 'perda_boa'},
    {'campo': 'circunferencia_abdome', 'nome': 'Abdômen', 'tipo': 'perda_boa'},
    {'campo': 'dobra_tricipital', 'nome': 'Dobra Tricipital', 'tipo': 'perda_boa'},
    {'campo': 'dobra_subescapular', 'nome': 'Dobra Subescapular', 'tipo': 'perda_boa'},
]


@login_required
def resultados_medidas(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    # Busca todos os registros de Consulta do paciente, ordenados pela data e, em seguida, pelo ID (mais recente primeiro)
    registros = Consulta.objects.filter(paciente=paciente).order_by('-data_consulta', '-id') 

    dados_para_template = []
    comparacao_peso = None

    if registros.exists():
        
        # 1. Obter o Último e Penúltimo Registro (Baseado em data e ID)
        ultimo_registro = registros.first() 
        penultimo_registro = registros[1] if registros.count() >= 2 else None
        
        # 2. Obter o Primeiro Registro (Baseado em data e ID, o mais antigo)
        primeiro_registro = Consulta.objects.filter(paciente=paciente).order_by('data_consulta', 'id').first()

        
        # ------------------ Lógica de Comparação de Medidas (Último vs. Penúltimo) ------------------
        for item in MEDIDAS_COMPARACAO:
            campo = item['campo']
            nome = item['nome']
            tipo = item['tipo']
            
            # Garantir que valores None sejam tratados como Decimal(0) para o cálculo
            valor_ultimo = Decimal(getattr(ultimo_registro, campo) or 0) 
            valor_penultimo = Decimal(getattr(penultimo_registro, campo) or 0) if penultimo_registro else None
            
            mensagem = "(Apenas 1 registro)"
            cor = "text-secondary"
            
            if penultimo_registro and valor_penultimo is not None:
                # Verificamos se há alteração significativa (evita comparar 0.00 com 0.00)
                if valor_ultimo != valor_penultimo:
                    
                    diferenca = abs(valor_ultimo - valor_penultimo)

                    if tipo == 'ganho_bom': # Punho, Braço, Coxa (Aumento é bom)
                        if valor_ultimo > valor_penultimo:
                            mensagem = f"Você ganhou massa! (+{diferenca:.2f})"
                            cor = "text-success" 
                        else: # valor_ultimo < valor_penultimo
                            mensagem = f"Você perdeu massa. (-{diferenca:.2f})"
                            cor = "text-danger" 
                    
                    elif tipo == 'perda_boa': # Cintura, Abdômen, Dobras (Diminuição é bom)
                        if valor_ultimo < valor_penultimo:
                            mensagem = f"Você perdeu medida! (-{diferenca:.2f})"
                            cor = "text-success"
                        else: # valor_ultimo > valor_penultimo
                            mensagem = f"Você ganhou medida. (+{diferenca:.2f})"
                            cor = "text-danger"
                else:
                    mensagem = "Sem alteração."
                        
            dados_para_template.append({
                'nome': nome,
                # Usar floatformat no template para exibir 0.00 em vez de 0
                'penultimo_valor': valor_penultimo, 
                'ultimo_valor': valor_ultimo,
                'mensagem': mensagem,
                'cor': cor
            })
            
        # ------------------ Lógica de Comparação de Peso (Primeiro vs. Último) ------------------
        
        # Garantir que os pesos sejam lidos como Decimal ou 0
        peso_primeiro_registro = Decimal(primeiro_registro.peso or 0) if primeiro_registro and primeiro_registro.peso is not None else None
        peso_ultimo_registro = Decimal(ultimo_registro.peso or 0) if ultimo_registro and ultimo_registro.peso is not None else None
        
        comparacao_peso = {}

        if peso_primeiro_registro is not None and peso_ultimo_registro is not None:
            
            diferenca = abs(peso_ultimo_registro - peso_primeiro_registro)
            
            comparacao_peso['primeiro_peso'] = peso_primeiro_registro
            comparacao_peso['ultimo_peso'] = peso_ultimo_registro
            
            if peso_ultimo_registro < peso_primeiro_registro:
                comparacao_peso['mensagem'] = f"Parabéns! Você perdeu {diferenca:.2f} kg desde a primeira consulta."
                comparacao_peso['cor'] = "text-success"
            elif peso_ultimo_registro > peso_primeiro_registro:
                comparacao_peso['mensagem'] = f"Você ganhou {diferenca:.2f} kg desde a primeira consulta."
                comparacao_peso['cor'] = "text-danger"
            else:
                comparacao_peso['mensagem'] = f"Seu peso se manteve o mesmo ({peso_primeiro_registro:.2f} kg)."
                comparacao_peso['cor'] = "text-secondary"
        else:
             comparacao_peso['mensagem'] = "Não há dados de peso suficientes para comparação."
             comparacao_peso['cor'] = "text-secondary"

    
    context = {
        'paciente': paciente,
        'titulo': 'Resultados das Medidas Antropométricas',
        'dados_medidas': dados_para_template,
        'comparacao_peso': comparacao_peso,
    }

    return render(request, 'nutricionista/resultados_medidas.html', context)