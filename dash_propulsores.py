import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Eficiência de Parceiros", layout="wide")

# Estilos CSS (Visual Clean)
st.markdown("""
    <style>
    [data-testid="stMetricLabel"] { color: #0051CC !important; font-weight: bold !important; }
    [data-testid="stHeader"] { color: #0051CC !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; padding-top: 10px; }
    .stTabs [aria-selected="true"] { background-color: #0051CC; color: white; }
    div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    # Link direto de um logo transparente
    st.image("https://logospng.org/download/asaas/logo-asaas-4096.png", width=150)
with col_titulo:
    st.title("🚀 Eficiência de Parceiros")

st.markdown("---")

# --- PASSO 1: CARREGAR DADOS (MÉTODO CSV - SEM AUTENTICAÇÃO) ---
url_planilha_1 = "https://docs.google.com/spreadsheets/d/1VvVWTAlmvQSQXyfv4sfBiag2K6g1DqnEea5a8HgB_Y0/edit?usp=sharing"
url_planilha_2 = "https://docs.google.com/spreadsheets/d/1W64m1cA5WzyrzciDcXc0R28zVMnRrP7kK7sxrSiHAXE/edit?usp=sharing"

@st.cache_data(ttl=600)
def carregar_dados_online():
    try:
        # TRUQUE: Transforma o link de visualização em link de exportação CSV
        csv_url_1 = url_planilha_1.replace("/edit?usp=sharing", "/export?format=csv")
        csv_url_2 = url_planilha_2.replace("/edit?usp=sharing", "/export?format=csv")
        
        # Lê direto com o Pandas (Pula a autenticação complexa)
        df1 = pd.read_csv(csv_url_1)
        df2 = pd.read_csv(csv_url_2)
        
        tabela_final = pd.concat([df1, df2], ignore_index=True)
        tabela_final.columns = tabela_final.columns.str.strip()
        
        col_data = "Data Criação"
        if col_data in tabela_final.columns:
            tabela_final[col_data] = pd.to_datetime(tabela_final[col_data], dayfirst=True, errors='coerce')
            tabela_final["Filtro_Data"] = tabela_final[col_data].dt.date
        else:
            tabela_final["Filtro_Data"] = None
            
        return tabela_final
    except Exception as e:
        st.error(f"Erro ao ler planilhas. Verifique se estão compartilhadas como 'Qualquer pessoa com o link'. Detalhe: {e}")
        return None

tabela = carregar_dados_online()

if tabela is None:
    st.stop()

# --- PASSO 2: NOMES DAS COLUNAS ---
col_empresa = "Tempo de Análise"
col_documento = "Tipo de Documento"
col_parceiro = "ID Conta Principal"
col_status = "Análise"
col_divergencia = "Divergências"

# --- PASSO 3: FILTROS ---
st.sidebar.header("🔍 Filtros")

if "Filtro_Data" in tabela.columns:
    datas_reais = tabela["Filtro_Data"].dropna()
    if not datas_reais.empty:
        max_date = datas_reais.max()
        st.sidebar.info(f"📅 Dados até: **{max_date}**")

tabela_filtrada = tabela.copy()
datas_validas = tabela["Filtro_Data"].dropna()

if not datas_validas.empty:
    try:
        min_data = datas_validas.min()
        max_data = datas_validas.max()
        
        st.sidebar.subheader("Período")
        incluir_vazios = st.sidebar.checkbox("Incluir linhas com Data Vazia?", value=True)
        
        data_inicial, data_final = st.sidebar.date_input(
            "Selecione o intervalo",
            value=(min_data, max_data),
            min_value=min_data, max_value=max_data
        )
        
        if incluir_vazios:
            mask_data = (
                ((tabela_filtrada["Filtro_Data"] >= data_inicial) & (tabela_filtrada["Filtro_Data"] <= data_final)) | 
                (tabela_filtrada["Filtro_Data"].isna())
            )
        else:
            mask_data = (
                (tabela_filtrada["Filtro_Data"].notna()) &
                (tabela_filtrada["Filtro_Data"] >= data_inicial) & 
                (tabela_filtrada["Filtro_Data"] <= data_final)
            )
            
        tabela_filtrada = tabela_filtrada.loc[mask_data]
        
    except Exception as e:
        st.sidebar.warning(f"Erro no calendário: {e}")
else:
    st.sidebar.info("📅 Filtro de data indisponível.")

st.sidebar.subheader("Categorias")

# Filtros
if col_parceiro in tabela.columns:
    opcoes_parceiro = sorted(tabela[col_parceiro].dropna().astype(str).unique())
    parceiro_sel = st.sidebar.multiselect("Parceiro (ID)", options=opcoes_parceiro)
else:
    parceiro_sel = []

if col_documento in tabela.columns:
    opcoes_doc = sorted(tabela[col_documento].dropna().astype(str).unique())
    doc_sel = st.sidebar.multiselect("Tipo de Documento", options=opcoes_doc)
else:
    doc_sel = []

if col_divergencia in tabela.columns:
    raw_options = tabela[col_divergencia].dropna().astype(str).unique()
    ignorar_filtro = ["", "nan", "None", "Não informado", "None", "NaT", "<NA>"]
    opcoes_divergencia = sorted([x for x in raw_options if x not in ignorar_filtro])
    divergencia_sel = st.sidebar.multiselect("Tipo de Divergência", options=opcoes_divergencia)
else:
    divergencia_sel = []

# Aplica Filtros
if parceiro_sel:
    tabela_filtrada = tabela_filtrada[tabela_filtrada[col_parceiro].astype(str).isin(parceiro_sel)]

if doc_sel:
    tabela_filtrada = tabela_filtrada[tabela_filtrada[col_documento].isin(doc_sel)]

if divergencia_sel:
    tabela_filtrada = tabela_filtrada[tabela_filtrada[col_divergencia].astype(str).isin(divergencia_sel)]

st.sidebar.markdown("---")
csv = tabela_filtrada.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Baixar CSV", csv, "dados_filtrados.csv", "text/csv")

# --- PASSO 4: MÉTRICAS ---
total = tabela_filtrada.shape[0]
divergencias = 0
qtd_adulterado = 0
perc_adulterado = 0
assertividade = 0

if col_status in tabela.columns:
    divergencias = tabela_filtrada[~tabela_filtrada[col_status].isin(["Confere", "Aprovado"])].shape[0]
    if total > 0: assertividade = ((total - divergencias) / total) * 100

if col_divergencia in tabela.columns:
    qtd_adulterado = tabela_filtrada[tabela_filtrada[col_divergencia] == "Documento adulterado"].shape[0]
    if divergencias > 0: perc_adulterado = (qtd_adulterado / divergencias) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("📄 Total de Docs Analisados", total)
c2.metric("🎯 Assertividade", f"{assertividade:.1f}%")
c3.metric("❌ Divergências Gerais", divergencias)
c4.metric("🚨 Doc. Adulterados", qtd_adulterado, help=f"{perc_adulterado:.1f}% das divergências")

st.markdown("---")

# --- PASSO 5: TABELAS ---
st.subheader("📋 Resumo Analítico")

def criar_resumo(df, coluna, nome_index):
    if coluna not in df.columns: return pd.DataFrame()
    temp = df[coluna].dropna().astype(str)
    ignorar = ["", "nan", "None", "NaT", "<NA>", "Não informado", "None"]
    temp = temp[~temp.isin(ignorar)]
    
    resumo = temp.value_counts().reset_index()
    resumo.columns = [nome_index, "Qtd"]
    total_loc = resumo["Qtd"].sum()
    # CORREÇÃO: Multiplica por 100 para virar porcentagem de verdade (41.5 em vez de 0.4)
    resumo["%"] = (resumo["Qtd"] / total_loc * 100) if total_loc > 0 else 0
    return resumo

col_t1, col_t2 = st.columns(2)

with col_t1:
    st.write("**Volume por Tipo de Empresa**")
    if col_empresa in tabela_filtrada.columns:
        df_emp = criar_resumo(tabela_filtrada, col_empresa, "Tipo")
        # CORREÇÃO: max_value ajustado para 100
        st.dataframe(df_emp, column_config={"%": st.column_config.ProgressColumn("Share", format="%.1f%%", max_value=100)}, hide_index=True, use_container_width=True)

with col_t2:
    st.write("**Ranking de Divergências**")
    if col_divergencia in tabela_filtrada.columns:
        df_div = criar_resumo(tabela_filtrada, col_divergencia, "Motivo")
        # CORREÇÃO: max_value ajustado para 100
        st.dataframe(df_div, column_config={"%": st.column_config.ProgressColumn("Impacto", format="%.1f%%", max_value=100)}, hide_index=True, use_container_width=True)

st.markdown("---")

# --- PASSO 6: GRÁFICOS ---
st.subheader("📊 Visualização Gráfica")

st.write("**Evolução Diária**")
if "Filtro_Data" in tabela_filtrada.columns and col_status in tabela_filtrada.columns and not tabela_filtrada.empty:
    df_chart = tabela_filtrada.copy()
    df_chart = df_chart.dropna(subset=["Filtro_Data"]) 
    
    if not df_chart.empty:
        df_chart['Status_Simplificado'] = df_chart[col_status].apply(lambda x: 'Aprovado' if x in ['Confere', 'Aprovado'] else 'Divergência')
        df_grouped = df_chart.groupby(['Filtro_Data', 'Status_Simplificado']).size().reset_index(name='Quantidade')
        
        fig_evolucao = px.bar(
            df_grouped, x='Filtro_Data', y='Quantidade', color='Status_Simplificado',
            color_discrete_map={'Aprovado': '#0051CC', 'Divergência': '#FF4B4B'}, barmode='stack'
        )
        fig_evolucao.update_layout(xaxis_title="Data", yaxis_title="Docs", plot_bgcolor="white", height=350)
        st.plotly_chart(fig_evolucao, use_container_width=True)
    else:
        st.info("Sem dados com data válida para o gráfico.")

g1, g2 = st.columns(2)
with g1:
    st.write("**Distribuição Visual (Tipos)**")
    if col_empresa in tabela_filtrada.columns and not tabela_filtrada.empty:
        df_pizza = tabela_filtrada[col_empresa].value_counts().reset_index()
        df_pizza.columns = ['Tipo', 'Qtd']
        fig_pizza = px.pie(df_pizza, values='Qtd', names='Tipo', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig_pizza, use_container_width=True)

with g2:
    st.write("**Top Divergências (Passe o mouse para detalhes)**")
    if col_divergencia in tabela_filtrada.columns and not tabela_filtrada.empty:
        df_div_graph = tabela_filtrada[col_divergencia].fillna("").astype(str)
        ignorar_grafico = ["", "nan", "None", "Não informado", "None"]
        df_div_graph = df_div_graph[~df_div_graph.isin(ignorar_grafico)]
        
        df_counts = df_div_graph.value_counts().reset_index()
        df_counts.columns = ['Motivo', 'Qtd']
        
        df_top10 = df_counts.head(10).copy()
        total_divergencias = df_counts['Qtd'].sum()
        df_top10['Porcentagem'] = (df_top10['Qtd'] / total_divergencias * 100).round(1).astype(str) + '%'
        
        if not df_top10.empty:
            fig_barras = px.bar(
                df_top10, 
                x='Qtd', 
                y='Motivo', 
                orientation='h',
                color_discrete_sequence=['#FF4B4B'],
                custom_data=['Porcentagem'] 
            )
            
            fig_barras.update_traces(
                hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<br>Impacto: %{customdata[0]}<extra></extra>"
            )
            
            fig_barras.update_layout(
                yaxis={'categoryorder':'total ascending'}, 
                plot_bgcolor="white", 
                xaxis_title="Quantidade",
                height=450
            )
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.info("Nenhuma divergência encontrada.")

st.markdown("---")

# --- PASSO 7: BASE DETALHADA ---
with st.expander("📂 Abrir Base de Dados Detalhada"):
    def highlight_erros(row):
        val = row[col_status] if col_status in row else ''
        if val not in ["Confere", "Aprovado"]: return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)
    try:
        st.dataframe(tabela_filtrada.style.apply(highlight_erros, axis=1), use_container_width=True)
    except:
        st.dataframe(tabela_filtrada, use_container_width=True)
