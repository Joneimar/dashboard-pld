"""Gráficos Plotly para o Dashboard de PLD."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.api import CORES_SUBMERCADO, SUBMERCADOS

_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13),
    margin=dict(l=50, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="#1e1e2e", font_size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def _apply(fig: go.Figure, **kw) -> go.Figure:
    fig.update_layout(**{**_LAYOUT, **kw})
    return fig


def serie_historica(pivot: pd.DataFrame) -> go.Figure:
    """Série temporal do PLD por submercado (linhas)."""
    fig = go.Figure()
    for sub in SUBMERCADOS:
        if sub not in pivot.columns:
            continue
        fig.add_trace(go.Scatter(
            x=pivot.index,
            y=pivot[sub],
            name=sub,
            mode="lines",
            line=dict(color=CORES_SUBMERCADO[sub], width=2),
            hovertemplate="<b>%{x|%b %Y}</b><br>PLD: R$ %{y:.2f}/MWh<extra>" + sub + "</extra>",
        ))

    return _apply(
        fig,
        title="Série Histórica do PLD Médio Mensal por Submercado",
        xaxis_title="",
        yaxis_title="PLD (R$/MWh)",
    )


def media_anual_barras(ma: pd.DataFrame) -> go.Figure:
    """Barras agrupadas com PLD médio anual por submercado."""
    fig = go.Figure()
    for sub in SUBMERCADOS:
        subset = ma[ma["submercado"] == sub]
        if subset.empty:
            continue
        fig.add_trace(go.Bar(
            x=subset["ano"].astype(str),
            y=subset["pld_medio"],
            name=sub,
            marker_color=CORES_SUBMERCADO[sub],
            hovertemplate="<b>%{x}</b><br>PLD médio: R$ %{y:.2f}/MWh<extra>" + sub + "</extra>",
        ))

    return _apply(
        fig,
        title="PLD Médio Anual por Submercado",
        xaxis_title="",
        yaxis_title="PLD (R$/MWh)",
        barmode="group",
    )


def boxplot_submercado(df: pd.DataFrame) -> go.Figure:
    """Boxplot do PLD por submercado para análise de dispersão."""
    fig = go.Figure()
    for sub in SUBMERCADOS:
        subset = df[df["submercado"] == sub]
        if subset.empty:
            continue
        fig.add_trace(go.Box(
            y=subset["pld"],
            name=sub,
            marker_color=CORES_SUBMERCADO[sub],
            boxmean="sd",
        ))

    return _apply(
        fig,
        title="Distribuição do PLD por Submercado",
        yaxis_title="PLD (R$/MWh)",
        showlegend=False,
    )


def heatmap_mensal(df: pd.DataFrame, submercado: str = "SUDESTE") -> go.Figure:
    """Heatmap ano x mês do PLD para um submercado."""
    sub_df = df[df["submercado"] == submercado]
    pivot = sub_df.pivot_table(index="ano", columns="mes", values="pld", aggfunc="first")
    pivot = pivot.reindex(columns=range(1, 13))

    labels_mes = [MESES_PT[m] for m in range(1, 13)]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=labels_mes,
        y=pivot.index.astype(str),
        colorscale="YlOrRd",
        colorbar=dict(title="R$/MWh"),
        hovertemplate="<b>%{y} — %{x}</b><br>PLD: R$ %{z:.2f}/MWh<extra></extra>",
    ))
    return _apply(
        fig,
        title=f"Mapa de Calor — PLD {submercado}",
        yaxis=dict(autorange="reversed"),
    )


def variacao_mensal(df: pd.DataFrame, submercado: str = "SUDESTE") -> go.Figure:
    """Variação percentual mês a mês do PLD."""
    sub_df = df[df["submercado"] == submercado].sort_values("data").copy()
    sub_df["var_pct"] = sub_df["pld"].pct_change() * 100

    cores = ["#22c55e" if v >= 0 else "#ef4444" for v in sub_df["var_pct"].fillna(0)]

    fig = go.Figure(go.Bar(
        x=sub_df["data"],
        y=sub_df["var_pct"],
        marker_color=cores,
        hovertemplate="<b>%{x|%b %Y}</b><br>Variação: %{y:.1f}%<extra></extra>",
    ))

    return _apply(
        fig,
        title=f"Variação Mensal do PLD — {submercado}",
        xaxis_title="",
        yaxis_title="Variação (%)",
    )


def spread_submercados(pivot: pd.DataFrame) -> go.Figure:
    """Spread (diferença) entre PLD máximo e mínimo entre submercados."""
    spread = pivot.max(axis=1) - pivot.min(axis=1)

    fig = go.Figure(go.Scatter(
        x=spread.index,
        y=spread.values,
        mode="lines",
        fill="tozeroy",
        line=dict(color="#8b5cf6", width=2),
        fillcolor="rgba(139, 92, 246, 0.15)",
        hovertemplate="<b>%{x|%b %Y}</b><br>Spread: R$ %{y:.2f}/MWh<extra></extra>",
    ))

    return _apply(
        fig,
        title="Spread entre Submercados (Máx − Mín)",
        xaxis_title="",
        yaxis_title="Spread (R$/MWh)",
    )
