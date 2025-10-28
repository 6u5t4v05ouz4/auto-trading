# 🤖 Da Vinci Sniper Bot

> **Bot de Trading Cripto com Estratégia EMA + RSI + ADX**
> Interface Web Completa | Alertas Sonoros | Operações em Tempo Real

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Trading View](https://img.shields.io/badge/TradingView-Compatible-orange)

---

## 📋 **Visão Geral**

O **Da Vinci Sniper Bot** é um sistema de trading automatizado desenvolvido em Python, inspirado em estratégias profissionais do TradingView. Utiliza uma combinação poderosa de indicadores técnicos para identificar pontos de entrada e saída no mercado de criptomoedas com alta precisão.

### 🎯 **Características Principais**

- 🕐 **Monitoramento em Tempo Real**: Verifica indicadores a cada 1 minuto
- 📊 **Interface Web Completa**: Painel de controle intuitivo
- 🔊 **Alertas Sonoros**: Notificações auditivas para operações
- 💰 **Modo Demo**: Operação segura sem risco financeiro
- 📈 **Gráficos Profissionais**: Visualização de candles e indicadores
- 🔄 **Gerenciamento Automático**: Stop Loss, Take Profit e Trailing Stop
- 🎛️ **Configuração Flexível**: 25+ pares de criptomoedas disponíveis

---

## 🚀 **Funcionalidades Detalhadas**

### 📈 **Estratégia de Trading**

**Indicadores Principais:**
- **EMA Crossover**: EMA 8 cruzando EMA 21 (sinal principal)
- **RSI Filter**: RSI > 55 para LONG, RSI < 40 para SHORT
- **ADX Filter**: Força da tendência (opcional)
- **Volume Filter**: Volume acima da média (opcional)

**Gerenciamento de Risco:**
- **Stop Loss**: 0.8% automático
- **Take Profit**: 1.8% automático
- **Trailing Stop**: 0.5% dinâmico
- **Saídas Técnicas**: EMA crossunder e MACD reversão

### 🎛️ **Interface Web**

**Painel Principal:**
- **Dashboard em tempo real** com preço e PnL
- **Gráficos interativos** com LightweightCharts
- **Controle total** da operação do bot
- **Múltiplos timeframes**: 1m, 3m, 5m, 15m, 30m, 1h
- **25+ pares** disponíveis organizados por categoria

**Recursos Avançados:**
- **PnL Centralizado**: Monitoramento de lucros/prejuízos
- **Estatísticas Detalhadas**: Win rate, operações, rentabilidade
- **Logs em Tempo Real**: Registro completo de operações
- **Configuração Dinâmica**: Ajuste de parâmetros sem parar o bot

### 🔊 **Sistema de Alertas**

**Alertas Sonoros Diferenciados:**
- **📈 LONG**: Tom otimista ascendente (A4 → A5 → E6)
- **📉 SHORT**: Tom cauteloso descendente (A5 → A4 → A3)
- **🔚 EXIT**: Notificação rápida (C5 → E5 → G5)

**Controles de Áudio:**
- Toggle ligar/desligar
- Controle de volume 0-100%
- Botão de teste
- Web Audio API integrada

### 💰 **Modos de Operação**

**🎮 Modo Demo (Padrão):**
- Saldo inicial: $1,000.00
- Sem risco financeiro real
- Operações 100% simuladas
- PnL em tempo real
- Reset de saldo disponível

**💰 Modo Real:**
- Integração com Binance Futures
- Operações reais com API
- Gerenciamento de risco automático
- Validação de credenciais

---

## 🛠️ **Instalação e Configuração**

### 📋 **Pré-requisitos**

- **Python 3.8+**
- **pip** (gerenciador de pacotes Python)
- **Conta Binance** (para modo real)

### ⚙️ **Instalação**

1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/davinci-sniper-bot.git
cd davinci-sniper-bot
```

2. **Instale dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure o bot:**
```bash
# Configure seus parâmetros em bot_config.json
# Para modo real, adicione suas credenciais (opcional)
```

### 🔧 **Configuração Inicial**

**`bot_config.json`:**
```json
{
    "SYMBOL": "SOL/USDT",
    "TIMEFRAME": "5m",
    "POSITION_SIZE_USD": 15,
    "LEVERAGE": 20,
    "USE_DEMO": true,
    "DEMO_BALANCE": 1000.0,
    "RSI_LONG": 55,
    "RSI_SHORT": 40,
    "USE_VOL": false,
    "USE_ADX": true,
    "ADX_THRESH": 18
}
```

---

## 🎮 **Como Usar**

### 🚀 **Iniciando o Bot**

1. **Inicie a interface web:**
```bash
python web_interface.py
```

2. **Acesse o painel:**
```
http://127.0.0.1:5000
```

3. **Configure seus parâmetros:**
   - Escolha o par e timeframe
   - Ajuste tamanho da posição e alavancagem
   - Configure filtros de entrada
   - Defina modo (Demo/Real)

4. **Inicie o bot:**
   - Clique em "▶️ Start Bot"
   - Monitore os logs e operações
   - Acompanhe PnL em tempo real

### 📊 **Monitoramento**

**Interface Web:**
- **Header**: Preço, PnL do dia, estatísticas
- **Abas**: Chart, Open Operations, Closed Operations
- **Logs**: Registro detalhado em tempo real
- **Controles**: Iniciar/Parar, Reset, Configurações

**Logs Importantes:**
```
✅ ENTRADA LONG | Preço: $194.20 | RSI: 58.2
✅ SAÍDA LONG | Stop/TP | PnL: +1.2%
⚠️ CROSSOVER (LONG) | EMA8 > EMA21
```

---

## 📈 **Pares Disponíveis**

### 🔥 **Top Majors**
- BTC/USDT, ETH/USDT, BNB/USDT

### ⚡ **Layer 1**
- SOL/USDT, ADA/USDT, AVAX/USDT, DOT/USDT, MATIC/USDT, ATOM/USDT

### 🚀 **DeFi & Gaming**
- LINK/USDT, UNI/USDT, AAVE/USDT, SAND/USDT, MANA/USDT, AXS/USDT

### 💎 **Mid Caps**
- XRP/USDT, LTC/USDT, BCH/USDT, FIL/USDT, ALGO/USDT, VET/USDT

### 🌟 **Others**
- DOGE/USDT, SHIB/USDT, PEPE/USDT, FLOKI/USDT

---

## 📚 **Documentação Técnica**

### 🔄 **Fluxo de Operação**

1. **Coleta de Dados**: OHLCV da Binance API
2. **Cálculo de Indicadores**: EMA, RSI, MACD, ADX, Volume
3. **Análise de Sinais**: Verificação de condições de entrada
4. **Gestão de Posição**: Stop Loss, Take Profit, Trailing
5. **Saída Automática**: Baseada em indicadores ou metas

### 🎯 **Estratégia Detalhada**

**Condições de Entrada LONG:**
- EMA 8 cruza para cima de EMA 21
- RSI > 55 (força do movimento)
- Preço > EMA 21 (tendência de alta)
- Filtros opcionais (Volume, ADX) ativados

**Condições de Entrada SHORT:**
- EMA 8 cruza para baixo de EMA 21
- RSI < 40 (força do movimento)
- Preço < EMA 21 (tendência de baixa)
- Filtros opcionais (Volume, ADX) ativados

### 🛡️ **Gerenciamento de Risco**

**Proteções Automáticas:**
- **Stop Loss Fixo**: 0.8% de perda máxima
- **Take Profit Fixo**: 1.8% de lucro alvo
- **Trailing Stop**: 0.5% de arrasto de lucro
- **Cooldown**: 5 minutos entre sinais
- **Validação**: Verificação de configuração ao iniciar

---

## 📊 **Performance e Métricas**

### 📈 **Métricas Disponíveis**

**Interface Web:**
- PnL total do dia (abertas + fechadas)
- Win rate (taxa de acerto)
- Número de operações
- Saldo demo atual
- Rentabilidade percentual

**Logs Detalhados:**
- Timestamp de cada operação
- Preços de entrada e saída
- PnL individual e acumulado
- Motivo de saída (Stop/TP/Técnico)

### 🎯 **Otimizações Implementadas**

- **Logs Eficientes**: Apenas informações relevantes
- **Cache Inteligente**: Reaproveitamento de dados
- **Timeouts Configurados**: Evita travamentos
- **Error Handling**: Recuperação automática de erros
- **Rate Limiting**: Respeita limites da API

---

## 🔧 **Troubleshooting**

### ❌ **Problemas Comuns**

**Bot não inicia:**
```bash
# Verifique dependências
pip install -r requirements.txt

# Verifique configuração
python -c "import json; print(json.load(open('bot_config.json')))"
```

**Sem conexão com Binance:**
```bash
# Verifique internet
ping api.binance.com

# Verifique API keys (modo real)
python -c "import ccxt; print(ccxt.binance().fetch_status())"
```

**Gráfico não aparece:**
- Verifique console do navegador (F12)
- Recarregue a página (Ctrl+R)
- Limpe cache do navegador

**Alertas sonoros não funcionam:**
- Verifique volume do sistema
- Clique em "Testar Som"
- Confirme permissões de áudio do navegador

### 🧹 **Limpeza e Reset**

**Reset completo:**
```bash
python reset_operation.py
```

**Limpar logs:**
```bash
# Manualmente
del *.log

# Ou pela interface web
# Botão "Clear Logs"
```

---

## 🤝 **Contribuição**

### 📋 **Como Contribuir**

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Faça** commit das mudanças
4. **Push** para a branch
5. **Abra** um Pull Request

### 🎯 **Áreas para Melhoria**

- [ ] Novos indicadores técnicos
- [ ] Integração com outras exchanges
- [ ] Machine Learning para previsões
- [ ] Telegram/Discord notifications
- [ ] Backtesting avançado
- [ ] Otimização de parâmetros

---

## ⚖️ **Aviso Legal**

### 🚨 **AVISO IMPORTANTE**

**Risco Financeiro:** Trading de criptomoedas envolve risco substancial de perda. Este bot é uma ferramenta educacional e de automação. Use por sua conta e risco.

**Responsabilidade:** Os desenvolvedores não são responsáveis por perdas financeiras. Teste sempre em modo demo antes de usar com capital real.

**Regulamentação:** Verifique as leis de seu país antes de operar trading automatizado.

---

## 📞 **Suporte**

### 📧 **Contato**

- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Email**: [seu-email@exemplo.com]

### 📚 **Recursos**

- **Documentação**: [Wiki do Projeto]
- **Vídeos Tutoriais**: [Canal YouTube]
- **Comunidade**: [Discord/Telegram]

---

## 📜 **Licença**

Este projeto está licenciado sob a **Licença MIT**. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 **Agradecimentos**

- **TradingView**: Inspiração para estratégias
- **Binance**: API robusta e confiável
- **CCXT**: Excelente biblioteca de exchanges
- **Lightweight Charts**: Gráficos profissionais
- **Comunidade**: Feedback e sugestões valiosas

---

## 📊 **Status do Projeto**

✅ **Interface Web Completa**
✅ **Alertas Sonoros**
✅ **Modo Demo Funcional**
✅ **25+ Pares Suportados**
✅ **Gerenciamento de Risco**
✅ **Logs em Tempo Real**
✅ **Documentação Completa**

**Próximo Release:** Machine Learning Integration

---

<div align="center">

**🤖 Da Vinci Sniper Bot - Trading Automatizado Profissional**

*Made with ❤️ by Traders for Traders*

</div>