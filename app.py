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

db_url = st.secrets["DB_URL"]
engine = create_engine(db_url)

cliente_slug = st.query_params.get("id")

if not cliente_slug:
    st.warning("⚠️ Aguardando parâmetro de identificação do projeto.")
    st.stop()

query = text("""
    select
        c.nome as cliente_nome,
        c.slug as cliente_slug,
        m.data,
        m.mensagens_enviadas,
        m.respostas,
        m.mensagens_recebidas,
        m.oportunidades_quentes,
        m.oportunidades_mornas,
        m.oportunidades_frias,
        m.vendas,
        m.faturamento,
        m.atendimentos_ia,
        m.atendimentos_humano,
        m.vendedor,
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
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

if df.empty:
    st.info(f"Nenhum dado encontrado para o cliente: {cliente_slug}")
    st.stop()

df["data"] = pd.to_datetime(df["data"], errors="coerce")

numeric_cols = [
    "mensagens_enviadas",
    "respostas",
    "mensagens_recebidas",
    "oportunidades_quentes",
    "oportunidades_mornas",
    "oportunidades_frias",
    "vendas",
    "faturamento",
    "atendimentos_ia",
    "atendimentos_humano",
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

nome_cliente = df["cliente_nome"].iloc[0]
st.subheader(f"Performance: {nome_cliente}")

# Filtros
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    data_inicio = st.date_input("Data inicial", value=df["data"].min().date())

with col_f2:
    data_fim = st.date_input("Data final", value=df["data"].max().date())

with col_f3:
    vendedores = sorted(df["vendedor"].dropna().unique().tolist())
    vendedor_sel = st.selectbox("Vendedor", ["Todos"] + vendedores)

df_filtrado = df[
    (df["data"].dt.date >= data_inicio) &
    (df["data"].dt.date <= data_fim)
]

if vendedor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["vendedor"] == vendedor_sel]

if df_filtrado.empty:
    st.info("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# Totais
mensagens_recebidas = int(df_filtrado["mensagens_recebidas"].sum())
mensagens_enviadas = int(df_filtrado["mensagens_enviadas"].sum())
respostas = int(df_filtrado["respostas"].sum())

quentes = int(df_filtrado["oportunidades_quentes"].sum())
mornas = int(df_filtrado["oportunidades_mornas"].sum())
frias = int(df_filtrado["oportunidades_frias"].sum())

vendas = int(df_filtrado["vendas"].sum())
faturamento = float(df_filtrado["faturamento"].sum())

atendimentos_ia = int(df_filtrado["atendimentos_ia"].sum())
atendimentos_humano = int(df_filtrado["atendimentos_humano"].sum())
total_atendimentos = atendimentos_ia + atendimentos_humano

taxa_resposta = (respostas / mensagens_recebidas * 100) if mensagens_recebidas > 0 else 0
percentual_ia = (atendimentos_ia / total_atendimentos * 100) if total_atendimentos > 0 else 0
percentual_humano = (atendimentos_humano / total_atendimentos * 100) if total_atendimentos > 0 else 0
ticket_medio = (faturamento / vendas) if vendas > 0 else 0

# KPIs
st.markdown("### Volume de atendimento")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Mensagens Recebidas", mensagens_recebidas)
c2.metric("Mensagens Enviadas", mensagens_enviadas)
c3.metric("Respostas", respostas)
c4.metric("Taxa de Resposta", f"{taxa_resposta:.1f}%")

st.markdown("### Performance da IA")
c5, c6, c7 = st.columns(3)
c5.metric("Atendimentos IA", atendimentos_ia)
c6.metric("Atendimentos Humano", atendimentos_humano)
c7.metric("% IA", f"{percentual_ia:.1f}%")

st.markdown("### Qualificação de oportunidades")
c8, c9, c10 = st.columns(3)
c8.metric("Quentes", quentes)
c9.metric("Mornas", mornas)
c10.metric("Frias", frias)

st.markdown("### Vendas")
c11, c12, c13 = st.columns(3)
c11.metric("Vendas", vendas)
c12.metric("Faturamento", f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c13.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

# Gráficos
st.markdown("### Evolução por período")
grafico = df_filtrado.copy()
grafico["data"] = grafico["data"].dt.date

grafico_diario = grafico.groupby("data", as_index=False)[
    ["mensagens_recebidas", "respostas", "vendas", "atendimentos_ia", "atendimentos_humano"]
].sum()

st.line_chart(grafico_diario, x="data", y=["mensagens_recebidas", "respostas", "vendas"])

st.markdown("### Atendimento IA x Humano")
st.bar_chart(grafico_diario, x="data", y=["atendimentos_ia", "atendimentos_humano"])

# Tabela
st.markdown("### Detalhamento")
st.dataframe(
    df_filtrado[[
        "data",
        "vendedor",
        "projeto",
        "campanha",
        "mensagens_recebidas",
        "respostas",
        "oportunidades_quentes",
        "oportunidades_mornas",
        "oportunidades_frias",
        "vendas",
        "faturamento",
        "atendimentos_ia",
        "atendimentos_humano"
    ]],
    use_container_width=True
)
