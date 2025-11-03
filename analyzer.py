"""
Analyzer - Analisa múltiplas moedas para identificar oportunidades de entrada
"""
import ccxt
import pandas as pd
import ta
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Lista de moedas suportadas (do dropdown)
SUPPORTED_SYMBOLS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT",
    "ADA/USDT", "AVAX/USDT", "DOT/USDT", "POL/USDT",  # MATIC foi renomeado para POL na Binance
    "LINK/USDT", "UNI/USDT", "AAVE/USDT", "XRP/USDT", "DOGE/USDT"
]

def load_entry_filters():
    """Carrega filtros de entrada do bot_config.json"""
    try:
        with open('bot_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return {
                'RSI_LONG': config.get('RSI_LONG', 60),
                'RSI_SHORT': config.get('RSI_SHORT', 35),
                'USE_VOL': config.get('USE_VOL', True),
                'USE_ADX': config.get('USE_ADX', True),
                'ADX_THRESH': config.get('ADX_THRESH', 20),
            }
    except Exception as e:
        log.warning(f"Erro ao carregar filtros, usando padrões: {e}")
        return {
            'RSI_LONG': 60,
            'RSI_SHORT': 35,
            'USE_VOL': True,
            'USE_ADX': True,
            'ADX_THRESH': 20,
        }

def calculate_indicators(df):
    """Calcula indicadores técnicos para análise"""
    if df.empty or len(df) < 50:
        return None
    
    # EMA 8 e 21
    df['ema_8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    
    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    # MACD
    df['macd_fast'] = df['close'].ewm(span=12, adjust=False).mean()
    df['macd_slow'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd_line'] = df['macd_fast'] - df['macd_slow']
    df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd_line'] - df['macd_signal']
    
    # ADX
    try:
        adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14)
        df['adx'] = adx.adx()
        df['plus_di'] = adx.adx_pos()
        df['minus_di'] = adx.adx_neg()
    except:
        df['adx'] = 0
        df['plus_di'] = 0
        df['minus_di'] = 0
    
    # Volume MA
    df['vol_ma'] = df['volume'].rolling(window=20).mean()
    
    return df

def analyze_symbol(exchange, symbol, timeframe, filters):
    """Analisa um símbolo específico e retorna sinal de entrada se houver"""
    try:
        # Busca dados OHLCV
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        
        if not ohlcv or len(ohlcv) < 50:
            return None
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Calcula indicadores
        df = calculate_indicators(df)
        if df is None:
            return None
        
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        
        # Verifica crossover/crossunder
        crossover = prev['ema_8'] <= prev['ema_21'] and last['ema_8'] > last['ema_21']
        crossunder = prev['ema_8'] >= prev['ema_21'] and last['ema_8'] < last['ema_21']
        
        # Não há sinal se não houve crossover/crossunder
        if not (crossover or crossunder):
            return None
        
        # Filtros para LONG
        long_signal = False
        long_reasons = []
        long_blocked_by = []
        
        if crossover:
            rsi_ok = last['rsi'] > filters['RSI_LONG']
            vol_ok = not filters['USE_VOL'] or (last['volume'] > last['vol_ma'] * 1.15)
            adx_ok = not filters['USE_ADX'] or (last['adx'] > filters['ADX_THRESH'])
            trend_ok = last['close'] > last['ema_21']
            
            if rsi_ok and vol_ok and adx_ok and trend_ok:
                long_signal = True
                long_reasons = [
                    f"RSI {last['rsi']:.1f} > {filters['RSI_LONG']}",
                    f"Volume {last['volume']:.0f} > {last['vol_ma']:.0f}×1.15" if filters['USE_VOL'] else "Volume: OK",
                    f"ADX {last['adx']:.1f} > {filters['ADX_THRESH']}" if filters['USE_ADX'] else "ADX: OK",
                    f"Preço {last['close']:.4f} > EMA21 {last['ema_21']:.4f}"
                ]
            else:
                if not rsi_ok:
                    long_blocked_by.append(f"RSI {last['rsi']:.1f} precisa ser > {filters['RSI_LONG']}")
                if not vol_ok:
                    long_blocked_by.append("Volume precisa estar 15% acima da média")
                if not adx_ok:
                    long_blocked_by.append(f"ADX {last['adx']:.1f} precisa ser > {filters['ADX_THRESH']}")
                if not trend_ok:
                    long_blocked_by.append(f"Preço {last['close']:.4f} precisa estar acima da EMA21 {last['ema_21']:.4f}")
        
        # Filtros para SHORT
        short_signal = False
        short_reasons = []
        short_blocked_by = []
        
        if crossunder:
            rsi_ok = last['rsi'] < filters['RSI_SHORT']
            vol_ok = not filters['USE_VOL'] or (last['volume'] > last['vol_ma'] * 1.15)
            adx_ok = not filters['USE_ADX'] or (last['adx'] > filters['ADX_THRESH'])
            trend_ok = last['close'] < last['ema_21']
            
            if rsi_ok and vol_ok and adx_ok and trend_ok:
                short_signal = True
                short_reasons = [
                    f"RSI {last['rsi']:.1f} < {filters['RSI_SHORT']}",
                    f"Volume {last['volume']:.0f} > {last['vol_ma']:.0f}×1.15" if filters['USE_VOL'] else "Volume: OK",
                    f"ADX {last['adx']:.1f} > {filters['ADX_THRESH']}" if filters['USE_ADX'] else "ADX: OK",
                    f"Preço {last['close']:.4f} < EMA21 {last['ema_21']:.4f}"
                ]
            else:
                if not rsi_ok:
                    short_blocked_by.append(f"RSI {last['rsi']:.1f} precisa ser < {filters['RSI_SHORT']}")
                if not vol_ok:
                    short_blocked_by.append("Volume precisa estar 15% acima da média")
                if not adx_ok:
                    short_blocked_by.append(f"ADX {last['adx']:.1f} precisa ser > {filters['ADX_THRESH']}")
                if not trend_ok:
                    short_blocked_by.append(f"Preço {last['close']:.4f} precisa estar abaixo da EMA21 {last['ema_21']:.4f}")
        
        # Retorna resultado se houver sinal ou se estiver próximo
        signal_type = None
        proximity_score = 0
        reasons = []
        blocked_by = []
        
        if long_signal:
            signal_type = "LONG"
            reasons = long_reasons
            proximity_score = 100
        elif short_signal:
            signal_type = "SHORT"
            reasons = short_reasons
            proximity_score = 100
        elif crossover and long_blocked_by:
            # Próximo de LONG mas bloqueado
            signal_type = "LONG (PRÓXIMO)"
            blocked_by = long_blocked_by
            # Calcula score de proximidade (quantos filtros passaram)
            passed_filters = 4 - len(long_blocked_by)
            proximity_score = (passed_filters / 4) * 100
        elif crossunder and short_blocked_by:
            # Próximo de SHORT mas bloqueado
            signal_type = "SHORT (PRÓXIMO)"
            blocked_by = short_blocked_by
            passed_filters = 4 - len(short_blocked_by)
            proximity_score = (passed_filters / 4) * 100
        
        if signal_type:
            return {
                'symbol': symbol,
                'signal': signal_type,
                'price': float(last['close']),
                'rsi': float(last['rsi']),
                'adx': float(last['adx']),
                'volume': float(last['volume']),
                'vol_ma': float(last['vol_ma']),
                'ema_8': float(last['ema_8']),
                'ema_21': float(last['ema_21']),
                'proximity_score': round(proximity_score, 1),
                'reasons': reasons,
                'blocked_by': blocked_by,
                'macd_hist': float(last['macd_hist']) if 'macd_hist' in last else 0,
            }
        
        return None
        
    except Exception as e:
        log.error(f"Erro ao analisar {symbol}: {e}")
        return None

def analyze_all_symbols(timeframe):
    """Analisa todos os símbolos suportados no timeframe especificado"""
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
            'timeout': 15000,
        })
        exchange.load_markets()
        
        filters = load_entry_filters()
        
        results = []
        
        for symbol in SUPPORTED_SYMBOLS:
            try:
                result = analyze_symbol(exchange, symbol, timeframe, filters)
                if result:
                    results.append(result)
            except Exception as e:
                log.warning(f"Erro ao processar {symbol}: {e}")
                continue
        
        # Ordena por score de proximidade (maior primeiro)
        results.sort(key=lambda x: x['proximity_score'], reverse=True)
        
        return results
        
    except Exception as e:
        log.error(f"Erro na análise geral: {e}")
        return []

