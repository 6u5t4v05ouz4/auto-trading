# 🗺️ Mapeamento Detalhado de Funções por Módulo

Este documento mostra exatamente onde cada função do `index.html` atual será colocada na estrutura modularizada.

---

## 📊 Resumo por Linha do Arquivo Original

| Linhas | Conteúdo | Destino Proposto |
|--------|----------|------------------|
| 1-6 | Head/Meta | `index.html` (mantido) |
| 7-896 | CSS Completo | `static/css/*.css` (5 arquivos) |
| 898-1566 | HTML Structure | `index.html` + `components/*.html` |
| 1567 | Lightweight Charts CDN | `index.html` (mantido) |
| 1569-2839 | JavaScript Completo | `static/js/*.js` (11 arquivos) |

---

## 🔍 Mapeamento Função → Módulo

### `sound-system.js`
**Linhas Originais:** 1575-1696

```javascript
// Variáveis globais
let soundEnabled = true;
let volumeLevel = 0.5;
let lastTradeCount = 0;

// Funções:
- playTradeSound(type)          // linhas 1578-1623
- testSound()                   // linhas 1625-1629 (opcional, pode ser removido)

// Event Listeners:
- DOMContentLoaded listener     // linhas 1632-1696
  * updateToggleUI()
  * updateVolumeUI()
  * Volume compact control
```

**Tamanho Estimado:** ~95 linhas

---

### `chart.js`
**Linhas Originais:** 1698-1930

```javascript
// Variável global (será movida para globals.js)
let priceChart = null;

// Funções:
- switchTab(tab)                // linhas 1699-1741
- loadChart()                    // linhas 1744-1771
- drawChart(candles, ema_short, ema_mid, forceFit) // linhas 1774-1930

// Event Listeners:
- window resize                 // linhas 1905-1907
```

**Tamanho Estimado:** ~230 linhas

---

### `config.js`
**Linhas Originais:** 1932-2035, 2073-2110, 2210-2330, 2364-2421

```javascript
// Funções:
- loadConfig()                   // linhas 1933-2001
- saveConfig()                   // linhas 2364-2421
- saveFiltersConfig()           // linhas 2210-2219
- updateConfigSummaries()       // linhas 2073-2110
- updateActiveFilters(config)    // linhas 2222-2319
- updateSidebarStatus(config)   // linhas 2322-2330
- updateDemoUI()                 // linhas 2004-2017
- loadDemoBalance()              // linhas 2020-2030

// Event Listeners:
- useDemo change                // linhas 2033-2035
- Config summaries inputs        // linhas 2113-2133
```

**Tamanho Estimado:** ~300 linhas

---

### `modals.js`
**Linhas Originais:** 2038-2045, 2048-2070, 2136-2142, 2145-2155

```javascript
// Funções:
- openConfigModal()              // linhas 2038-2041
- closeConfigModal()             // linhas 2043-2045
- switchConfigTab(tab)           // linhas 2048-2070
- openHelpModal()                // linhas 2136-2138
- closeHelpModal()               // linhas 2140-2142

// Event Listeners:
- window.onclick (close modals)  // linhas 2145-2155
```

**Tamanho Estimado:** ~70 linhas

---

### `bot-control.js`
**Linhas Originais:** 2424-2463

```javascript
// Funções:
- startBot()                     // linhas 2424-2443
- stopBot()                      // linhas 2446-2463
```

**Tamanho Estimado:** ~40 linhas

**Nota:** Estas funções chamam `saveConfig()` e `api-client.js` - garantir ordem de carregamento.

---

### `api-client.js`
Este módulo **extrai apenas as chamadas fetch()** das funções existentes.

**Funções que FAZEM fetch() (extrair lógica de API):**

```javascript
// Endpoints identificados:
- GET  /api/config               // usado em loadConfig()
- POST /api/config               // usado em saveConfig()
- GET  /api/chart/:symbol        // usado em loadChart()
- GET  /api/price/:symbol        // usado em loadPrice()
- GET  /api/pnl                  // usado em loadPnl()
- GET  /api/operations           // usado em loadOperations()
- GET  /api/logs                 // usado em loadLogs()
- POST /api/clear-logs           // usado em clearLogs()
- GET  /api/demo-balance         // usado em loadDemoBalance()
- POST /api/reset-demo           // usado em resetDemo()
- POST /api/start-bot            // usado em startBot()
- POST /api/stop-bot             // usado em stopBot()

// Estrutura proposta:
class ApiClient {
    async getConfig()
    async saveConfig(config)
    async getChart(symbol)
    async getPrice(symbol)
    async getPnl()
    async getOperations()
    async getLogs()
    async clearLogs()
    async getDemoBalance()
    async resetDemo()
    async startBot()
    async stopBot()
}
```

**Tamanho Estimado:** ~200 linhas

**Nota:** Este módulo NÃO substitui as funções existentes. As funções atuais serão refatoradas para USAR o ApiClient.

---

### `operations.js`
**Linhas Originais:** 2580-2644

```javascript
// Funções:
- loadOperations()               // linhas 2580-2613
- createOperationCard(op, isClosed) // linhas 2616-2644
```

**Tamanho Estimado:** ~70 linhas

**Nota:** `loadOperations()` usa `api-client.js` para buscar dados.

---

### `dashboard-data.js` (Novo nome sugerido)
**Linhas Originais:** 2647-2769

```javascript
// Funções:
- loadPrice()                    // linhas 2647-2687
- loadPnl()                      // linhas 2690-2769
```

**Tamanho Estimado:** ~120 linhas

**Nota:** Estas funções fazem chamadas API, mas também atualizam UI. Manter lógica de apresentação aqui, API calls via `api-client.js`.

---

### `logs.js`
**Linhas Originais:** 2478-2553

```javascript
// Funções:
- loadLogs()                     // linhas 2478-2527
- clearLogs()                    // linhas 2530-2553
```

**Tamanho Estimado:** ~80 linhas

**Nota:** `loadLogs()` interage com `sound-system.js` (toca som em novas operações).

---

### `sidebar.js`
**Linhas Originais:** 2158-2180, 2333-2361, 2183-2208

```javascript
// Funções:
- toggleMobileSidebar()          // linhas 2158-2170
- closeMobileSidebar()           // linhas 2172-2180
- updateSidebarPrice(priceData)  // linhas 2333-2348
- updateSidebarPnl(pnlData)      // linhas 2351-2361

// Event Listeners:
- window resize                  // linhas 2183-2208
- DOMContentLoaded (mobile init) // linhas 2202-2208
```

**Tamanho Estimado:** ~80 linhas

---

### `utils.js`
**Linhas Originais:** 2466-2475, 2556-2577

```javascript
// Funções:
- showAlert(message, type)       // linhas 2466-2475
- resetDemo()                    // linhas 2556-2577
```

**Tamanho Estimado:** ~30 linhas

---

### `main.js` (Inicialização)
**Linhas Originais:** 2772-2839

```javascript
// Inicialização:
- loadConfig() chamada inicial   // linha 2772

// Polling Automático:
- Gráfico (30s)                  // linhas 2775-2788
  * loadChart() se tab ativa
  
- Dashboard (5s)                 // linhas 2791-2839
  * Status check
  * loadLogs()
  * loadPrice()
  * loadOperations()
  * loadPnl()
  * loadDemoBalance() (se demo)
```

**Tamanho Estimado:** ~70 linhas

---

### `globals.js` (NOVO - Criar)
**Variáveis que precisam ser compartilhadas:**

```javascript
// Variáveis globais compartilhadas entre módulos
window.DaVinciBot = {
    // Chart
    priceChart: null,
    
    // Sound System
    soundEnabled: true,
    volumeLevel: 0.5,
    lastTradeCount: 0,
    
    // State
    currentConfig: null,
    currentTab: 'chart',
    
    // Utils
    updateInterval: null,
    chartUpdateInterval: null
};
```

**Tamanho Estimado:** ~20 linhas

---

## 📦 Dependências entre Módulos

```
main.js
  ├── depende de: todos os outros módulos
  └── inicializa: tudo

config.js
  ├── depende de: api-client.js, utils.js
  └── usa: globals.js

chart.js
  ├── depende de: api-client.js
  └── usa: globals.js (priceChart)

modals.js
  ├── depende de: config.js
  └── usa: utils.js

bot-control.js
  ├── depende de: config.js, api-client.js, utils.js
  └── função isolada

api-client.js
  └── função isolada (classe utilitária)

operations.js
  ├── depende de: api-client.js
  └── função isolada

dashboard-data.js
  ├── depende de: api-client.js
  └── função isolada

logs.js
  ├── depende de: api-client.js, sound-system.js
  └── usa: globals.js (soundEnabled, lastTradeCount)

sidebar.js
  └── função isolada (UI apenas)

sound-system.js
  └── usa: globals.js (soundEnabled, volumeLevel)

utils.js
  └── função isolada

filters.js
  └── função isolada (UI apenas)
```

---

## 🔄 Ordem de Carregamento Correta

```html
<!-- 1. Variáveis globais primeiro -->
<script src="/static/js/globals.js"></script>

<!-- 2. Utilitários básicos -->
<script src="/static/js/utils.js"></script>

<!-- 3. Cliente API (não tem dependências) -->
<script src="/static/js/api-client.js"></script>

<!-- 4. Sistema de som (isolado, mas logs.js precisa) -->
<script src="/static/js/sound-system.js"></script>

<!-- 5. Componentes UI (independentes) -->
<script src="/static/js/filters.js"></script>
<script src="/static/js/operations.js"></script>
<script src="/static/js/sidebar.js"></script>

<!-- 6. Dashboard (usa api-client) -->
<script src="/static/js/dashboard-data.js"></script>
<script src="/static/js/logs.js"></script>
<script src="/static/js/chart.js"></script>

<!-- 7. Configuração (usa api-client, utils) -->
<script src="/static/js/config.js"></script>

<!-- 8. Modais (usa config) -->
<script src="/static/js/modals.js"></script>

<!-- 9. Bot control (usa config, api-client, utils) -->
<script src="/static/js/bot-control.js"></script>

<!-- 10. Main (inicializa tudo) -->
<script src="/static/js/main.js"></script>
```

---

## ✅ Checklist de Funcionalidades por Módulo

### `sound-system.js`
- ✅ Reproduz som LONG
- ✅ Reproduz som SHORT
- ✅ Reproduz som EXIT
- ✅ Toggle enable/disable
- ✅ Controle de volume
- ✅ Slider compacto funcional

### `chart.js`
- ✅ Alterna entre tabs
- ✅ Carrega dados do gráfico
- ✅ Desenha candles
- ✅ Desenha EMA 8
- ✅ Desenha EMA 21
- ✅ Preserva zoom/pan
- ✅ Atualização automática
- ✅ Resize responsivo

### `config.js`
- ✅ Carrega configuração do servidor
- ✅ Salva configuração
- ✅ Atualiza summaries em tempo real
- ✅ Mostra badges de filtros ativos
- ✅ Gerencia modo Demo
- ✅ Atualiza sidebar

### `modals.js`
- ✅ Abre/fecha modal de config
- ✅ Abre/fecha modal de ajuda
- ✅ Alterna tabs Entry/Exit
- ✅ Fecha ao clicar fora

### `bot-control.js`
- ✅ Inicia bot
- ✅ Para bot
- ✅ Valida configuração antes

### `operations.js`
- ✅ Lista operações abertas
- ✅ Lista operações fechadas
- ✅ Cria cards de operação
- ✅ Mostra PnL

### `dashboard-data.js`
- ✅ Carrega preço atual
- ✅ Mostra mudança 24h
- ✅ Carrega PnL total
- ✅ Mostra estatísticas
- ✅ Atualiza sidebar

### `logs.js`
- ✅ Carrega logs do servidor
- ✅ Formata logs por tipo
- ✅ Auto-scroll
- ✅ Detecta novas operações
- ✅ Toca som em novas operações
- ✅ Limpa logs

### `sidebar.js`
- ✅ Toggle mobile menu
- ✅ Fecha mobile menu
- ✅ Atualiza preço no sidebar
- ✅ Atualiza PnL no sidebar
- ✅ Responsivo

### `utils.js`
- ✅ Mostra alertas
- ✅ Reset demo balance

### `main.js`
- ✅ Inicializa tudo ao carregar
- ✅ Polling de status (5s)
- ✅ Polling de dados (5s)
- ✅ Atualização de gráfico (30s)
- ✅ Carrega config inicial

---

## 📊 Estatísticas Finais

| Módulo | Linhas Estimadas | Funções | Dependências |
|--------|------------------|---------|--------------|
| globals.js | ~20 | 0 | 0 |
| utils.js | ~30 | 2 | 0 |
| api-client.js | ~200 | 12 | 0 |
| sound-system.js | ~95 | 2 | 1 (globals) |
| filters.js | ~100 | 1 | 0 |
| operations.js | ~70 | 2 | 1 (api-client) |
| sidebar.js | ~80 | 4 | 0 |
| dashboard-data.js | ~120 | 2 | 1 (api-client) |
| logs.js | ~80 | 2 | 2 (api-client, sound) |
| chart.js | ~230 | 3 | 1 (api-client) |
| config.js | ~300 | 8 | 2 (api-client, utils) |
| modals.js | ~70 | 5 | 1 (config) |
| bot-control.js | ~40 | 2 | 3 (config, api-client, utils) |
| main.js | ~70 | 0 | 13 (todos) |
| **TOTAL** | **~1.596** | **43** | - |

**Nota:** Total de linhas é maior que o original (1.270) porque:
1. Cada módulo terá cabeçalho/comentários
2. Código será mais organizado com espaçamento
3. Melhor estruturação e documentação

---

## 🎯 Conclusão

Esta modularização **preserva 100% das funcionalidades** existentes, apenas reorganizando o código em módulos lógicos, testáveis e mantíveis.

**Nenhuma funcionalidade será perdida.**

