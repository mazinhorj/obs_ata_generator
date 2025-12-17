import streamlit as st
import pandas as pd
import time
import db
import utils
import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ATAS - Observações",
    page_icon="🏫",
    layout="wide"
)

# --- CARREGAR CSS ---


def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(
            f"Arquivo {file_name} não encontrado. O estilo padrão será usado.")


local_css("style.css")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
if 'db_initialized' not in st.session_state:
    db.init_db()
    st.session_state['db_initialized'] = True

# --- CABEÇALHO ---
st.title("🏫 ATAS de Resultados Finais - Gerador de Observações")
st.markdown("### Rede Municipal de Duque de Caxias")

# --- FUNÇÕES AUXILIARES ---


def is_turma_elegivel_pp(turma_str):
    if turma_str is None:
        return False
    try:
        valor = int(turma_str)
        return 601 <= valor <= 999
    except (ValueError, TypeError):
        return False


# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("📂 Dados e Configurações")
    uploaded_file = st.file_uploader(
        "Carregar 'Livro de matrícula' (XLSX)", type=["xlsx"])

    st.info("Carregue o arquivo 'Livro de matrícula.xlsx' exportado do e-duque.")

    st.markdown("---")

    if st.button("🗑️ Limpar todas as observações", type="secondary"):
        db.clear_db()
        if 'preview_texto' in st.session_state:
            del st.session_state['preview_texto']
        msg = st.success("Histórico limpo com sucesso!")
        time.sleep(1.2)
        msg.empty()
        st.rerun()

# --- LÓGICA PRINCIPAL ---
df = None

if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file, header=8)

        if df_raw.shape[1] >= 7:
            df = df_raw.iloc[:, [4, 6]].copy()
            df.columns = ['turma', 'nome']

            df = df.dropna(subset=['nome', 'turma'])
            df['turma'] = df['turma'].astype(
                str).str.replace(r'\.0$', '', regex=True)
            df['nome'] = df['nome'].astype(str).str.strip().str.upper()

            df = df[df['turma'].str.lower() != 'nan']
            df = df[df['nome'].str.lower() != 'nan']
        else:
            st.error("❌ O arquivo enviado não possui o número mínimo de colunas.")
            df = None

    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")

if df is not None:
    if df.empty:
        st.warning(
            "⚠️ O arquivo foi carregado, mas não foram encontrados dados válidos.")
    else:
        # --- SELEÇÃO ---
        col_sel_1, col_sel_2 = st.columns(2)
        turmas_disponiveis = sorted(df['turma'].unique())

        if not turmas_disponiveis:
            st.error("Não foram encontradas turmas válidas no arquivo.")
            st.stop()

        turma_sel = col_sel_1.selectbox(
            "Selecione a Turma:", turmas_disponiveis)
        alunos_da_turma = df[df['turma'] ==
                             turma_sel]['nome'].sort_values().tolist()
        alunos_sel = col_sel_2.multiselect(
            "Selecione o(s) Aluno(s):", alunos_da_turma)

        st.divider()

        # --- OPÇÕES ---
        textos_base = {
            "1": "Retido freq. ano anterior -> Reclassificado",
            "2": "Retido freq. ano atual -> Reclassificar",
            "3": "Cumpriu PP (Notas)",
            "4": "Promovido com PP (Disciplinas)",
            "5": "Alunos AEE",
            "6": "Turmas Regular (para AEE)",
            "7": "Classificados ou Reclassificados"
        }

        permite_pp = is_turma_elegivel_pp(turma_sel)

        if permite_pp:
            chaves_disponiveis = ["1", "2", "3", "4", "5", "6", "7"]
        else:
            chaves_disponiveis = ["1", "2", "5", "6", "7"]

        def formatar_opcao(chave):
            numero_visual = chaves_disponiveis.index(chave) + 1
            texto = textos_base[chave]
            return f"{numero_visual}. {texto}"

        tipo_selecionado = st.selectbox(
            "Selecione o Tipo de Observação:",
            chaves_disponiveis,
            format_func=formatar_opcao
        )

        # --- INPUTS ---
        disciplinas_padrao = ["Língua Portuguesa", "Matemática", "Ciências", "História", "Geografia", "Língua Inglesa", "Arte", "Educação Física"]
        dados_para_gerar = {}

        if not alunos_sel:
            st.warning(
                "Selecione pelo menos um aluno acima para preencher os dados.")
        else:
            if tipo_selecionado in ["1", "2"]:
                dados_para_gerar = {'alunos': alunos_sel}

            # --- TIPO 7 COM DATA ---
            elif tipo_selecionado == "7":
                st.subheader("📋 Detalhes da Classificação/Reclassificação")

                sub_opcoes = {
                    "1": "1. Sem comprovação de vida escolar",
                    "2": "2. Matrícula por transferência (Reclassificação)",
                    "3": "3. Transferência de países estrangeiros",
                    "4": "4. Alunos com PP enviados para EJA"
                }

                c1, c2 = st.columns([2, 1])
                sub_sel = c1.selectbox(
                    "Selecione o motivo:",
                    list(sub_opcoes.keys()),
                    format_func=lambda x: sub_opcoes[x]
                )

                data_input = c2.date_input(
                    "Data do Registro:", format="DD/MM/YYYY")
                # Formata para texto brasileiro
                data_str = data_input.strftime("%d/%m/%Y")

                dados_para_gerar = {
                    'alunos': alunos_sel,
                    'sub_opcao': sub_sel,
                    'data': data_str
                }

            elif tipo_selecionado == "3":
                st.subheader("📝 Lançamento de Notas de PP")
                detalhes = []
                for aluno in alunos_sel:
                    with st.expander(f"Notas para: {aluno}", expanded=True):
                        c1, c2, c3 = st.columns([3, 2, 2])
                        d1 = c1.selectbox(
                            f"Disciplina 1", disciplinas_padrao, key=f"d1_{aluno}")
                        n1 = c2.number_input(
                            f"Nota 1", 0.0, 10.0, step=0.1, key=f"n1_{aluno}")
                        r1 = "PROMOVIDO" if n1 >= 6.0 else "RETIDO"
                        c3.markdown(
                            f"<br>Resultado: **{r1}**", unsafe_allow_html=True)

                        tem_d2 = st.checkbox(
                            f"Adicionar 2ª disciplina?", key=f"chk_{aluno}")
                        d2, n2, r2 = None, None, None
                        if tem_d2:
                            c1b, c2b, c3b = st.columns([3, 2, 2])
                            opcoes_d2 = [
                                disc for disc in disciplinas_padrao if disc != d1]
                            d2 = c1b.selectbox(
                                f"Disciplina 2", opcoes_d2, key=f"d2_{aluno}")
                            n2 = c2b.number_input(
                                f"Nota 2", 0.0, 10.0, step=0.1, key=f"n2_{aluno}")
                            r2 = "PROMOVIDO" if n2 >= 6.0 else "RETIDO"
                            c3b.markdown(
                                f"<br>Resultado: **{r2}**", unsafe_allow_html=True)

                        detalhes.append({
                            'nome': aluno,
                            'd1': d1, 'n1': f"{n1:.1f}".replace('.', ','), 'r1': r1,
                            'd2': d2, 'n2': f"{n2:.1f}".replace('.', ',') if n2 is not None else "", 'r2': r2 if r2 else ""
                        })
                dados_para_gerar = {'detalhes': detalhes}

            elif tipo_selecionado == "4":
                st.subheader("📚 Indicação de Disciplinas PP")
                detalhes = []
                for aluno in alunos_sel:
                    with st.expander(f"Disciplinas para: {aluno}", expanded=True):
                        d1 = st.selectbox(
                            f"Disciplina 1", disciplinas_padrao, key=f"t4_d1_{aluno}")
                        tem_d2 = st.checkbox(
                            "2ª Disciplina?", key=f"t4_chk_{aluno}")
                        d2 = None
                        if tem_d2:
                            opcoes_d2 = [
                                disc for disc in disciplinas_padrao if disc != d1]
                            d2 = st.selectbox(
                                f"Disciplina 2", opcoes_d2, key=f"t4_d2_{aluno}")
                        detalhes.append({'nome': aluno, 'd1': d1, 'd2': d2})
                dados_para_gerar = {'detalhes': detalhes}

            elif tipo_selecionado in ["5", "6"]:
                st.subheader("🏫 Informar Turma Referência")
                detalhes = []
                for aluno in alunos_sel:
                    t_input = st.text_input(
                        f"Turma para {aluno}:", key=f"turma_{aluno}")
                    detalhes.append({'nome': aluno, 'turma': t_input})
                dados_para_gerar = {'detalhes': detalhes}

            # --- PREVIEW E SALVAR ---
            if st.button("👁️ Pré-visualizar Observação", type="primary"):
                texto_gerado = utils.gerar_texto_observacao(
                    tipo_selecionado, dados_para_gerar)
                st.session_state['preview_texto'] = texto_gerado

        if 'preview_texto' in st.session_state:
            st.markdown("### ✏️ Editar Texto Final")
            st.markdown(
                "_Verifique se o texto está correto antes de adicionar à lista._")
            texto_final = st.text_area(
                "Edite aqui:", value=st.session_state['preview_texto'], height=150)

            col_act_1, col_act_2 = st.columns([1, 5])
            if col_act_1.button("💾 Salvar"):
                db.add_observacao(tipo_selecionado, texto_final)
                st.success("Observação adicionada à fila!")
                del st.session_state['preview_texto']
                time.sleep(1)
                st.rerun()

# --- FILA E RODAPÉ ---
st.divider()
st.header("📄 Fila de Impressão (Observações Geradas)")

obs_list = db.get_observacoes()

if obs_list:
    for obs in obs_list:
        with st.container(border=True):
            col_a, col_b = st.columns([6, 1])
            col_a.markdown(f"**Tipo {obs[1]}**")
            col_a.text(obs[2])
            if col_b.button("❌ Remover", key=f"del_{obs[0]}"):
                db.delete_observacao(obs[0])
                st.rerun()

    st.markdown("###")
    if st.button("🖨️ Baixar PDF com todas as observações", type="primary", use_container_width=True):
        pdf_bytes = utils.criar_pdf(obs_list)
        st.download_button(
            label="📥 Clique aqui para baixar o PDF",
            data=bytes(pdf_bytes),
            file_name="atas_observacoes.pdf",
            mime="application/pdf"
        )
else:
    if df is None:
        st.info("Aguardando carregamento do arquivo XLSX...")
    else:
        st.info(
            "Nenhuma observação gerada ainda.")

st.markdown(
    """
    <div class='content-footer'>
        Desenvolvido por <b>MazinhoBigDaddy</b> - 2025
    </div>
    """,
    unsafe_allow_html=True
)
