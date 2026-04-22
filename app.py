import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Dashboard Escala Vendas", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    </style>
""", unsafe_allow_html=True)

try:
    db_url = st.secrets["DB_URL"]
    engine = create_engine(db_url)
except Exception:
    st.error("Erro na conexão com o Banco de Dados. Verifique os Secrets.")
    st.stop()

query_params = st.query_params
cliente_slug = query_params.get("id")

if cliente_slug:
    query = text("""
        select
            c.nome as cliente_nome,
            c.slug as cliente_slug,
            m.data,
            m.mensagens_enviadas,
            m.respostas,
            m.projeto,
            m.campanha
        from metricas m
        inner join clientes c on c.id = m.cliente_id
        where c.slug = :cliente_slug
          and c.ativo = true
        order by m.data asc
    """)

    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"cliente_slug": cliente_slug})

        if not df.empty:
            nome_cliente = str(df["cliente_nome"].iloc[0])
            st.subheader(f"Performance: {nome_cliente}")

            df["mensagens_enviadas"] = pd.to_numeric(df["mensagens_enviadas"], errors="coerce").fillna(0)
            df["respostas"] = pd.to_numeric(df["respostas"], errors="coerce").fillna(0)
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df = df.sort_values("data")

            total_enviadas = int(df["mensagens_enviadas"].sum())
            total_respostas = int(df["respostas"].sum())
            taxa_conversao = (total_respostas / total_enviadas * 100) if total_enviadas > 0 else 0

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Enviadas", total_enviadas)
            with c2:
                st.metric("Respostas", total_respostas)
            with c3:
                st.metric("Taxa de Conversão", f"{taxa_conversao:.1f}%")

            grafico = df[["data", "respostas"]].dropna()
            if not grafico.empty:
                st.line_chart(data=grafico, x="data", y="respostas")

            st.dataframe(
                df[["data", "projeto", "campanha", "mensagens_enviadas", "respostas"]],
                use_container_width=True
            )

        else:
            st.info(f"Nenhum dado encontrado para o cliente: {cliente_slug}")

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else:
    st.warning("⚠️ Aguardando parâmetro de identificação do projeto.")
