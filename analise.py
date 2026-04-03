"""
Análise Exploratória de Ativos com Python
Núcleo Quant · Liga de Mercado Financeiro · UFU · 2026.1

Ativos: MGLU3.SA, WEGE3.SA, BOVA11.SA, USDBRL=X
Período: 2020-01-01 a 2024-01-01
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────
# PASSO 1 — Coleta e Tratamento de Dados
# ─────────────────────────────────────────

START = "2020-01-01"
END   = "2024-01-01"

TICKERS_B3 = ["MGLU3.SA", "WEGE3.SA", "BOVA11.SA"]

print("📥 Baixando dados da B3...")
df_b3 = yf.download(
    TICKERS_B3,
    start=START,
    end=END,
    auto_adjust=True,
    progress=False
)["Close"]

print("📥 Baixando Dólar (USDBRL=X) separadamente...")
df_usd = yf.download(
    "USDBRL=X",
    start=START,
    end=END,
    auto_adjust=True,
    progress=False
)["Close"]

# Remove timezone para compatibilidade de índices
df_b3.index   = df_b3.index.tz_localize(None)
df_usd.index  = df_usd.index.tz_localize(None)
df_usd.name   = "USDBRL=X"

# Join left: mantém apenas os dias de pregão da B3
df_raw = df_b3.join(df_usd, how="left")

# Tratamento de dados faltantes
df_clean = df_raw.ffill().dropna()

print(f"\n✅ Dados prontos: {len(df_clean)} pregões | {df_clean.columns.tolist()}")
print(df_clean.tail())


# ─────────────────────────────────────────
# PASSO 2 — Normalização e Retornos
# ─────────────────────────────────────────

# Normalização Base 100
df_norm = (df_clean / df_clean.iloc[0]) * 100

fig_norm = go.Figure()
colors = {"MGLU3.SA": "#e74c3c", "WEGE3.SA": "#2ecc71",
          "BOVA11.SA": "#3498db", "USDBRL=X": "#f39c12"}

for col in df_norm.columns:
    fig_norm.add_trace(go.Scatter(
        x=df_norm.index, y=df_norm[col],
        name=col, line=dict(color=colors[col], width=1.8)
    ))

fig_norm.update_layout(
    title="Desempenho Normalizado — Base 100 (Jan/2020)",
    xaxis_title="Data", yaxis_title="Índice (Base 100)",
    hovermode="x unified", template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_norm.write_html("graficos/01_normalizacao.html")
print("\n📊 Gráfico 1 salvo: graficos/01_normalizacao.html")

# Retornos simples diários
returns = df_clean.pct_change().dropna()
print("\n📈 Primeiras linhas dos retornos diários:")
print(returns.head())


# ─────────────────────────────────────────
# PASSO 3 — Análise de Volatilidade
# ─────────────────────────────────────────

vol_anual = returns.std() * np.sqrt(252)

print("\n📉 Volatilidade Anualizada:")
for ticker, v in vol_anual.sort_values(ascending=False).items():
    print(f"  {ticker:12s}: {v:.2%}")

print(f"\n  🔴 Maior volatilidade : {vol_anual.idxmax()} ({vol_anual.max():.2%})")
print(f"  🟢 Menor volatilidade : {vol_anual.idxmin()} ({vol_anual.min():.2%})")

# Histograma MGLU3 vs WEGE3
fig_hist = go.Figure()
for ticker, cor in [("MGLU3.SA", "#e74c3c"), ("WEGE3.SA", "#2ecc71")]:
    fig_hist.add_trace(go.Histogram(
        x=returns[ticker],
        name=ticker,
        opacity=0.65,
        nbinsx=80,
        marker_color=cor
    ))

fig_hist.update_layout(
    barmode="overlay",
    title="Distribuição dos Retornos Diários — MGLU3 vs WEGE3",
    xaxis_title="Retorno Diário", yaxis_title="Frequência",
    template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_hist.write_html("graficos/02_histograma_volatilidade.html")
print("📊 Gráfico 2 salvo: graficos/02_histograma_volatilidade.html")


# ─────────────────────────────────────────
# PASSO 4 — Correlação e Diversificação
# ─────────────────────────────────────────

corr = returns.corr()

print("\n🔗 Matriz de Correlação:")
print(corr.round(2))

fig_corr = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1, zmax=1,
    title="Matriz de Correlação dos Retornos Diários",
    aspect="auto"
)
fig_corr.update_layout(template="plotly_white")
fig_corr.write_html("graficos/03_heatmap_correlacao.html")
print("📊 Gráfico 3 salvo: graficos/03_heatmap_correlacao.html")

corr_usd_bova = corr.loc["USDBRL=X", "BOVA11.SA"]
print(f"\n💡 Correlação Dólar × Ibovespa: {corr_usd_bova:.2f}")
print("   → Correlação negativa: o Dólar tende a subir quando o Ibovespa cai,")
print("     funcionando como hedge natural em períodos de crise.")


# ─────────────────────────────────────────
# PASSO 5 — Médias Móveis e Tendência (WEGE3)
# ─────────────────────────────────────────

close_wege = df_clean["WEGE3.SA"]
mm20  = close_wege.rolling(20).mean()
mm200 = close_wege.rolling(200).mean()

# Detectar cruzamentos
cross = pd.DataFrame({"mm20": mm20, "mm200": mm200}).dropna()
cross["diff"]  = cross["mm20"] - cross["mm200"]
cross["shift"] = cross["diff"].shift(1)

golden_cross = cross[(cross["diff"] > 0) & (cross["shift"] <= 0)].index.tolist()
death_cross  = cross[(cross["diff"] < 0) & (cross["shift"] >= 0)].index.tolist()

print(f"\n🔆 Golden Crosses detectados: {len(golden_cross)}")
for d in golden_cross:
    print(f"   {d.date()}")

print(f"💀 Death Crosses detectados: {len(death_cross)}")
for d in death_cross:
    print(f"   {d.date()}")

fig_mm = go.Figure()
fig_mm.add_trace(go.Scatter(x=close_wege.index, y=close_wege,
                            name="WEGE3.SA", line=dict(color="#2ecc71", width=1.5)))
fig_mm.add_trace(go.Scatter(x=mm20.index, y=mm20,
                            name="MM20", line=dict(color="#3498db", width=1.5, dash="dot")))
fig_mm.add_trace(go.Scatter(x=mm200.index, y=mm200,
                            name="MM200", line=dict(color="#e74c3c", width=2)))

for d in golden_cross:
    fig_mm.add_vline(x=d, line=dict(color="gold", dash="dash", width=1.5),
                     annotation_text="Golden Cross", annotation_position="top right",
                     annotation_font_color="goldenrod")

for d in death_cross:
    fig_mm.add_vline(x=d, line=dict(color="red", dash="dash", width=1.5),
                     annotation_text="Death Cross", annotation_position="top right",
                     annotation_font_color="red")

fig_mm.update_layout(
    title="WEGE3.SA — Preço de Fechamento com MM20 e MM200",
    xaxis_title="Data", yaxis_title="Preço (R$)",
    hovermode="x unified", template="plotly_white",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_mm.write_html("graficos/04_medias_moveis_wege3.html")
print("📊 Gráfico 4 salvo: graficos/04_medias_moveis_wege3.html")

print("\n✅ Análise concluída! Todos os gráficos foram salvos na pasta graficos/")
