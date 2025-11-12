import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from nutricionista.models import Consulta, Paciente

# =========================================
# Função separada para comparação de medidas
# =========================================
def dados_comparacao_medidas(paciente):
    consultas = Consulta.objects.filter(paciente=paciente).order_by('-data_consulta')

    dados_medidas = []
    comparacao_peso = None
    possui_duas_consultas = consultas.count() >= 2
    data_primeira = consultas.last().data_consulta if consultas.exists() else None
    data_ultima = consultas.first().data_consulta if consultas.exists() else None

    if possui_duas_consultas:
        ultima = consultas[0]
        penultima = consultas[1]

        campos = [
            ("Peso", ultima.peso, penultima.peso),
            ("Punho", ultima.circunferencia_punho, penultima.circunferencia_punho),
            ("Cintura", ultima.circunferencia_cintura, penultima.circunferencia_cintura),
            ("Braço", ultima.circunferencia_braco, penultima.circunferencia_braco),
            ("Abdome", ultima.circunferencia_abdome, penultima.circunferencia_abdome),
            ("Coxa", ultima.circunferencia_coxa, penultima.circunferencia_coxa),
            ("Quadril", ultima.circunferencia_quadril, penultima.circunferencia_quadril),
            ("Dobra Tricipital", ultima.dobra_tricipital, penultima.dobra_tricipital),
            ("Dobra Subescapular", ultima.dobra_subescapular, penultima.dobra_subescapular),
        ]

        for nome, atual, anterior in campos:
            if atual is None or anterior is None:
                continue
            diferenca = float(atual) - float(anterior)
            cor = "text-success" if diferenca < 0 else "text-danger" if diferenca > 0 else "text-secondary"
            mensagem = "Reduziu" if diferenca < 0 else "Aumentou" if diferenca > 0 else "Manteve"

            dados_medidas.append({
                "nome": nome,
                "penultimo_valor": anterior,
                "ultimo_valor": atual,
                "mensagem": mensagem,
                "cor": cor
            })

    # Comparação de peso geral
    if consultas.exists():
        primeiro_peso = consultas.last().peso
        ultimo_peso = consultas.first().peso
        if primeiro_peso and ultimo_peso:
            dif = float(ultimo_peso) - float(primeiro_peso)
            cor = "success" if dif < 0 else "danger" if dif > 0 else "secondary"
            mensagem = (
                f"Parabéns! Você perdeu {abs(dif):.2f} kg 🎉"
                if dif < 0 else
                f"Você ganhou {dif:.2f} kg ⚖️" if dif > 0 else
                "Peso mantido 👍"
            )
            comparacao_peso = {
                "primeiro_peso": primeiro_peso,
                "ultimo_peso": ultimo_peso,
                "mensagem": mensagem,
                "cor": cor,
            }

    return {
        "dados_medidas": dados_medidas,
        "comparacao_peso": comparacao_peso,
        "possui_duas_consultas": possui_duas_consultas,
        "data_primeira": data_primeira,
        "data_ultima": data_ultima
    }

# =========================================
# View principal
# =========================================
@login_required
def dashboard_paciente(request):
    paciente = get_object_or_404(Paciente, user=request.user)

    # Chama a função de comparação sem import circular
    comparacao_context = dados_comparacao_medidas(paciente)

    consultas = Consulta.objects.filter(paciente=paciente).order_by('-data_consulta')

    context = {
        "paciente": paciente,
        "consultas": consultas,
        **comparacao_context
    }

    return render(request, "paciente/dashboard_paciente.html", context)

#------------------------------------------------------------------------------------------------
#  GRAFICO DE EVOLUÇÃO DO PACIENTE
#------------------------------------------------------------------------------------------------
@login_required
def grafico_evolucao_paciente(request):
    """Exibe o gráfico de evolução do peso e circunferência do paciente logado."""

    # 1️⃣ Identifica o paciente logado
    paciente = get_object_or_404(Paciente, user=request.user)

    # 2️⃣ Busca todas as consultas ordenadas por data (mais antiga → mais recente)
    consultas = Consulta.objects.filter(paciente=paciente).order_by('data_consulta')

    # 3️⃣ Extrai dados para o gráfico
    datas = [c.data_consulta.strftime("%d/%m/%Y") for c in consultas]
    pesos = [float(c.peso) if c.peso else None for c in consultas]
    cinturas = [float(c.circunferencia_cintura) if c.circunferencia_cintura else None for c in consultas]

    # 4️⃣ Converte para JSON (para o Chart.js no template)
    datas_json = json.dumps(datas)
    pesos_json = json.dumps(pesos)
    cinturas_json = json.dumps(cinturas)

    # 5️⃣ Define se há dados suficientes para exibir o gráfico
    tem_dados = len(consultas) > 0

    # 6️⃣ Contexto enviado ao template
    context = {
        "paciente": paciente,
        "datas_json": datas_json,
        "pesos_json": pesos_json,
        "cinturas_json": cinturas_json,
        "tem_dados": tem_dados,
    }

    # 7️⃣ Renderiza o template do gráfico
    return render(request, "paciente/grafico_evolucao.html", context)

