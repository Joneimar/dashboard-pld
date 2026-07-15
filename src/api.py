"""Pipeline ETL — PLD Médio Mensal via Dados Abertos da CCEE.

Realiza scraping das URLs de download dos CSVs no portal CKAN da CCEE,
baixa e consolida todos os anos em um único DataFrame.
"""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_LOCAL_CSV = _DATA_DIR / "pld_historico.csv"

_DATASET_URL = "https://dadosabertos.ccee.org.br/dataset/pld_media_mensal"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://dadosabertos.ccee.org.br/",
}


def _get_session() -> requests.Session:
    """Cria sessão HTTP com cookies do portal (bypassa WAF)."""
    s = requests.Session()
    s.headers.update(_HEADERS)
    try:
        s.get(_DATASET_URL, timeout=15)
    except requests.RequestException:
        pass
    return s

_FALLBACK_URLS: dict[str, str] = {
    "pld_media_mensal_2001_2020": "https://pda-download.ccee.org.br/f0XoqvKpQGyTE_eXw1LJvw/content",
    "pld_media_mensal_2021": "https://pda-download.ccee.org.br/n84EY5RxSDuxbn3ijIEzog/content",
    "pld_media_mensal_2022": "https://pda-download.ccee.org.br/luZm_3f4QZawp493rQcUng/content",
    "pld_media_mensal_2023": "https://pda-download.ccee.org.br/FFP3SAqERlyCt8YYPRNoKA/content",
    "pld_media_mensal_2024": "https://pda-download.ccee.org.br/d27b5AyUSGmBvg8kv9roxw/content",
    "pld_media_mensal_2025": "https://pda-download.ccee.org.br/PAZD3cb-QK60HeSTuv5h8Q/content",
    "pld_media_mensal_2026": "https://pda-download.ccee.org.br/NMaqaxA6T-ujInbyFlyN3Q/content",
}

SUBMERCADOS = ["SUDESTE", "SUL", "NORDESTE", "NORTE"]

CORES_SUBMERCADO: dict[str, str] = {
    "SUDESTE": "#3b82f6",
    "SUL": "#22c55e",
    "NORDESTE": "#f59e0b",
    "NORTE": "#ef4444",
}


def _discover_download_urls(session: requests.Session) -> dict[str, str]:
    """Descobre URLs de download dos CSVs no portal da CCEE via scraping.

    Se o portal estiver indisponível ou bloqueado por WAF,
    usa URLs de fallback previamente mapeadas.
    """
    try:
        resp = session.get(_DATASET_URL, timeout=15)
        resp.raise_for_status()

        resource_ids = list(
            dict.fromkeys(
                re.findall(r"/dataset/pld_media_mensal/resource/([a-f0-9-]+)", resp.text)
            )
        )
        titles = re.findall(r'class="heading"[^>]*title="([^"]+)"', resp.text)

        urls: dict[str, str] = {}
        for i, rid in enumerate(resource_ids):
            resp_r = session.get(
                f"{_DATASET_URL}/resource/{rid}", timeout=15
            )
            download = re.findall(r'href="(https://pda-download[^"]+)"', resp_r.text)
            name = titles[i] if i < len(titles) else f"resource_{i}"
            if download:
                urls[name] = download[0]

        if urls:
            return urls
    except (requests.RequestException, IndexError):
        pass

    return _FALLBACK_URLS


def _parse_raw(raw: pd.DataFrame) -> pd.DataFrame:
    """Normaliza o DataFrame bruto da CCEE."""
    raw["data"] = pd.to_datetime(raw["MES_REFERENCIA"].astype(str), format="%Y%m")
    raw["submercado"] = raw["SUBMERCADO"].str.strip()
    raw["pld"] = raw["PLD_MEDIA_MES"].astype(float)
    raw["ano"] = raw["data"].dt.year
    raw["mes"] = raw["data"].dt.month
    return (
        raw[["data", "submercado", "pld", "ano", "mes"]]
        .sort_values(["data", "submercado"])
        .reset_index(drop=True)
    )


def _fetch_from_api() -> pd.DataFrame | None:
    """Tenta baixar dados frescos da CCEE. Retorna None se falhar."""
    try:
        session = _get_session()
        urls = _discover_download_urls(session)

        dfs: list[pd.DataFrame] = []
        for _name, url in urls.items():
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            df = pd.read_csv(StringIO(resp.text), sep=";", encoding="latin-1")
            dfs.append(df)

        return _parse_raw(pd.concat(dfs, ignore_index=True))
    except Exception:
        return None


def fetch_pld() -> pd.DataFrame:
    """Carrega dados de PLD. Tenta API da CCEE, fallback para CSV local."""
    df = _fetch_from_api()
    if df is not None and len(df) > 0:
        if _LOCAL_CSV.parent.exists():
            df.to_csv(_LOCAL_CSV, index=False)
        return df

    if _LOCAL_CSV.exists():
        return pd.read_csv(_LOCAL_CSV, parse_dates=["data"])

    raise RuntimeError(
        "Não foi possível carregar dados da CCEE e nenhum cache local encontrado."
    )


def pld_atual(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna o PLD mais recente por submercado."""
    ultima_data = df["data"].max()
    return df[df["data"] == ultima_data].copy()


def pld_pivot_submercado(df: pd.DataFrame) -> pd.DataFrame:
    """Pivota os dados: index=data, colunas=submercado, valores=PLD."""
    return df.pivot_table(index="data", columns="submercado", values="pld").sort_index()


def estatisticas_por_submercado(df: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas descritivas do PLD por submercado."""
    stats = (
        df.groupby("submercado")["pld"]
        .agg(["mean", "median", "std", "min", "max"])
        .round(2)
    )
    stats.columns = ["Média", "Mediana", "Desvio Padrão", "Mínimo", "Máximo"]
    return stats.reset_index()


def media_anual(df: pd.DataFrame) -> pd.DataFrame:
    """PLD médio anual por submercado."""
    return (
        df.groupby(["ano", "submercado"])["pld"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"pld": "pld_medio"})
    )
