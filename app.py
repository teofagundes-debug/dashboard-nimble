import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

st.set_page_config(page_title="Dashboard Escala Vendas", layout="wide")

# Competência atual (MÊS ATUAL)
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
db_url = st.secrets["DB_URL"]
engine = create_engine(db_url)

cliente_slug = st.query_params.get("id")

if not cliente_slug:
    st.warning("⚠️ Aguardando parâmetro de identificação do projeto.")
    st.stop()


# QUERY (AGORA FILTRANDO POR MÊS)
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
    st.info(f"Nenhum dado encontrado para o mês atual.")
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

# Título com mês
mes_formatado = datetime.now().strftime("%B/%Y").capitalize()
st.title(f"{nome_cliente} — {mes_formatado}")


# TOTAIS DO MÊS
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
ticket_medio = (faturamento / vendas) if vendas else 0


# CARDS
st.markdown('<div class="section-title">Volume</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(card("Recebidas", mensagens_recebidas, "blue"))
c2.markdown(card("Enviadas", mensagens_enviadas, "blue"))
c3.markdown(card("Respostas", respostas, "green"))
c4.markdown(card("Taxa", f"{taxa_resposta:.1f}%", "green"))

st.markdown('<div class="section-title">IA</div>', unsafe_allow_html=True)
c5, c6, c7 = st.columns(3)
c5.markdown(card("IA", atendimentos_ia, "purple"))
c6.markdown(card("Humano", atendimentos_humano, "gray"))
c7.markdown(card("% IA", f"{percentual_ia:.1f}%", "purple"))

st.markdown('<div class="section-title">Oportunidades</div>', unsafe_allow_html=True)
c8, c9, c10 = st.columns(3)
c8.markdown(card("Quentes", quentes, "orange"))
c9.markdown(card("Mornas", mornas, "blue"))
c10.markdown(card("Frias", frias, "gray"))

st.markdown('<div class="section-title">Vendas</div>', unsafe_allow_html=True)
c11, c12, c13 = st.columns(3)
c11.markdown(card("Vendas", vendas, "green"))
c12.markdown(card("Faturamento", moeda(faturamento), "green"))
c13.markdown(card("Ticket", moeda(ticket_medio), "purple"))


# GRÁFICO
st.markdown('<div class="section-title">Evolução</div>', unsafe_allow_html=True)

grafico = df.copy()
grafico["Data"] = grafico["data"].dt.strftime("%d/%m/%Y")

grafico = grafico.groupby("Data", as_index=False)[
    ["mensagens_recebidas", "respostas", "vendas"]
].sum()

st.line_chart(grafico.set_index("Data"))


# TABELA
st.markdown('<div class="section-title">Detalhamento</div>', unsafe_allow_html=True)

tabela = df.copy()

tabela["data"] = tabela["data"].dt.strftime("%d/%m/%Y")
tabela["faturamento"] = tabela["faturamento"].apply(moeda)

st.dataframe(tabela, use_container_width=True)
