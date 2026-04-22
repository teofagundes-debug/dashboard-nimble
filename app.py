import streamlit as st
from sqlalchemy import create_engine, text

st.title("Teste de conexão com banco")

try:
    db_url = st.secrets["DB_URL"]
    engine = create_engine(db_url)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        st.success("Conectado com sucesso!")

except Exception as e:
    st.error(f"Erro ao conectar: {e}")
