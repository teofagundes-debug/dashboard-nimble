import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

st.set_page_config(page_title="Dashboard Escala Vendas", layout="wide")

competencia_atual = datetime.now().strftime("%Y-%m")

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
    width: 100%;
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

.kpi-card.blue { background: linear-gradient(135deg, #1e3a8a, #2563eb); }
.kpi-card.green { background: linear-gradient(135deg, #064e3b, #047857); }
.kpi-card.orange { background: linear-gradient(135deg, #7c2d12, #ea580c); }
.kpi-card.purple { background: linear-gradient(135deg, #4c1d95, #7c3aed); }
.kpi-card.gray { background: linear-gradient(135deg, #374151, #111827); }

.kpi-title {
    font-size: 14px;
    color: #e5e7eb;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #ffffff;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #111827;
}

.insight-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 14px;
    padding: 14px 18px;
    color: #14532d;
    font-size: 15px;
    margin-top: 4px;
    margin-bottom: 12px;
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
    st.info("Nenhum dado encontrado para o mês atual.")
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
mes_formatado = datetime.now().strftime("%B/%Y").capitalize()

st.title(f"{nome_cliente} — {mes_formatado}")


# Totais
mensagens_recebidas = int(df["mensagens_recebidas"].sum())
mensagens_enviadas = int(df["mensagens_enviadas"].sum())
respostas = int(df["respostas"].sum())

quentes = int(df["oportunidades_quentes"].sum())
mornas = int(df["oportunidades_mornas"].sum())
frias = int(df["oportunidades_frias"].sum())

vendas = int(df["vendas"].sum())
faturamento = float(df["faturamento"].sum())

atendimentos_ia = int(df["atendimentos_ia"].sum())
atendimentos_humano = int(df["atendimentos_humano"].sum())
total_atendimentos = atendimentos_ia + atendimentos_humano

taxa_resposta = (respostas / mensagens_recebidas * 100) if mensagens_recebidas else 0
percentual_ia = (atendimentos_ia / total_atendimentos * 100) if total_atendimentos else 0
percentual_humano = (atendimentos_humano / total_atendimentos * 100) if total_atendimentos else 0
ticket_medio = (faturamento / vendas) if vendas else 0

# Eficiência da IA
tempo_medio_atendimento_min = 4
minutos_economizados = atendimentos_ia * tempo_medio_atendimento_min
horas_economizadas = minutos_economizados / 60


# Cards - Volume
st.markdown('<div class="section-title">Volume de atendimento</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    card("Recebidas", mensagens_recebidas, "blue")
with c2:
    card("Enviadas", mensagens_enviadas, "blue")
with c3:
    card("Respostas", respostas, "green")
with c4:
    card("Taxa de Resposta", f"{taxa_resposta:.1f}%", "green")


# Cards - IA
st.markdown('<div class="section-title">Eficiência da IA</div>', unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)

with c5:
    card("Atendimentos IA", atendimentos_ia, "purple")
with c6:
    card("% Atendido por IA", f"{percentual_ia:.1f}%", "purple")
with c7:
    card("Horas Economizadas", f"{horas_economizadas:.1f}h", "green")
with c8:
    card("Atendimentos Humano", atendimentos_humano, "gray")

st.markdown(f"""
<div class="insight-box">
    A IA realizou <strong>{percentual_ia:.1f}%</strong> dos atendimentos no período,
    economizando aproximadamente <strong>{horas_economizadas:.1f} horas</strong>
    de trabalho humano, considerando uma média conservadora de
    <strong>{tempo_medio_atendimento_min} minutos</strong> por atendimento.
</div>
""", unsafe_allow_html=True)


# Cards - Oportunidades
st.markdown('<div class="section-title">Qualificação de oportunidades</div>', unsafe_allow_html=True)

c9, c10, c11 = st.columns(3)

with c9:
    card("Quentes", quentes, "orange")
with c10:
    card("Mornas", mornas, "blue")
with c11:
    card("Frias", frias, "gray")


# Cards - Vendas
st.markdown('<div class="section-title">Vendas</div>', unsafe_allow_html=True)

c12, c13, c14 = st.columns(3)

with c12:
    card("Vendas", vendas, "green")
with c13:
    card("Faturamento", moeda(faturamento), "green")
with c14:
    card("Ticket Médio", moeda(ticket_medio), "purple")


# Gráfico - Evolução
st.markdown('<div class="section-title">Evolução do mês</div>', unsafe_allow_html=True)

grafico = df.copy()
grafico["data_ordem"] = pd.to_datetime(grafico["data"], errors="coerce").dt.date

grafico_diario = grafico.groupby("data_ordem", as_index=False)[
    ["mensagens_recebidas", "respostas", "vendas"]
].sum()

grafico_diario = grafico_diario.sort_values("data_ordem")
grafico_diario["Data"] = pd.to_datetime(grafico_diario["data_ordem"]).dt.strftime("%d/%m/%Y")

grafico_diario = grafico_diario.rename(columns={
    "mensagens_recebidas": "Mensagens Recebidas",
    "respostas": "Respostas",
    "vendas": "Vendas"
})

st.line_chart(
    grafico_diario,
    x="Data",
    y=["Mensagens Recebidas", "Respostas", "Vendas"]
)


# Gráfico - IA x Humano
st.markdown('<div class="section-title">Atendimento IA x Humano</div>', unsafe_allow_html=True)

grafico_ia = df.copy()
grafico_ia["data_ordem"] = pd.to_datetime(grafico_ia["data"], errors="coerce").dt.date

grafico_ia = grafico_ia.groupby("data_ordem", as_index=False)[
    ["atendimentos_ia", "atendimentos_humano"]
].sum()

grafico_ia = grafico_ia.sort_values("data_ordem")
grafico_ia["Data"] = pd.to_datetime(grafico_ia["data_ordem"]).dt.strftime("%d/%m/%Y")

grafico_ia = grafico_ia.rename(columns={
    "atendimentos_ia": "Atendimentos IA",
    "atendimentos_humano": "Atendimentos Humano"
})

st.bar_chart(
    grafico_ia,
    x="Data",
    y=["Atendimentos IA", "Atendimentos Humano"]
)


# Tabela
st.markdown('<div class="section-title">Detalhamento</div>', unsafe_allow_html=True)

tabela = df[[
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
