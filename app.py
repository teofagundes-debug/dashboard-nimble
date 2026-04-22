import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Configuração da página para o Iframe do Nimble
st.set_page_config(page_title="Dashboard Escala Vendas", layout="wide")

# Estilo para remover margens e deixar o dashboard limpo no iFrame
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
    """, unsafe_allow_html=True)

# Conexão Segura
try:
    db_url = st.secrets["DB_URL"]
    engine = create_engine(db_url)
except Exception:
    st.error("Erro na conexão com o Banco de Dados. Verifique os Secrets.")
    st.stop()

# Captura o ID do cliente pela URL (?id=nome_do_cliente)
query_params = st.query_params
cliente_id = query_params.get("id")

if cliente_id:
    query = text("""
        SELECT *
        FROM metricas
        WHERE cliente_id = :cliente_id
        ORDER BY data DESC
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"cliente_id": cliente_id})

        if not df.empty:
            st.subheader(f"Performance: {str(cliente_id).upper()}")

            c1, c2, c3 = st.columns(3)

            mensagens_enviadas = pd.to_numeric(df["mensagens_enviadas"], errors="coerce").fillna(0).sum()
            respostas = pd.to_numeric(df["respostas"], errors="coerce").fillna(0).sum()
            conv = (respostas / mensagens_enviadas * 100) if mensagens_enviadas > 0 else 0

            with c1:
                st.metric("Enviadas", int(mensagens_enviadas))
            with c2:
                st.metric("Respostas", int(respostas))
            with c3:
                st.metric("Taxa de Conversão", f"{conv:.1f}%")

            if "data" in df.columns and "respostas" in df.columns:
                df["data"] = pd.to_datetime(df["data"], errors="coerce")
                df = df.sort_values("data")
                st.line_chart(data=df, x="data", y="respostas")

        else:
            st.info(f"Nenhum dado encontrado para o cliente: {cliente_id}")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else:
    st.warning("⚠️ Aguardando parâmetro de identificação do projeto.")
