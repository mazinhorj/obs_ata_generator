from fpdf import FPDF
import datetime

# --- CONSTANTES DE TEXTO ---
TEXTOS_PADRAO = {
    "1": {
        "singular": "O aluno {nomes}, retido por insuficiência de frequência em {ano_anterior}, foi reclassificado em {ano_corrente}, de acordo com LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso II.",
        "plural": "Os alunos {nomes}, retidos por insuficiência de frequência em {ano_anterior}, foram reclassificados em {ano_corrente}, de acordo com LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso II."
    },
    "2": {
        "singular": "O aluno {nomes}, retido por infrequência em {ano_corrente} foi indicado a reclassificação de acordo com o Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso II; LDB Art.23, §1º.",
        "plural": "Os alunos {nomes}, retidos por infrequência em {ano_corrente} foram indicados a reclassificação de acordo com o Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso II; LDB Art.23, §1º."
    },
    # TIPO 7 COM DATA DE REGISTRO
    "7": {
        "1": {  # Sem comprovação
            "singular": "O aluno {nomes} foi Classificado em {data_registro}, de acordo com a LDBEN nº 9394/1996, Art. 24, inciso II, alínea c e Regimento Escolar da Rede Municipal de Duque de Caxias, Art. 92 - §§ 1º e 2º.",
            "plural":   "Os alunos {nomes} foram Classificados em {data_registro}, de acordo com a LDBEN nº 9394/1996, Art. 24, inciso II, alínea c e Regimento Escolar da Rede Municipal de Duque de Caxias, Art. 92 - §§ 1º e 2º."
        },
        "2": {  # Transferência
            "singular": "O aluno {nomes} foi Reclassificado em {data_registro}, de acordo com a LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso I.",
            "plural":   "Os alunos {nomes} foram Reclassificados em {data_registro}, de acordo com a LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso I."
        },
        "3": {  # Exterior
            "singular": "O aluno {nomes} foi Reclassificado em {data_registro}, de acordo com a LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso I.",
            "plural":   "Os alunos {nomes} foram Reclassificados em {data_registro}, de acordo com a LDBEN nº 9394/1996- Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias Art.94, inciso I."
        },
        "4": {  # PP para EJA
            "singular": "O aluno {nomes} foi Reclassificado em {data_registro}, de acordo com a LDBEN 9394/1996 Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias, Art.94, Inciso III.",
            "plural":   "Os alunos {nomes} foram Reclassificados em {data_registro}, de acordo com a LDBEN 9394/1996 Art. 23, § 1º e Regimento Escolar da Rede Municipal de Duque de Caxias, Art.94, Inciso III."
        }
    },
    "3": "Considerando o Regimento Escolar da Rede Municipal de Duque de Caxias, artigo 86, os alunos abaixo relacionados, em Regime de Progressão Parcial feita através de Programa de Estudos, obtiveram as seguintes médias finais:\n{lista_alunos}",
    "4": "De acordo com LDBEN nº9394/1996 artigo 24, inciso III e o artigo 86 do Regimento Escolar da Rede Municipal de Duque de Caxias, os alunos abaixo relacionados foram promovidos em Regime de Progressão Parcial que será feita através de Programa de Estudos nos Componentes Curriculares:\n{lista_alunos}",
    "5": "Os alunos abaixo frequentaram o Atendimento Educacional Especializado nesta unidade escolar:\n{lista_alunos}",
    "6": "Os alunos abaixo são matriculados nesta Unidade Escolar nas seguintes turmas do Ensino Regular:\n{lista_alunos}"
}


def formatar_lista_nomes(nomes):
    """Junta nomes com vírgula e 'e' no final."""
    if not nomes:
        return ""
    nomes = [n.upper() for n in nomes]
    if len(nomes) == 1:
        return nomes[0]
    return ", ".join(nomes[:-1]) + " e " + nomes[-1]


def gerar_texto_observacao(tipo, dados):
    ano_atual = datetime.date.today().year
    ano_anterior = ano_atual - 1

    if tipo in ["1", "2"]:
        nomes = formatar_lista_nomes(dados['alunos'])
        is_plural = len(dados['alunos']) > 1
        template = TEXTOS_PADRAO[tipo]["plural" if is_plural else "singular"]
        return template.format(nomes=nomes, ano_corrente=ano_atual, ano_anterior=ano_anterior)

    # Lógica Tipo 7 (Com Data)
    elif tipo == "7":
        nomes = formatar_lista_nomes(dados['alunos'])
        is_plural = len(dados['alunos']) > 1
        sub_opcao = dados['sub_opcao']
        data_registro = dados['data']  # Recebe a string formatada

        template = TEXTOS_PADRAO["7"][sub_opcao]["plural" if is_plural else "singular"]

        return template.format(nomes=nomes, data_registro=data_registro)

    elif tipo == "3":
        linhas = []
        for item in dados['detalhes']:
            linha = f"{item['nome'].upper()}"
            linha += f", {item['d1']}: {item['n1']} - {item['r1']}"
            if item['d2']:
                linha += f" / {item['d2']}: {item['n2']} - {item['r2']}"
            linhas.append(linha)
        return TEXTOS_PADRAO["3"].format(lista_alunos="\n".join(linhas))

    elif tipo == "4":
        linhas = []
        for item in dados['detalhes']:
            d_str = f"{item['d1']}"
            if item['d2']:
                d_str += f" e {item['d2']}"
            linhas.append(f"{item['nome'].upper()}, {d_str}")
        return TEXTOS_PADRAO["4"].format(lista_alunos="\n".join(linhas))

    elif tipo == "5":
        linhas = [
            f"{item['nome'].upper()} - Turma: {item['turma']}" for item in dados['detalhes']]
        return TEXTOS_PADRAO["5"].format(lista_alunos="\n".join(linhas))

    elif tipo == "6":
        linhas = [
            f"{item['nome'].upper()} - Turma: {item['turma']}" for item in dados['detalhes']]
        return TEXTOS_PADRAO["6"].format(lista_alunos="\n".join(linhas))


def criar_pdf(observacoes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    pdf.cell(0, 10, "Observações para ATA de Resultados Finais",
             ln=True, align='C')
    pdf.ln(10)

    for obs in observacoes:
        tipo, texto = obs[1], obs[2]
        pdf.set_font("Helvetica", 'B', size=10)

        titulo_obs = f"Observação (Tipo {tipo})"
        if tipo == "7":
            titulo_obs += " - Classificação/Reclassificação"

        pdf.cell(0, 6, f"{titulo_obs}:", ln=True)

        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 6, texto)
        pdf.ln(5)

        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    return pdf.output(dest='S')
