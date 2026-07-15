"""Dashboard — PLD · Preço de Liquidação das Diferenças.

Dados consumidos em tempo real da API de Dados Abertos da CCEE.
Desenvolvido por Joneimar Lemos · energycode.com.br
"""

import streamlit as st

st.set_page_config(
    page_title="PLD — Preço de Liquidação das Diferenças",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd

from src.api import (
    CORES_SUBMERCADO,
    SUBMERCADOS,
    estatisticas_por_submercado,
    fetch_pld,
    media_anual,
    pld_atual,
    pld_pivot_submercado,
)
from src.charts import (
    boxplot_submercado,
    heatmap_mensal,
    media_anual_barras,
    serie_historica,
    spread_submercados,
    variacao_mensal,
)

# ── Estilo ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0f0f13; }
    [data-testid="stSidebar"] { background-color: #141418; }
    .kpi-card {
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #2a2a32;
        background: linear-gradient(135deg, #18181c 0%, #141418 100%);
        text-align: center;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #a1a1aa;
        margin-top: 0.25rem;
    }
    .info-box {
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid #2a2a32;
        background: #18181c;
        font-size: 0.9rem;
        color: #d4d4d8;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def load_data() -> pd.DataFrame:
    return fetch_pld()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 PLD — Dashboard")
    st.caption("Dados: [CCEE — Dados Abertos](https://dadosabertos.ccee.org.br/)")

    st.markdown("---")

    st.markdown("""
    <div class="info-box">
        <strong>O que é o PLD?</strong><br><br>
        O Preço de Liquidação das Diferenças (PLD) é o preço spot
        da energia elétrica no Brasil. Calculado diariamente pela CCEE
        com base no Custo Marginal de Operação (CMO), ele reflete o
        custo de produzir mais uma unidade de energia no sistema.<br><br>
        O PLD é o principal indicador do mercado de curto prazo e
        impacta diretamente as operações de <strong>trading</strong>,
        contratos bilaterais e a receita de geradores.<br><br>
        <strong>Submercados:</strong> Sudeste/CO, Sul, Nordeste e Norte.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "Desenvolvido por [Joneimar Lemos](https://energycode.com.br)  \n"
        "Dados atualizados via CCEE"
    )


# ── Dados ────────────────────────────────────────────────────────────────────
with st.spinner("Buscando dados de PLD na CCEE..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Não foi possível carregar os dados da CCEE: {e}")
        st.stop()

pivot = pld_pivot_submercado(df)
atual = pld_atual(df)
data_ref = df["data"].max()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Dashboard — PLD · Preço de Liquidação das Diferenças")
st.markdown(
    "Análise do Preço de Liquidação das Diferenças (PLD) do mercado de energia elétrica brasileiro, "
    "com dados consolidados por submercado desde 2001. Fonte: Dados Abertos da CCEE."
)
st.markdown("---")

# ── KPIs: PLD atual por submercado ───────────────────────────────────────────
cols = st.columns(4)
for i, sub in enumerate(SUBMERCADOS):
    row = atual[atual["submercado"] == sub]
    if row.empty:
        continue
    pld_val = row.iloc[0]["pld"]
    cor = CORES_SUBMERCADO[sub]
    with cols[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{sub}</div>
            <div class="kpi-value" style="color:{cor}">R$ {pld_val:.2f}</div>
            <div class="kpi-sub">R$/MWh — {data_ref.strftime('%b/%Y')}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── Filtros ──────────────────────────────────────────────────────────────────
with st.expander("🔍 Filtros", expanded=False):
    f1, f2 = st.columns(2)
    anos = sorted(df["ano"].unique())
    ano_min, ano_max = int(anos[0]), int(anos[-1])
    with f1:
        sel_anos = st.slider("Período", ano_min, ano_max, (ano_min, ano_max))
    with f2:
        sel_sub = st.multiselect("Submercados", SUBMERCADOS, default=SUBMERCADOS)

    df_f = df[(df["ano"] >= sel_anos[0]) & (df["ano"] <= sel_anos[1]) & (df["submercado"].isin(sel_sub))]
    pivot_f = pld_pivot_submercado(df_f)
    st.caption(f"{len(df_f)} registros no período {sel_anos[0]}–{sel_anos[1]}")

# ── Série histórica ─────────────────────────────────────────────────────────
st.plotly_chart(serie_historica(pivot_f), use_container_width=True)

# ── Spread + Boxplot ─────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(spread_submercados(pivot_f), use_container_width=True)
with c2:
    st.plotly_chart(boxplot_submercado(df_f), use_container_width=True)

# ── Média anual ──────────────────────────────────────────────────────────────
st.plotly_chart(media_anual_barras(media_anual(df_f)), use_container_width=True)

# ── Heatmap e variação por submercado ────────────────────────────────────────
st.markdown("### Análise por Submercado")
tab_sub = st.selectbox("Selecione o submercado", SUBMERCADOS, index=0)

h1, h2 = st.columns(2)
with h1:
    st.plotly_chart(heatmap_mensal(df_f, tab_sub), use_container_width=True)
with h2:
    st.plotly_chart(variacao_mensal(df_f, tab_sub), use_container_width=True)

# ── Estatísticas ─────────────────────────────────────────────────────────────
with st.expander("📈 Estatísticas descritivas por submercado", expanded=False):
    stats = estatisticas_por_submercado(df_f)
    stats.columns = ["Submercado", "Média (R$/MWh)", "Mediana", "Desvio Padrão", "Mínimo", "Máximo"]
    st.dataframe(stats, use_container_width=True, hide_index=True)

# ── Tabela ───────────────────────────────────────────────────────────────────
with st.expander("📋 Dados completos", expanded=False):
    st.dataframe(
        df_f[["data", "submercado", "pld"]]
        .rename(columns={"data": "Data", "submercado": "Submercado", "pld": "PLD (R$/MWh)"})
        .sort_values("Data", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

# ── Seção metodológica ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### Sobre os Dados e a Metodologia")

st.markdown("""
**Fonte:** [Dados Abertos da CCEE](https://dadosabertos.ccee.org.br/dataset/pld_media_mensal)
— PLD Médio Mensal por submercado.

**Pipeline de dados:**
1. Scraping das URLs de download no portal CKAN da CCEE (7 recursos: 2001–2020 consolidado + 2021–2026 anuais).
2. Download paralelo dos CSVs (separador `;`, encoding `latin-1`).
3. Consolidação, tipagem e enriquecimento temporal (`MES_REFERENCIA` → datetime).
4. Cache de 1h via `st.cache_data`.

**Sobre o PLD:**

O Preço de Liquidação das Diferenças (PLD) é o preço da energia no mercado de curto prazo
do SIN (Sistema Interligado Nacional). Ele é calculado diariamente pela CCEE com base no
Custo Marginal de Operação (CMO), determinado pelos modelos computacionais NEWAVE e DECOMP.

| Conceito | Descrição |
|---|---|
| **CMO** | Custo Marginal de Operação — base de cálculo do PLD |
| **Submercados** | SE/CO, S, NE e N — refletem restrições de transmissão |
| **Piso / Teto** | Limites regulatórios que contêm o PLD |
| **Spread** | Diferença de PLD entre submercados — oportunidade de arbitragem |
| **Sazonalidade** | Período úmido (nov–mar) tende a ter PLD mais baixo; seco (mai–set) mais alto |

**Contexto regulatório:** O PLD horário foi instituído a partir de janeiro de 2021
(Resolução ANEEL nº 2.927/2020), substituindo o PLD semanal. Este dashboard utiliza
a série de médias mensais para manter a comparabilidade com dados históricos.
""")

st.markdown("---")
st.caption("📊 Dashboard de PLD · Desenvolvido por Joneimar Lemos · energycode.com.br")
