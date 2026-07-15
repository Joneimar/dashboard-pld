# 📊 Dashboard — PLD · Preço de Liquidação das Diferenças

Dashboard interativo para análise do **PLD** (preço spot da energia elétrica no Brasil), com dados consolidados por submercado desde 2001. Dados consumidos em tempo real da **API de Dados Abertos da CCEE**.

O PLD é o principal indicador do mercado de curto prazo do SIN e impacta diretamente operações de trading, contratos bilaterais e a receita de geradores. Este dashboard permite visualizar tendências históricas, sazonalidade, spreads entre submercados e volatilidade.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?logo=streamlit&logoColor=white)
![CCEE](https://img.shields.io/badge/Dados-CCEE_Abertos-009c3b)
![License](https://img.shields.io/badge/Licença-MIT-blue)

## Funcionalidades

- **PLD vigente** por submercado (SE/CO, S, NE, N) com KPIs visuais.
- **Série histórica** (2001–2026) com linhas por submercado.
- **Spread entre submercados** — diferença máx-mín, relevante para arbitragem em trading.
- **Boxplot de distribuição** — dispersão e outliers do PLD por submercado.
- **PLD médio anual** — barras agrupadas para comparação entre anos e submercados.
- **Heatmap mensal** (ano × mês) — padrões sazonais do PLD por submercado.
- **Variação mensal** — oscilação percentual mês a mês com destaque de altas/baixas.
- **Estatísticas descritivas** — média, mediana, desvio padrão, mín/máx por submercado.
- **Filtros interativos** por período e submercado.
- **Seção metodológica** com contexto regulatório sobre CMO, NEWAVE/DECOMP e PLD horário.

## Pipeline de Dados

```
Portal CCEE (CKAN)  →  Scraping de URLs  →  Download CSVs  →  Consolidação (pandas)  →  Cache 1h  →  Dashboard (Streamlit + Plotly)
```

1. Scraping das URLs de download no portal CKAN da CCEE (7 recursos CSV).
2. Download e concatenação de todos os anos (2001–2026, ~1200 registros).
3. Tipagem e enriquecimento temporal (`MES_REFERENCIA` → datetime).
4. Cache de 1h para performance.
5. Visualizações interativas com Plotly em tema escuro.

## Estrutura do Projeto

```
dashboard-pld/
├── app.py                 # App Streamlit principal
├── src/
│   ├── api.py             # Pipeline ETL: scraping + download + transformações
│   └── charts.py          # 6 gráficos Plotly (série, spread, boxplot, heatmap, etc.)
├── requirements.txt
└── README.md
```

## Como Executar

```bash
git clone https://github.com/Joneimar/dashboard-pld.git
cd dashboard-pld

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run app.py
```

## Tecnologias

| Tecnologia | Uso |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **Streamlit** | Framework do dashboard |
| **pandas** | Manipulação e análise de dados |
| **Plotly** | Gráficos interativos |
| **requests** | Download de CSVs e scraping de URLs |

## Fonte de Dados

[Dados Abertos da CCEE](https://dadosabertos.ccee.org.br/dataset/pld_media_mensal) — PLD Médio Mensal por submercado, com dados desde janeiro de 2001. Licença CC-BY-4.0.

## Autor

**Joneimar Lemos** — Desenvolvedor & Analista de Dados no Setor Elétrico

- Portfólio: [energycode.com.br](https://energycode.com.br)
- LinkedIn: [linkedin.com/in/joneimar](https://linkedin.com/in/joneimar)

## Licença

MIT
