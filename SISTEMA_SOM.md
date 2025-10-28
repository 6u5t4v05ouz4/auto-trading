# 🔔 Sistema de Alertas Sonoros - Da Vinci Bot

## 📋 **Visão Geral**

Sistema completo de alertas sonoros para notificar quando o bot realiza operações, permitindo monitoramento sem precisar olhar a tela constantemente.

## 🎵 **Tipos de Alertas Sonoros**

### **1. Entrada LONG** 📈
- **Som**: Tom otimista ascendente (A4 → A5 → E6)
- **Frequências**: 440Hz → 880Hz → 1320Hz
- **Duração**: 300ms
- **Significado**: Bot entrou em posição de compra

### **2. Entrada SHORT** 📉
- **Som**: Tom cauteloso descendente (A5 → A4 → A3)
- **Frequências**: 880Hz → 440Hz → 220Hz
- **Duração**: 300ms
- **Significado**: Bot entrou em posição de venda

### **3. Saída de Posição** 🔚
- **Som**: Notificação rápida (C5 → E5 → G5)
- **Frequências**: 523Hz → 659Hz → 784Hz
- **Duração**: 100ms
- **Significado**: Bot fechou operação

## 🎛️ **Controles na Interface**

### **Localização**: Sidebar do painel lateral

### **Componentes**:

#### **1. Toggle de Ativação/Desativação**
- **Função**: Liga/desliga todos os alertas sonoros
- **Visual**: Interruptor deslizante azul
- **Padrão**: Ativado

#### **2. Controle de Volume**
- **Tipo**: Slider deslizante (0% - 100%)
- **Padrão**: 50%
- **Visual**: Barra progressiva azul
- **Feedback**: Percentual exibido em tempo real

#### **3. Botão de Teste**
- **Função**: Reproduz sequência dos 3 sons
- **Sequência**: LONG → SHORT → EXIT (com 400ms de intervalo)
- **Propósito**: Verificar funcionamento e volume

## 🔧 **Tecnologia**

### **Web Audio API**
- Geração de sons programaticamente (sem necessidade de arquivos)
- Síntese de áudio em tempo real
- Compatibilidade: Chrome, Firefox, Safari, Edge

### **Características Técnicas**
- **Codec**: Sintetizado (sem perdas)
- **Latência**: < 10ms
- **Volume máximo**: 20% do sistema
- **Envelope ADSR**: Attack → Decay → Sustain → Release

## 📱 **Como Usar**

### **1. Ativação**
- O sistema vem ativado por padrão
- Use o toggle para ligar/desligar conforme necessário

### **2. Ajuste de Volume**
- Arraste o slider para ajustar o volume
- O ajuste é salvo durante a sessão

### **3. Teste**
- Clique em "Testar Som" para verificar os alertas
- Útil para confirmar que o áudio está funcionando

### **4. Monitoramento**
- Deixe o bot rodando em segundo plano
- Os alertas sonoros notificarão cada operação
- Combine com notificações visuais da interface

## ⚙️ **Configurações**

### **Configurações Padrão**
```javascript
soundEnabled: true      // Alertas ativos
volumeLevel: 0.5        // 50% do volume máximo
maxVolume: 0.2          // 20% do volume do sistema
```

### **Personalização**
- Frequências podem ser ajustadas no código
- Padrões sonoros podem ser customizados
- Novos tipos de alertas podem ser adicionados

## 🎯 **Casos de Uso**

### **1. Monitoramento Passivo**
- Deixe o bot rodando enquanto faz outras atividades
- Os sons alertarão quando há operações
- Não precisa ficar verificando a tela constantemente

### **2. Trading Noturno**
- Configure volume baixo para não perturbar
- Mantenha-se informado sobre atividades durante a noite
- Desative se necessário para dormir

### **3. Backtesting**
- Teste estratégias com feedback auditivo
- Identifique padrões de entrada/saída pelos sons
- Ajuste configurações baseado na frequência de alertas

## 🔇 **Solução de Problemas**

### **Som Não Toca**
1. Verifique se o toggle está ativado
2. Teste com o botão "Testar Som"
3. Verifique o volume do sistema
4. Confirme permissões de áudio do navegador

### **Volume Muito Baixo/Alto**
1. Ajuste o slider de volume na interface
2. Verifique o volume master do sistema
3. Teste diferentes níveis (10%, 50%, 90%)

### **Sons Cortados**
- Normalmente é uma limitação do navegador
- Recarregue a página se persistir
- Evite múltiplas abas com o bot

## 📈 **Benefícios**

- **Monitoramento mãos-livres**: Fique informado sem olhar a tela
- **Reação rápida**: Identifique operações imediatamente
- **Redução de estresse**: Menos necessidade de verificação constante
- **Feedback multi-sensorial**: Combina visual e auditivo
- **Personalização**: Ajuste volume e ativação conforme preferência

---

**Status**: ✅ Sistema implementado e funcional