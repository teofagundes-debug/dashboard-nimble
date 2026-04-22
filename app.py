import streamlit as st
from sqlalchemy.engine import make_url

st.title("Diagnóstico da conexão")

try:
    db_url = st.secrets["DB_URL"]
    parsed = make_url(db_url)

    st.write("Usuário lido:", parsed.username)
    st.write("Host lido:", parsed.host)
    st.write("Porta lida:", parsed.port)
    st.write("Banco lido:", parsed.database)

except Exception as e:
    st.error(f"Erro ao ler a URL: {e}")
