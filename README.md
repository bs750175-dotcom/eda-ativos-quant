# 📊 Análise Exploratória de Ativos com Python

**Núcleo Quant · Liga de Mercado Financeiro · UFU · 2026.1**

Análise quantitativa de quatro ativos ao longo de 4 anos (2020–2024), cobrindo retorno, risco, correlação e análise técnica de tendência.

---

## 🗂️ Ativos Analisados

| Ticker | Ativo | Descrição |
|---|---|---|
| `MGLU3.SA` | Magazine Luiza | Setor de varejo; alta volatilidade |
| `WEGE3.SA` | WEG S.A. | Setor industrial; crescimento consistente |
| `BOVA11.SA` | ETF Ibovespa | Benchmark do mercado acionário brasileiro |
| `USDBRL=X` | Dólar (USD/BRL) | Hedge cambial natural em crises |

**Período:** `2020-01-01` a `2024-01-01`

---

## 📋 O que foi implementado

### Passo 1 — Coleta e Tratamento de Dados
- Download via `yfinance` com `auto_adjust=True` para preços ajustados a splits e dividendos
- Download separado do Dólar (`USDBRL=X`), com remoção de timezone e `join(how="left")` para alinhar ao calendário da B3
- Tratamento de dados faltantes com `ffill()` + `dropna()`

### Passo 2 — Normalização e Retornos
- Normalização para **Base 100** permitindo comparação visual entre ativos em escalas diferentes
- Cálculo de retornos simples diários com `pct_change()`
- Gráfico interativo com Plotly

### Passo 3 — Análise de Volatilidade
- Volatilidade anualizada: `σ_diária × √252`
- Histograma interativo sobreposto de MGLU3 vs WEGE3 para comparar dispersão das distribuições

### Passo 4 — Correlação e Diversificação
- Matriz de correlação dos retornos com `.corr()`
- Heatmap interativo com `plotly.express.imshow` na escala `RdBu_r`
- Análise da relação **Dólar × Ibovespa** (correlação negativa esperada → hedge natural)

### Passo 5 — Médias Móveis e Tendência (WEGE3)
- MM20 (`rolling(20).mean()`) e MM200 (`rolling(200).mean()`)
- Detecção automática de **Golden Cross** e **Death Cross**
- Sinalização com `add_vline()` no gráfico interativo

---

## ⚙️ Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/eda-ativos-quant.git
cd eda-ativos-quant
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a análise

```bash
python setup.py    # cria a pasta graficos/
python analise.py
```

### 5. Visualizar os gráficos

Abra os arquivos `.html` gerados na pasta `graficos/` em qualquer navegador:

| Arquivo | Conteúdo |
|---|---|
| `01_normalizacao.html` | Desempenho normalizado Base 100 |
| `02_histograma_volatilidade.html` | Distribuição de retornos MGLU3 vs WEGE3 |
| `03_heatmap_correlacao.html` | Matriz de correlação |
| `04_medias_moveis_wege3.html` | MM20, MM200 e cruzamentos WEGE3 |

---

## 📁 Estrutura do projeto

```
eda-ativos-quant/
├── analise.py          # Script principal (Passos 1–5)
├── setup.py            # Cria pasta de saída
├── requirements.txt    # Dependências
├── graficos/           # Gerado ao executar (gráficos HTML interativos)
└── README.md
```

---

## 💡 Observações técnicas

- **Calendário forex vs B3:** O Dólar opera em dias que a B3 não opera. O `join(how="left")` garante que apenas os pregões brasileiros sejam mantidos, e o `ffill()` propaga o último câmbio válido nos dias sem cotação forex.
- **Correlação Dólar × Ibovespa:** Historicamente negativa — em períodos de crise, o capital estrangeiro sai do Brasil, pressionando o Real para baixo (Dólar sobe) ao mesmo tempo que o Ibovespa cai. Isso torna o Dólar um hedge natural na carteira.
- **Limitações das médias móveis:** Sinais de Golden/Death Cross são **lagging indicators** — chegam depois que a tendência já começou, gerando falsos positivos em mercados laterais e entradas tardias em tendências fortes. Não devem ser usados como sinal único de entrada/saída.

---

*Projeto desenvolvido para o exercício prático da Liga de Mercado Financeiro — UFU 2026.1*
