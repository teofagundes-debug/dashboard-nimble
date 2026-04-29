import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Dashboard Escala Vendas", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.kpi-card {
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.10);
    margin-bottom: 12px;
    min-height: 105px;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;

    transition: transform 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
}

.kpi-card.blue {
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
}

.kpi-card.green {
    background: linear-gradient(135deg, #064e3b, #047857);
}

.kpi-card.orange {
    background: linear-gradient(135deg, #7c2d12, #ea580c);
}

.kpi-card.purple {
    background: linear-gradient(135deg, #4c1d95, #7c3aed);
}

.kpi-card.gray {
    background: linear-gradient(135deg, #374151, #111827);
}

.kpi-title {
    font-size: 14px;
    color: #e5e7eb;
    margin-bottom: 6px;
    text-align: center;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)


def card(title, value, color="blue"):
    st.markdown(f"""
    <div class="kpi-card {color}">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Conexão
try:
    db_url = st.secrets["DB_URL"]
    engine = create_engine(db_url)
except Exception:
    st.error("Erro na conexão com o Banco de Dados. Verifique os Secrets.")
    st.stop()


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
      and m.competencia = :competencia_atual
    order by m.data asc
""")


try:
    with engine.connect() as conn:
        df = pd.read_sql(
    query,
    conn,
    params={
        "cliente_slug": cliente_slug,
        "competencia_atual": competencia_atual
    }
)
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
from datetime import datetime

competencia_atual = datetime.now().strftime("%Y-%m")

nome_cliente = df["cliente_nome"].iloc[0]

st.title(f"Dashboard - {nome_cliente}")


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


# Cards
st.markdown('<div class="section-title">Volume de atendimento</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    card("Mensagens Recebidas", mensagens_recebidas, "blue")
with c2:
    card("Mensagens Enviadas", mensagens_enviadas, "blue")
with c3:
    card("Respostas", respostas, "green")
with c4:
    card("Taxa de Resposta", f"{taxa_resposta:.1f}%", "green")


st.markdown('<div class="section-title">Performance da IA</div>', unsafe_allow_html=True)
c5, c6, c7, c8 = st.columns(4)

with c5:
    card("Atendimentos IA", atendimentos_ia, "purple")
with c6:
    card("Atendimentos Humano", atendimentos_humano, "gray")
with c7:
    card("% IA", f"{percentual_ia:.1f}%", "purple")
with c8:
    card("% Humano", f"{percentual_humano:.1f}%", "gray")


st.markdown('<div class="section-title">Qualificação de oportunidades</div>', unsafe_allow_html=True)
c9, c10, c11 = st.columns(3)

with c9:
    card("Quentes", quentes, "orange")
with c10:
    card("Mornas", mornas, "blue")
with c11:
    card("Frias", frias, "gray")


st.markdown('<div class="section-title">Vendas</div>', unsafe_allow_html=True)
c12, c13, c14 = st.columns(3)

with c12:
    card("Vendas", vendas, "green")
with c13:
    card("Faturamento", moeda(faturamento), "green")
with c14:
    card("Ticket Médio", moeda(ticket_medio), "purple")


# Gráficos
st.markdown('<div class="section-title">Evolução por período</div>', unsafe_allow_html=True)

grafico = df_filtrado.copy()

# Mantém a data real para ordenação correta
grafico["data_ordem"] = pd.to_datetime(grafico["data"], errors="coerce").dt.date

grafico_diario = grafico.groupby("data_ordem", as_index=False)[
    [
        "mensagens_recebidas",
        "respostas",
        "vendas",
        "atendimentos_ia",
        "atendimentos_humano"
    ]
].sum()

# Ordena pela data real
grafico_diario = grafico_diario.sort_values("data_ordem")

# Cria a data formatada em português apenas para exibição
grafico_diario["Data"] = pd.to_datetime(grafico_diario["data_ordem"]).dt.strftime("%d/%m/%Y")

grafico_diario = grafico_diario.rename(columns={
    "mensagens_recebidas": "Mensagens Recebidas",
    "respostas": "Respostas",
    "vendas": "Vendas",
    "atendimentos_ia": "Atendimentos IA",
    "atendimentos_humano": "Atendimentos Humano"
})
st.line_chart(
    grafico_diario,
    x="Data",
    y=["Mensagens Recebidas", "Respostas", "Vendas"]
)


st.markdown('<div class="section-title">Atendimento IA x Humano</div>', unsafe_allow_html=True)

st.bar_chart(
    grafico_diario,
    x="Data",
    y=["Atendimentos IA", "Atendimentos Humano"]
)


# Tabela
st.markdown('<div class="section-title">Detalhamento</div>', unsafe_allow_html=True)

tabela = df_filtrado[[
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
]].copy()

tabela = tabela.rename(columns={
    "data": "Data",
    "vendedor": "Vendedor",
    "projeto": "Projeto",
    "campanha": "Campanha",
    "mensagens_recebidas": "Mensagens Recebidas",
    "respostas": "Respostas",
    "oportunidades_quentes": "Oportunidades Quentes",
    "oportunidades_mornas": "Oportunidades Mornas",
    "oportunidades_frias": "Oportunidades Frias",
    "vendas": "Vendas",
    "faturamento": "Faturamento",
    "atendimentos_ia": "Atendimentos IA",
    "atendimentos_humano": "Atendimentos Humano"
})

tabela["Data"] = pd.to_datetime(tabela["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
tabela["Faturamento"] = tabela["Faturamento"].apply(moeda)

st.dataframe(tabela, use_container_width=True)
