import streamlit as st
import pandas as pd
import plotly.express as px
import hmac
from datetime import date
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Eficiência de Parceiros", layout="wide")

# --- BLOCO DE AUTENTICAÇÃO ---
def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["passwords"]["acesso_diretoria"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("### 🔒 Acesso Restrito - Diretoria")
    st.text_input("Digite a senha de acesso:", type="password", on_change=password_entered, key="password")
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta")
    return False

if not check_password():
    st.stop()

# Estilos CSS
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
    try:
        st.image("logo_asaas.png", width=150)
    except:
        st.write("💙 Asaas")
with col_titulo:
    st.title("🚀 Eficiência de Parceiros")

st.markdown("---")

# --- FUNÇÃO: A "PENEIRA" DE COLUNAS ---
def padronizar_planilha(df):
    """Filtra, renomeia e mantém apenas as colunas essenciais antes de juntar as planilhas."""
    mapa_colunas = {}
    
    for col in df.columns:
        s = str(col)
        normalized = unicodedata.normalize('NFD', s)
        clean_name = "".join([c for c in normalized if unicodedata.category(c) != 'Mn'])
        clean_name = clean_name.lower().replace(" ", "").strip()
        
        if "semana" in clean_name: mapa_colunas[col] = "Semana"
        elif "analista" in clean_name: mapa_colunas[col] = "Analista"
        elif "link" in clean_name: mapa_colunas[col] = "Link Análise"
        elif clean_name == "analise": mapa_colunas[col] = "Análise"
        elif "tipodedocumento" in clean_name
