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

# --- FUNÇÃO MÁGICA: ASPIRADOR DE DATAS ---
def encontrar_e_mesclar_datas(df):
    col_map = {}
    cols_de_data_encontradas = []
    
    for col in df.columns:
        clean_name = ''.join(c for c in unicodedata.normalize('NFD', col) if unicodedata.category(c) != 'Mn')
        clean_name = clean_name.lower().replace(" ", "").strip()
        
        if "nomeparceiro" in clean_name: col_map[col] = "Nome Parceiro"
        elif "tipodeempresa" in clean_name: col_map[col] = "Tipo de Empresa"
        elif "tipodedocumento" in clean_name: col_map[col] = "Tipo de Documento"
        elif "analise" == clean_name: col_map[col] = "Análise"
        elif "divergencias" in clean_name: col_map[col] = "Divergências"
        
        if "datacriacao" in clean_name:
            cols_de_data_encontradas.append(col)

    df = df.rename(columns=col_map)
    
    if cols_de_data_encontradas:
        df["Data_Final_Mestre"] = pd.NaT
        for col
