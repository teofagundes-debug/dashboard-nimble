import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

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
except Exception as e:
    st.error("Erro na conexão com o Banco de Dados. Verifique os Secrets.")
    st.stop()

# Captura o ID do cliente pela URL (?id=nome_do_cliente)
query_params = st.query_params
cliente_id = query_params.get("id")

if cliente_id:
    # SQL Dinâmico - Filtra os dados do cliente específico
    # Substitua 'metricas' pelo nome real da sua tabela no Supabase
    query = f"SELECT * FROM metricas WHERE cliente_id = '{cliente_id}' ORDER BY data DESC"
    
    try:
        df = pd.read_sql(query, engine)

        if not df.empty:
            st.subheader(f"Performance: {cliente_id.upper()}")
            
            # Linha de Métricas Principais (KPIs)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Enviadas", df['mensagens_enviadas'].sum())
            with c2:
                st.metric("Respostas", df['respostas'].sum())
            with c3:
                # Exemplo de cálculo de conversão
                conv = (df['respostas'].sum() / df['mensagens_enviadas'].sum()) * 100
                st.metric("Taxa de Conversão", f"{conv:.1f}%")

            # Gráfico de Evolução
            st.line_chart(data=df, x='data', y='respostas')
            
        else:
            st.info(f"Nenhum dado encontrado para o cliente: {cliente_id}")
            
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else:
    st.warning("⚠️ Aguardando parâmetro de identificação do projeto.")
