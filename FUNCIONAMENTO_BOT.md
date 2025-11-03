# 🤖 Da Vinci Sniper Bot - Manual de Funcionamento

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Estratégia Principal](#estratégia-principal)
3. [Indicadores Técnicos](#indicadores-técnicos)
4. [Filtros de Entrada](#filtros-de-entrada)
5. [Condições de Saída](#condições-de-saída)
6. [Fluxo de Operação](#fluxo-de-operação)
7. [Modos de Operação](#modos-de-operação)
8. [Arquivos e Persistência](#arquivos-e-persistência)

---

## 🎯 Visão Geral

O **Da Vinci Sniper Bot** é um bot de trading automatizado que opera no mercado de futuros da Binance, utilizando análise técnica para identificar oportunidades de entrada e saída. O bot monitora o mercado continuamente e executa operações baseadas em sinais técnicos validados por múltiplos filtros.

### Características Principais
- **Operação Automatizada**: Monitora o mercado 24/7 e executa trades automaticamente
- **Análise Técnica**: Utiliza múltiplos indicadores (EMA, RSI, ADX, MACD)
- **Gerenciamento de Risco**: Stop Loss, Take Profit e Trailing Stop integrados
- **Modo Demo**: Permite testar estratégias sem risco real
- **Interface Web**: Dashboard completo para monitoramento e configuração

---

## 📊 Estratégia Principal

### Sinal Primário: Crossover de EMAs

O bot utiliza o **crossover/crossunder das médias móveis exponenciais (EMA)** como sinal principal:

#### **ENTRADA LONG (Compra)**
- **Sinal**: EMA 8 cruza **ACIMA** da EMA 21 (Crossover)
- **Interpretação**: Indica início de tendência de alta
- **Condições Adicionais**: Todos os filtros de entrada devem ser atendidos

#### **ENTRADA SHORT (Venda)**
- **Sinal**: EMA 8 cruza **ABAIXO** da EMA 21 (Crossunder)
- **Interpretação**: Indica início de tendência de baixa
- **Condições Adicionais**: Todos os filtros de entrada devem ser atendidos

### Por que EMA 8 e EMA 21?

- **EMA 8 (Rápida)**: Reage rapidamente às mudanças de preço, captura movimentos de curto prazo
- **EMA 21 (Lenta)**: Representa a tendência de médio prazo, filtra ruídos
- **Crossover**: Quando a rápida cruza acima da lenta, indica momentum de alta
- **Crossunder**: Quando a rápida cruza abaixo da lenta, indica momentum de baixa

---

## 📈 Indicadores Técnicos

O bot calcula e utiliza os seguintes indicadores:

### 1. **EMA (Exponential Moving Average)**
- **EMA 8**: Média móvel exponencial de 8 períodos
- **EMA 21**: Média móvel exponencial de 21 períodos
- **Uso**: Sinal primário de entrada/saída

### 2. **RSI (Relative Strength Index)**
- **Período**: 9 candles
- **Faixa**: 0-100
- **Uso**: 
  - **Entrada LONG**: RSI > 55 (evita sobrecompra inicial)
  - **Entrada SHORT**: RSI < 40 (evita sobrevenda inicial)
  - **Saída**: Opcional quando RSI atinge extremos (Long ≥ 90, Short ≤ 10)

### 3. **ADX (Average Directional Index)**
- **Período**: 10 candles
- **Faixa**: 0-100 (mede força da tendência, não direção)
- **Uso**: 
  - **Entrada**: ADX > 18 (garante tendência forte) - Opcional
  - **Saída**: ADX < 25 (tendência enfraquecendo) - Opcional

### 4. **MACD (Moving Average Convergence Divergence)**
- **Rápida**: EMA de 8 períodos
- **Lenta**: EMA de 21 períodos
- **Sinal**: EMA de 5 períodos do histograma
- **Uso**: 
  - **Saída LONG**: MACD histograma negativo (com confirmação de preço)
  - **Saída SHORT**: MACD histograma positivo (com confirmação de preço)

### 5. **Volume**
- **Média Móvel**: Últimos 20 candles
- **Uso**: 
  - **Entrada**: Volume 15% acima da média (confirmação de interesse) - Opcional
  - **Saída**: Spike de volume (exaustão do movimento) - Opcional

---

## ✅ Filtros de Entrada

O bot aplica múltiplos filtros antes de executar uma entrada, garantindo que apenas sinais de alta qualidade sejam executados.

### Filtros Obrigatórios (Sempre Ativos)

1. **Crossover/Crossunder de EMA**
   - ✅ EMA 8 > EMA 21 (para LONG)
   - ✅ EMA 8 < EMA 21 (para SHORT)
   - **Motivo**: Sinal primário da estratégia

2. **RSI Entry Filter**
   - ✅ **LONG**: RSI > 55
   - ✅ **SHORT**: RSI < 40
   - **Motivo**: Evita entrar em extremos (sobrecompra/sobrevenda)

3. **Tendência Geral**
   - ✅ **LONG**: Preço acima da EMA 21
   - ✅ **SHORT**: Preço abaixo da EMA 21
   - **Motivo**: Confirma que está operando a favor da tendência

### Filtros Opcionais (Configuráveis)

4. **Volume Filter** (`USE_VOL`)
   - Volume atual > 115% da média (15% acima)
   - **Motivo**: Confirma interesse do mercado no movimento
   - **Default**: Desabilitado

5. **ADX Filter** (`USE_ADX`)
   - ADX > 18 (ou valor configurado)
   - **Motivo**: Garante que há tendência forte
   - **Default**: Habilitado (18)

### Cooldown de Sinais

- **Intervalo Mínimo**: 5 minutos entre sinais
- **Motivo**: Evita múltiplas entradas muito próximas (overtrading)
- **Configuração**: `SIGNAL_COOLDOWN = 300 segundos`

### Exemplo de Fluxo de Entrada

```
1. Bot detecta: EMA 8 cruza acima EMA 21 ✅
2. Verifica: RSI = 68 > 55 ✅
3. Verifica: Preço > EMA 21 ✅
4. Verifica: ADX = 23 > 18 ✅ (se habilitado)
5. Verifica: Volume > 115% média ✅ (se habilitado)
6. Verifica: Cooldown OK (último sinal há >5min) ✅
7. → EXECUTA ENTRADA LONG
```

---

## 🚪 Condições de Saída

O bot monitora continuamente a posição aberta e pode fechar por várias condições. As saídas são hierarquizadas e algumas requerem confirmação para evitar saídas prematuras.

### Saídas Prioritárias (Fechamento Imediato)

#### 1. **Stop Loss** (`USE_FIXED_EXIT`)
- **LONG**: Preço ≤ Entry Price × (1 - STOP_LOSS)
- **SHORT**: Preço ≥ Entry Price × (1 + STOP_LOSS)
- **Default**: 0.8% (0.008)
- **Prioridade**: ⚠️ ALTA - Proteção de capital
- **Motivo**: Limita perdas máximas por operação

#### 2. **Take Profit** (`USE_FIXED_EXIT`)
- **LONG**: Preço ≥ Entry Price × (1 + TAKE_PROFIT)
- **SHORT**: Preço ≤ Entry Price × (1 - TAKE_PROFIT)
- **Default**: 1.8% (0.018)
- **Prioridade**: ⚠️ ALTA - Realização de lucro
- **Motivo**: Garante lucro quando objetivo é atingido

#### 3. **Trailing Stop** (`USE_TRAILING`)
- **LONG**: Preço cai abaixo do pico menos trailing
  - `Trailing Price = Highest Price × (1 - TRAILING_STOP)`
- **SHORT**: Preço sobe acima do mínimo mais trailing
  - `Trailing Price = Lowest Price × (1 + TRAILING_STOP)`
- **Default**: 0.5% (0.005)
- **Prioridade**: ⚠️ ALTA - Protege lucro em tendências
- **Motivo**: Permite que o lucro aumente enquanto protege ganhos

### Saídas com Confirmação (Evita Saídas Prematuras)

#### 4. **EMA Crossunder/Crossover** (Conservador)
- **LONG**: EMA 8 < EMA 21 **E** já está em lucro (+1% mínimo)
- **SHORT**: EMA 8 > EMA 21 **E** já está em lucro (+1% mínimo)
- **Prioridade**: ⚠️ MÉDIA - Confirmação de reversão
- **Motivo**: Não fecha imediatamente, apenas se já tem lucro garantido

#### 5. **MACD Negativo/Positivo** (Inteligente)
- **LONG**: MACD histograma < 0 **E** uma das condições:
  - Preço recuou do pico (≥ 2× Trailing Stop) **OU**
  - Preço está em perda (< 99.5% do entry)
- **SHORT**: MACD histograma > 0 **E** uma das condições:
  - Preço subiu do mínimo (≥ 2× Trailing Stop) **OU**
  - Preço está em pequeno lucro (> 100.5% do entry)
- **Prioridade**: ⚠️ MÉDIA - Confirmação de momentum
- **Motivo**: Ignora flutuações momentâneas do MACD se a tendência ainda está forte

### Saídas Opcionais (Configuráveis)

#### 6. **RSI Exit Filter** (`USE_EXIT_RSI`)
- **LONG**: RSI ≥ EXIT_RSI_LONG (default: 90)
- **SHORT**: RSI ≤ EXIT_RSI_SHORT (default: 10)
- **Default**: Desabilitado
- **Motivo**: Sai quando atinge extremos de sobrecompra/sobrevenda

#### 7. **ADX Exit Filter** (`USE_EXIT_ADX`)
- **LONG/SHORT**: ADX < EXIT_ADX_THRESHOLD (default: 25)
- **Default**: Desabilitado
- **Motivo**: Sai quando a tendência perde força

#### 8. **Time Exit** (`USE_TIME_EXIT`)
- Tempo em posição ≥ EXIT_AFTER_MINUTES (default: 60min)
- **Default**: Desabilitado
- **Motivo**: Limita tempo máximo em posição

#### 9. **Volume Spike Exit** (`EXIT_ON_VOLUME_SPIKE`)
- Volume > Média × EXIT_VOLUME_MULTIPLIER (default: 2.0x)
- **Default**: Desabilitado
- **Motivo**: Sai em momentos de exaustão/panic do mercado

### Exemplo de Fluxo de Saída

```
Posição LONG aberta em $3864.13
Pico alcançado: $3880.58
Preço atual: $3874.09

Verificações:
1. Stop Loss: $3833.22 ❌ (não atingido)
2. Take Profit: $3933.68 ❌ (não atingido)
3. Trailing Stop: $3861.18 ❌ (não atingido)
4. EMA: 3870.81 > 3864.75 ✅ (ainda positivo)
5. MACD: -0.0795 (negativo) ✅
   → Mas preço está próximo do pico
   → NÃO fecha imediatamente
   
Resultado: Posição mantida (com a nova lógica inteligente)
```

---

## 🔄 Fluxo de Operação

### Loop Principal do Bot

O bot executa um loop contínuo a cada **60 segundos** (1 minuto), independente do timeframe configurado.

```
┌─────────────────────────────────────┐
│   INICIALIZAÇÃO DO BOT              │
│   - Carrega configuração            │
│   - Inicializa arquivos             │
│   - Conecta à Binance (se Live)     │
│   - Limpa operações antigas         │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   LOOP PRINCIPAL (a cada 60s)       │
│                                     │
│   1. Recarrega configuração         │
│   2. Busca dados OHLCV (candles)    │
│   3. Calcula indicadores técnicos   │
│   4. Gera sinais de entrada         │
│   5. Verifica condições de saída    │
│   6. Atualiza PnL das posições      │
│   7. Registra logs                  │
│   8. Aguarda 60 segundos            │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   SEM POSIÇÃO ABERTA?       │   │
│   └─────────────────────────────┘   │
│            │          │              │
│         SIM │          │ NÃO          │
│            ▼          ▼               │
│    ┌──────────┐  ┌──────────────┐    │
│    │Verifica  │  │Verifica      │    │
│    │Entrada   │  │Saída         │    │
│    └──────────┘  └──────────────┘    │
└─────────────────────────────────────┘
              │
              ▼
        (Continua Loop)
```

### Fluxo Detalhado: Entrada

```
1. Bot detecta crossover/crossunder ✅
2. Verifica filtros de entrada:
   ├─ RSI dentro do range? ✅
   ├─ ADX > threshold? ✅ (se habilitado)
   ├─ Volume acima da média? ✅ (se habilitado)
   ├─ Preço na direção correta? ✅
   └─ Cooldown respeitado? ✅
3. Calcula quantidade:
   Quantidade = (Position Size × Leverage) / Preço
4. Executa ordem (DEMO ou LIVE):
   ├─ DEMO: Simula entrada (não executa na Binance)
   └─ LIVE: Cria ordem market na Binance
5. Registra entrada:
   ├─ Salva em operations.json
   ├─ Define entry_price, entry_time
   ├─ Inicializa highest_price/lowest_price
   └─ Ativa flag in_position
```

### Fluxo Detalhado: Saída

```
1. Bot verifica condições de saída a cada minuto
2. Ordem de prioridade:
   ├─ Stop Loss? → FECHA IMEDIATAMENTE ⚠️
   ├─ Take Profit? → FECHA IMEDIATAMENTE ⚠️
   ├─ Trailing Stop? → FECHA IMEDIATAMENTE ⚠️
   ├─ EMA Crossunder + Lucro? → FECHA ✅
   ├─ MACD Negativo + Confirmação? → FECHA ✅
   ├─ RSI Exit (se habilitado)? → FECHA ✅
   ├─ ADX Exit (se habilitado)? → FECHA ✅
   ├─ Time Exit (se habilitado)? → FECHA ✅
   └─ Volume Spike (se habilitado)? → FECHA ✅
3. Executa saída:
   ├─ DEMO: Simula saída, atualiza saldo
   └─ LIVE: Cria ordem market reduzOnly na Binance
4. Calcula PnL final:
   PnL = (Exit Price - Entry Price) × Quantidade × Direção
5. Registra saída:
   ├─ Remove de open_operations
   ├─ Adiciona em closed_operations
   ├─ Salva em operations.json
   └─ Reseta estado (in_position = False)
```

---

## 🎮 Modos de Operação

### Modo DEMO (Recomendado para Iniciantes)

**Características:**
- ✅ Nenhuma ordem real é executada na Binance
- ✅ Saldo simulado (inicial: $1000)
- ✅ Operações registradas para análise
- ✅ Sem risco financeiro real
- ✅ Permite testar estratégias livremente

**Funcionamento:**
1. Bot calcula todas as condições normalmente
2. Quando detecta entrada/saída:
   - Simula execução (não cria ordem real)
   - Atualiza saldo demo em `demo_balance.json`
   - Registra operação em `operations.json`
3. PnL é calculado baseado em preços reais do mercado

**Vantagens:**
- Teste sem risco
- Validação de estratégias
- Aprendizado da plataforma

### Modo LIVE (Binance Real)

**Características:**
- ⚠️ Ordens reais executadas na Binance
- ⚠️ Dinheiro real em risco
- ✅ Requer API Keys configuradas
- ✅ Permissões: Trading e Futures

**Funcionamento:**
1. Bot conecta à Binance via API
2. Quando detecta entrada:
   - Cria ordem **market** na Binance
   - Posição é aberta real no mercado
3. Quando detecta saída:
   - Cria ordem **market reduceOnly**
   - Posição é fechada real no mercado
4. Saldo atualizado automaticamente pela Binance

**⚠️ IMPORTANTE:**
- Sempre teste extensivamente no modo DEMO antes
- Comece com valores pequenos
- Monitore continuamente
- Configure Stop Loss rigorosamente

---

## 💾 Arquivos e Persistência

### Arquivos de Configuração

#### `bot_config.json`
Contém todas as configurações do bot:
```json
{
  "SYMBOL": "ETH/USDT",
  "TIMEFRAME": "3m",
  "POSITION_SIZE_USD": 50,
  "LEVERAGE": 10,
  "USE_DEMO": true,
  "STOP_LOSS": 0.008,
  "TAKE_PROFIT": 0.018,
  "RSI_LONG": 55,
  ...
}
```

**Atualização:**
- Atualizado pela interface web
- Bot recarrega automaticamente a cada loop
- Mudanças aplicadas sem reiniciar o bot

### Arquivos de Dados

#### `operations.json`
Armazena histórico de operações:
```json
{
  "open_operations": [
    {
      "id": 1762124627613,
      "symbol": "ETH/USDT",
      "side": "LONG",
      "entry_price": 3864.13,
      "current_price": 3908.11,
      "quantity": 0.129395,
      "pnl": 5.69,
      "status": "open"
    }
  ],
  "closed_operations": [...]
}
```

**Atualização:**
- Criado quando entra em posição
- Atualizado a cada minuto (PnL atual)
- Operações fechadas movidas para `closed_operations`

#### `demo_balance.json`
Saldo do modo demo:
```json
{
  "balance": 1001.35
}
```

**Atualização:**
- Atualizado quando operação é fechada
- PnL é adicionado/subtraído do saldo

### Arquivos de Log

#### `davinci_bot.log`
Log principal do bot com:
- Inicialização
- Sinais detectados
- Entradas/saídas
- Status a cada minuto
- Erros e avisos

#### `bot_output.log`
Output do processo (inclui erros do sistema)

---

## 📊 Exemplo Completo de Operação

### Cenário: Operação LONG

**1. Detecção do Sinal (20:03:47)**
```
Preço: $3864.60
EMA 8: 3856.14
EMA 21: 3854.90
→ EMA 8 cruza ACIMA da EMA 21 ✅

Verificações:
- RSI: 71.1 > 55 ✅
- ADX: 23.3 > 18 ✅
- Volume: OK ✅
- Preço > EMA 21 ✅
→ TODOS OS FILTROS PASSARAM
```

**2. Execução da Entrada (20:03:47)**
```
Ordem executada: LONG
Preço de entrada: $3864.13
Quantidade: 0.129395 ETH
Posição: $50 × 10x = $500 exposição
```

**3. Monitoramento (20:03 - 20:30)**
```
20:04 - PnL: +$0.12 (+0.02%)
20:10 - PnL: +$1.28 (+0.26%)
20:15 - PnL: +$1.46 (+0.29%) ← Pico
20:19 - PnL: +$1.87 (+0.37%) ← Máximo
20:30 - PnL: +$1.11 (+0.22%)
```

**4. Detecção de Saída (20:30:36)**
```
Condições verificadas:
- Stop Loss: $3833.22 ❌ (preço: $3874.09)
- Take Profit: $3933.68 ❌ (preço: $3874.09)
- Trailing Stop: $3861.18 ❌ (preço: $3874.09)
- MACD: -0.0795 (negativo) ✅
  → MAS preço ainda próximo do pico
  → Com nova lógica: NÃO fecha ainda

Resultado: Posição mantida (evita saída prematura)
```

**5. Saída Real (Se ocorrer)**
```
Motivo: Take Profit atingido OU Trailing Stop
Preço de saída: $3933.68 (exemplo)
PnL: +$1.35 a +$1.87 (dependendo do momento)
Duração: ~27-60 minutos (exemplo)
```

---

## 🔧 Parâmetros Importantes

### Intervalos e Timing

- **CHECK_INTERVAL**: 60 segundos (verificação a cada minuto)
- **SIGNAL_COOLDOWN**: 300 segundos (5 minutos entre sinais)
- **Timeframe**: Configurável (1m, 3m, 5m, 15m, 30m, 1h)

### Cálculo de Quantidade

```
Quantidade = (POSITION_SIZE_USD × LEVERAGE) / Preço Atual

Exemplo:
- Position Size: $50
- Leverage: 10x
- Preço ETH: $3864

Quantidade = ($50 × 10) / $3864
Quantidade = 0.129395 ETH
```

### Cálculo de PnL

**LONG:**
```
PnL % = ((Preço Atual - Preço Entrada) / Preço Entrada) × 100
PnL $ = (Preço Atual - Preço Entrada) × Quantidade
```

**SHORT:**
```
PnL % = ((Preço Entrada - Preço Atual) / Preço Entrada) × 100
PnL $ = (Preço Entrada - Preço Atual) × Quantidade
```

---

## 🎓 Dicas e Boas Práticas

### Para Melhores Resultados

1. **Teste em DEMO Primeiro**
   - Execute por pelo menos 24-48 horas
   - Analise os logs e resultados
   - Ajuste filtros conforme necessário

2. **Configure Stop Loss Rigorosamente**
   - Nunca deixe sem proteção
   - Default 0.8% é conservador
   - Ajuste conforme sua tolerância a risco

3. **Monitore os Logs**
   - Verifique quantos sinais foram bloqueados
   - Entenda por que operações saíram
   - Ajuste filtros baseado em dados reais

4. **Ajuste Filtros Gradualmente**
   - Comece com configurações conservadoras
   - Aumente agressividade progressivamente
   - Teste cada mudança separadamente

5. **Use Timeframes Adequados**
   - Timeframes menores (1m-3m): Mais operações, mais ruído
   - Timeframes maiores (15m-1h): Menos operações, mais qualidade
   - Recomendação: 3m-5m para começar

### Armadilhas Comuns

- ❌ **Filtros Muito Restritivos**: Pode não entrar em nenhuma operação
- ❌ **Filtros Muito Permissivos**: Muitas operações de baixa qualidade
- ❌ **Sem Stop Loss**: Perdas podem se acumular
- ❌ **Alavancagem Excessiva**: Amplifica perdas rapidamente
- ❌ **Ignorar o Modo Demo**: Teste sempre primeiro!

---

## 📝 Conclusão

O Da Vinci Sniper Bot é uma ferramenta poderosa para trading automatizado, mas requer:
- ✅ **Configuração adequada** dos filtros
- ✅ **Compreensão** da estratégia
- ✅ **Testes extensivos** antes de usar dinheiro real
- ✅ **Monitoramento** contínuo dos resultados
- ✅ **Ajustes** baseados em dados reais

Lembre-se: **Trading envolve risco**. Sempre opere com capital que você pode perder e comece sempre no modo DEMO.

---

**Versão do Documento**: 1.0  
**Última Atualização**: 2025-11-02  
**Compatível com**: Da Vinci Sniper Bot v2.0+

