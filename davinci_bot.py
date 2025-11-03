import os
import sys
import time
import json
import logging
import numpy as np
import pandas as pd
import ta
import ccxt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ===================== CONFIGURAÇÕES =====================
load_dotenv()

# --- Exchange --- Será inicializado após carregar o config
exchange = None

# --- Carrega Configuração do Arquivo ---
def load_config():
    """Carrega configuração do arquivo JSON ou cria um novo se não existir"""
    try:
        # Tenta carregar configuração existente
        with open('bot_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Validação básica da configuração
        required_fields = ['SYMBOL', 'TIMEFRAME', 'POSITION_SIZE_USD', 'LEVERAGE']
        for field in required_fields:
            if field not in config:
                log.warning(f"Campo '{field}' não encontrado no config, usando valor padrão")

        # Validações de valores
        if config.get('POSITION_SIZE_USD', 0) <= 0:
            config['POSITION_SIZE_USD'] = 50
            log.warning("POSITION_SIZE_USD inválido, usando $50")

        if config.get('LEVERAGE', 0) <= 0:
            config['LEVERAGE'] = 10
            log.warning("LEVERAGE inválido, usando 10x")

        # Validação de símbolo
        symbol = config.get('SYMBOL', '').strip()
        if not symbol or '/' not in symbol:
            config['SYMBOL'] = 'BTC/USDT'
            log.warning("SYMBOL inválido, usando BTC/USDT")

        # Validação de timeframe
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d']
        timeframe = config.get('TIMEFRAME', '').strip()
        if timeframe not in valid_timeframes:
            config['TIMEFRAME'] = '5m'
            log.warning(f"TIMEFRAME '{timeframe}' inválido, usando 5m")

        return config
    except FileNotFoundError:
        # Arquivo não existe - cria configuração padrão
        log.info("bot_config.json não encontrado, criando arquivo de configuração padrão...")
        default_config = {
            "SYMBOL": "SOL/USDT",
            "TIMEFRAME": "5m",
            "POSITION_SIZE_USD": 15,
            "LEVERAGE": 20,
            "USE_DEMO": True,
            "DEMO_BALANCE": 1000.0,
            "RSI_LONG": 55,
            "RSI_SHORT": 40,
            "USE_VOL": False,
            "USE_ADX": True,
            "ADX_THRESH": 18,
            "SIGNAL_COOLDOWN": 300,
            "LOG_LEVEL": "INFO",
            "STOP_LOSS": 0.008,
            "TAKE_PROFIT": 0.018,
            "TRAILING_STOP": 0.005,
            "USE_FIXED_EXIT": True,
            "USE_TRAILING": True,
            "EXIT_RSI_LONG": 70,
            "EXIT_RSI_SHORT": 30,
            "USE_EXIT_RSI": False,
            "EXIT_ADX_THRESHOLD": 25,
            "USE_EXIT_ADX": False,
            "EXIT_AFTER_MINUTES": 60,
            "USE_TIME_EXIT": False,
            "EXIT_ON_VOLUME_SPIKE": True,
            "EXIT_VOLUME_MULTIPLIER": 2.0
        }

        # Salva o arquivo de configuração padrão
        try:
            with open('bot_config.json', 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            log.info("✅ bot_config.json criado com configuração padrão")
            return default_config
        except Exception as e:
            log.error(f"Erro ao criar bot_config.json: {e}")
            return default_config

    except Exception as e:
        log.error(f"Erro ao carregar configuração: {e}")
        return {
            "SYMBOL": "BTC/USDT",
            "TIMEFRAME": "5m",
            "POSITION_SIZE_USD": 50,
            "LEVERAGE": 10,
            "USE_DEMO": True,
            "DEMO_BALANCE": 1000.0,
            "RSI_LONG": 55,
            "RSI_SHORT": 40,
            "USE_VOL": False,
            "USE_ADX": False,
            "ADX_THRESH": 18,
            "STOP_LOSS": 0.008,
            "TAKE_PROFIT": 0.018,
            "TRAILING_STOP": 0.005,
            "USE_FIXED_EXIT": True,
            "USE_TRAILING": True,
            "EXIT_RSI_LONG": 70,
            "EXIT_RSI_SHORT": 30,
            "USE_EXIT_RSI": False,
            "EXIT_ADX_THRESHOLD": 25,
            "USE_EXIT_ADX": False,
            "EXIT_AFTER_MINUTES": 60,
            "USE_TIME_EXIT": False,
            "EXIT_ON_VOLUME_SPIKE": True,
            "EXIT_VOLUME_MULTIPLIER": 2.0
        }

def load_demo_balance():
    """Carrega saldo demo do arquivo JSON"""
    try:
        if os.path.exists('demo_balance.json'):
            with open('demo_balance.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('balance', 1000.0)
    except:
        pass
    return 1000.0

def save_demo_balance(balance):
    """Salva saldo demo no arquivo JSON"""
    try:
        with open('demo_balance.json', 'w', encoding='utf-8') as f:
            json.dump({'balance': balance}, f, indent=4)
        return True
    except:
        return False

def initialize_files():
    """Inicializa arquivos necessários se não existirem"""
    # Cria operations.json se não existir
    if not os.path.exists('operations.json'):
        try:
            with open('operations.json', 'w', encoding='utf-8') as f:
                json.dump({"open_operations": [], "closed_operations": []}, f, indent=4, ensure_ascii=False)
            log.info("✅ operations.json criado")
        except Exception as e:
            log.error(f"Erro ao criar operations.json: {e}")

    # Cria demo_balance.json se não existir e estiver em modo demo
    if not os.path.exists('demo_balance.json'):
        try:
            config = load_config()
            if config.get('USE_DEMO', True):
                initial_balance = config.get('DEMO_BALANCE', 1000.0)
                with open('demo_balance.json', 'w', encoding='utf-8') as f:
                    json.dump({'balance': initial_balance}, f, indent=4, ensure_ascii=False)
                log.info(f"✅ demo_balance.json criado com saldo inicial de ${initial_balance:.2f}")
        except Exception as e:
            log.error(f"Erro ao criar demo_balance.json: {e}")

# --- Estratégia ---
def reload_config():
    """Recarrega configuração do arquivo e atualiza variáveis globais"""
    global config, SYMBOL, TIMEFRAME, POSITION_SIZE_USD, LEVERAGE, USE_DEMO, DEMO_BALANCE_INITIAL
    global RSI_LONG, RSI_SHORT, USE_VOL, USE_ADX, ADX_THRESH, STOP_LOSS, TAKE_PROFIT, TRAILING_STOP
    global USE_FIXED_EXIT, USE_TRAILING, EXIT_RSI_LONG, EXIT_RSI_SHORT, USE_EXIT_RSI, EXIT_ADX_THRESHOLD
    global USE_EXIT_ADX, EXIT_AFTER_MINUTES, USE_TIME_EXIT, EXIT_ON_VOLUME_SPIKE, EXIT_VOLUME_MULTIPLIER

    config = load_config()
    SYMBOL = config.get('SYMBOL', 'BTC/USDT')
    TIMEFRAME = config.get('TIMEFRAME', '5m')  # Timeframe para candles (ex: 5m, 15m, 1h)
    POSITION_SIZE_USD = config.get('POSITION_SIZE_USD', 50)
    LEVERAGE = config.get('LEVERAGE', 10)
    USE_DEMO = config.get('USE_DEMO', True)
    DEMO_BALANCE_INITIAL = config.get('DEMO_BALANCE', 1000.0)

    # Filtros de entrada
    RSI_LONG = config.get('RSI_LONG', 55)
    RSI_SHORT = config.get('RSI_SHORT', 40)
    USE_VOL = config.get('USE_VOL', False)
    USE_ADX = config.get('USE_ADX', True)
    ADX_THRESH = config.get('ADX_THRESH', 18)

    # Filtros de saída
    STOP_LOSS = config.get('STOP_LOSS', 0.008)
    TAKE_PROFIT = config.get('TAKE_PROFIT', 0.018)
    TRAILING_STOP = config.get('TRAILING_STOP', 0.005)
    USE_FIXED_EXIT = config.get('USE_FIXED_EXIT', True)
    USE_TRAILING = config.get('USE_TRAILING', True)

    # Filtros de saída avançados
    EXIT_RSI_LONG = config.get('EXIT_RSI_LONG', 70)
    EXIT_RSI_SHORT = config.get('EXIT_RSI_SHORT', 30)
    USE_EXIT_RSI = config.get('USE_EXIT_RSI', False)
    EXIT_ADX_THRESHOLD = config.get('EXIT_ADX_THRESHOLD', 25)
    USE_EXIT_ADX = config.get('USE_EXIT_ADX', False)
    EXIT_AFTER_MINUTES = config.get('EXIT_AFTER_MINUTES', 60)
    USE_TIME_EXIT = config.get('USE_TIME_EXIT', False)
    EXIT_ON_VOLUME_SPIKE = config.get('EXIT_ON_VOLUME_SPIKE', True)
    EXIT_VOLUME_MULTIPLIER = config.get('EXIT_VOLUME_MULTIPLIER', 2.0)

# Carrega configuração inicial
config = load_config()
reload_config()
CHECK_INTERVAL = 60  # SEMPRE 60 segundos - lê indicadores a cada 1min independente do timeframe

# --- Parâmetros do Script ---
EMA_SHORT = 8
EMA_MID = 21
RSI_LEN = 9
MACD_FAST = 8
MACD_SLOW = 21
MACD_SIGNAL = 5
VOL_MULT = 1.05
USE_VWAP = False  # FILTRO VWAP REMOVIDO (não usado no TradingView)
ADX_LEN = 10
TRAIL_OFFSET = config.get('TRAILING_STOP', 0.005)  # 0.5% (TradingView: trailOffsetPerc)

# --- Filtros de Saída Adicionais ---
# Todas as variáveis de configuração são carregadas dinamicamente na função reload_config()

# --- Estado da Posição ---
in_position = False
position_side = None
entry_price = 0.0
entry_time = None
highest_price = 0.0
lowest_price = 0.0
last_candle_time = None
last_signal_time = None  # Cooldown para evitar múltiplos sinais
SIGNAL_COOLDOWN = 300  # 5 minutos em segundos

# --- Logging ---
# Configura encoding para UTF-8 no Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("davinci_bot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()

# ===================== FUNÇÕES =====================
def get_log_mode():
    """Retorna o modo de operação"""
    global USE_DEMO
    config = load_config()
    USE_DEMO = config.get('USE_DEMO', True)
    return "DEMO" if USE_DEMO else "LIVE"

def set_leverage():
    if not USE_DEMO and exchange:
        try:
            exchange.set_leverage(LEVERAGE, SYMBOL)
            log.info(f"Alavancagem definida: {LEVERAGE}x ({get_log_mode()})")
        except Exception as e:
            log.warning(f"Erro ao definir alavancagem: {e}")
    else:
        log.info(f"Alavancagem (simulada): {LEVERAGE}x ({get_log_mode()})")

def get_balance():
    if not USE_DEMO and exchange:
        try:
            balance = exchange.fetch_balance(params={'type': 'future'})
            usdt = balance['total'].get('USDT', 0)
            log.info(f"Saldo USDT ({get_log_mode()}): ${usdt:.2f}")
            return usdt
        except Exception as e:
            log.error(f"Erro ao obter saldo: {e}")
            return 0
    else:
        # Modo Demo
        demo_balance = load_demo_balance()
        log.info(f"Saldo Demo ({get_log_mode()}): ${demo_balance:.2f}")
        return demo_balance

def fetch_ohlcv():
    global exchange
    try:
        # Inicializa exchange se ainda não foi criado
        if exchange is None:
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'future'},
                'timeout': 15000,
            })
            exchange.load_markets()
        
        # Verifica timeframe válido para Binance
        valid_timeframes = exchange.timeframes
        if TIMEFRAME not in valid_timeframes:
            log.error(f"Timeframe inválido: {TIMEFRAME}. Use um de: {list(valid_timeframes.keys())[:10]}")
            return None
        
        ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)

        # Validação dos dados recebidos
        if not ohlcv or len(ohlcv) < 50:
            log.error(f"Dados insuficientes: {len(ohlcv) if ohlcv else 0} candles")
            return None

        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Validação dos intervals dos candles
        if len(df) > 1:
            last_candle = df.iloc[-1]
            second_last_candle = df.iloc[-2]
            time_diff = last_candle.name - second_last_candle.name
            
            # Converte timeframe para Timedelta (suporta m, h, d)
            try:
                if 'm' in TIMEFRAME:
                    minutes = int(TIMEFRAME.replace('m', ''))
                    expected_diff = pd.Timedelta(minutes=minutes)
                elif 'h' in TIMEFRAME:
                    hours = int(TIMEFRAME.replace('h', ''))
                    expected_diff = pd.Timedelta(hours=hours)
                elif 'd' in TIMEFRAME:
                    days = int(TIMEFRAME.replace('d', ''))
                    expected_diff = pd.Timedelta(days=days)
                else:
                    # Fallback: assume minutos
                    expected_diff = pd.Timedelta(minutes=5)
                    log.warning(f"Formato de timeframe não reconhecido: {TIMEFRAME}, usando 5min como padrão")
            except (ValueError, AttributeError) as e:
                log.warning(f"Erro ao parsear timeframe: {TIMEFRAME}, pulando validação de gap: {e}")
                expected_diff = None
            
            if expected_diff and abs(time_diff - expected_diff) > pd.Timedelta(minutes=1):
                log.warning(f"[CANDLE] Gap detectado: {time_diff} (esperado: {expected_diff})")

        return df
    except Exception as e:
        log.error(f"Erro ao buscar OHLCV: {e}")
        return None

def calculate_indicators(df):
    if len(df) < 50:
        return df  # Evita erros em dados insuficientes

    # EMA (usando cálculo manual como TradingView)
    df['ema_short'] = df['close'].ewm(span=EMA_SHORT, adjust=False).mean()
    df['ema_mid'] = df['close'].ewm(span=EMA_MID, adjust=False).mean()
    
    # RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], RSI_LEN).rsi()
    
    # MACD - Conforme TradingView: macdLine = ema(close, fast) - ema(close, slow)
    macd_fast_ema = df['close'].ewm(span=MACD_FAST, adjust=False).mean()
    macd_slow_ema = df['close'].ewm(span=MACD_SLOW, adjust=False).mean()
    macd_line = macd_fast_ema - macd_slow_ema
    macd_signal = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
    df['macd_hist'] = macd_line - macd_signal  # Histogram
    df['macd_line'] = macd_line
    df['macd_signal'] = macd_signal
    
    # ADX
    try:
        adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], ADX_LEN)
        df['adx'] = adx.adx()
        df['plus_di'] = adx.adx_pos()
        df['minus_di'] = adx.adx_neg()
    except:
        # Fallback se ADX não disponível
        df['adx'] = 0
        df['plus_di'] = 0
        df['minus_di'] = 0
    
    # Volume MA - implementação manual
    df['vol_ma'] = df['volume'].rolling(window=20).mean()
    df['high_vol'] = df['volume'] > df['vol_ma'] * VOL_MULT

    # VWAP Diário
    daily = df.resample('1D').agg({
        'open': 'first', 'high': 'max', 'low': 'min',
        'close': 'last', 'volume': 'sum'
    })
    if not daily.empty and daily['volume'].sum() > 0:
        cum_vol = daily['volume'].cumsum()
        cum_vwap = (daily['close'] * daily['volume']).cumsum()
        daily_vwap = cum_vwap / cum_vol
        df['daily_vwap'] = daily_vwap.reindex(df.index, method='ffill').ffill()
    else:
        df['daily_vwap'] = df['close']

    return df

def is_new_candle(df):
    global last_candle_time
    try:
        if df.empty:
            return False

        # Pega o timestamp do último candle
        last_timestamp = df.index[-1]

        # Converte para UTC para evitar problemas de timezone
        if last_timestamp.tz is None:
            last_timestamp = last_timestamp.tz_localize('UTC')
        else:
            last_timestamp = last_timestamp.tz_convert('UTC')

        # Usa o timeframe dinâmico do config
        if TIMEFRAME.endswith('m'):
            try:
                minutes = int(TIMEFRAME.replace('m', ''))
            except ValueError:
                log.error(f"Erro ao parsear timeframe '{TIMEFRAME}' para minutos")
                return False
            # Calcula o início do candle (floor por minutos)
            current_candle = last_timestamp.replace(
                minute=(last_timestamp.minute // minutes) * minutes,
                second=0,
                microsecond=0
            )
        elif TIMEFRAME.endswith('h'):
            try:
                hours = int(TIMEFRAME.replace('h', ''))
            except ValueError:
                log.error(f"Erro ao parsear timeframe '{TIMEFRAME}' para horas")
                return False
            # Calcula o início do candle (floor por horas)
            current_candle = last_timestamp.replace(
                minute=0,
                second=0,
                microsecond=0
            )
            if hours > 1:
                current_candle = current_candle.replace(
                    hour=(last_timestamp.hour // hours) * hours
                )
        else:
            # Fallback para 1 minuto
            current_candle = last_timestamp.replace(
                minute=last_timestamp.minute,
                second=0,
                microsecond=0
            )

        # Verifica se é um novo candle
        if last_candle_time is None or current_candle > last_candle_time:
            last_candle_time = current_candle
            return True

        return False
    except Exception as e:
        log.error(f"Erro em is_new_candle: {e}")
        # Em caso de erro, assume que é novo candle se não houver referência
        if last_candle_time is None:
            last_candle_time = df.index[-1].replace(second=0, microsecond=0)
            return True
        return False

def generate_signal(df):
    global last_signal_time

    if len(df) < 50:
        return None, None

    # Verifica cooldown de sinais
    current_time = datetime.now()
    if last_signal_time and (current_time - last_signal_time).total_seconds() < SIGNAL_COOLDOWN:
        return None, None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Crossover/crossunder das EMAs
    crossover = prev['ema_short'] <= prev['ema_mid'] and last['ema_short'] > last['ema_mid']
    crossunder = prev['ema_short'] >= prev['ema_mid'] and last['ema_short'] < last['ema_mid']

    # Filtros opcionais (do TradingView)
    vol_ok = last['high_vol'] if USE_VOL else True
    adx_ok = last['adx'] > ADX_THRESH if USE_ADX else True

    # Filtro de tendência (do TradingView: upTrendLong / downTrendShort)
    upTrendLong = last['close'] > last['ema_mid']
    downTrendShort = last['close'] < last['ema_mid']

    # Filtro de RSI
    rsi_ok_long = last['rsi'] > RSI_LONG  # RSI > 55 para LONG
    rsi_ok_short = last['rsi'] < RSI_SHORT  # RSI < 40 para SHORT

    # Log apenas quando há crossover/crossunder real
    if crossover or crossunder:
        log.info(f"[SINAL] CROSSOVER={crossover} CROSSUNDER={crossunder} | RSI={last['rsi']:.1f} | Vol={vol_ok} | ADX={adx_ok}")

    # Sinais conforme TradingView com RSI
    long_signal = crossover and vol_ok and adx_ok and upTrendLong and rsi_ok_long
    short_signal = crossunder and vol_ok and adx_ok and downTrendShort and rsi_ok_short

    # Debug apenas quando sinal é bloqueado por filtros
    if (crossover or crossunder) and not (long_signal or short_signal):
        log.info(f"[BLOQUEADO] Sinal filtrado | RSI={last['rsi']:.1f} | Vol={vol_ok} | ADX={adx_ok}")

    # Atualiza timestamp do último sinal se houver sinal válido
    if long_signal or short_signal:
        last_signal_time = current_time

    return long_signal, short_signal

def save_operation_to_file(operation):
    """Salva operação no arquivo operations.json"""
    try:
        if os.path.exists('operations.json'):
            with open('operations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"open_operations": [], "closed_operations": []}
        
        if operation.get('status') == 'open':
            data['open_operations'].append(operation)
        else:
            # Remove da lista aberta se existir
            operation_id = operation.get('id')
            if operation_id:
                # Remove por ID (mais preciso)
                data['open_operations'] = [op for op in data['open_operations'] if op.get('id') != operation_id]
            else:
                # Fallback: Remove por símbolo, lado e preço de entrada (caso ID não esteja disponível)
                data['open_operations'] = [
                    op for op in data['open_operations'] 
                    if not (op.get('symbol') == operation.get('symbol') and 
                           op.get('side') == operation.get('side') and
                           abs(op.get('entry_price', 0) - operation.get('entry_price', 0)) < 0.01)
                ]
            data['closed_operations'].append(operation)
        
        with open('operations.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log.error(f"Erro ao salvar operação: {e}")

def enter_position(side):
    global in_position, position_side, entry_price, entry_time, highest_price, lowest_price
    try:
        ticker = exchange.fetch_ticker(SYMBOL)
        price = ticker['last']
        amount = (POSITION_SIZE_USD * LEVERAGE) / price
        
        # Apenas executa ordem real se NÃO estiver em modo Demo
        order = None
        if not USE_DEMO:
            try:
                order = exchange.create_order(
                    symbol=SYMBOL,
                    type='market',
                    side=side,
                    amount=exchange.amount_to_precision(SYMBOL, amount),
                    params={'reduceOnly': False}
                )
            except Exception as e:
                log.error(f"Erro ao criar ordem: {e}")
                return None
        else:
            log.info(f"[DEMO] Simulando entrada - Nenhuma ordem real executada")
        
        entry_price = price
        entry_time = datetime.now()
        highest_price = price
        lowest_price = price
        in_position = True
        position_side = 'long' if side == 'buy' else 'short'
        
        # Salva operação aberta
        operation = {
            "id": int(time.time() * 1000),  # ID único
            "symbol": SYMBOL,
            "side": position_side.upper(),
            "entry_price": float(price),
            "current_price": float(price),
            "quantity": float(amount),
            "leverage": LEVERAGE,
            "entry_time": entry_time.strftime("%H:%M"),
            "entry_date": entry_time.strftime("%Y-%m-%d"),
            "pnl": 0.0,
            "pnl_percent": 0.0,
            "status": "open"
        }
        save_operation_to_file(operation)
        
        log.info(f"ENTRADA {position_side.upper()} ({get_log_mode()}) | Preço: ${price:.2f} | Qtd: {amount:.6f}")
        return order
    except Exception as e:
        log.error(f"Erro ao entrar {side}: {e}")
        return None

def exit_position(reason="Manual"):
    global in_position, position_side, entry_price, entry_time
    if not in_position:
        return None
    try:
        exit_price = 0.0
        pnl = 0.0
        pnl_usd = 0.0
        amount = 0.0

        if not USE_DEMO:
            # Modo REAL - executa ordem na Binance
            side = 'sell' if position_side == 'long' else 'buy'
            positions = exchange.fetch_positions([SYMBOL])
            pos = next((p for p in positions if p['symbol'] == SYMBOL and float(p['contracts']) > 0), None)

            if not pos:
                log.warning("Nenhuma posição aberta encontrada.")
                in_position = False
                return None

            amount = float(pos['contracts'])
            order = exchange.create_order(
                symbol=SYMBOL,
                type='market',
                side=side,
                amount=exchange.amount_to_precision(SYMBOL, amount),
                params={'reduceOnly': True}
            )
            exit_price = exchange.fetch_ticker(SYMBOL)['last']
        else:
            # Modo DEMO - simulação
            ticker = exchange.fetch_ticker(SYMBOL) if exchange else {'last': entry_price}
            exit_price = ticker['last']
            # Busca quantidade da operação aberta
            if os.path.exists('operations.json'):
                try:
                    with open('operations.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for op in data['open_operations']:
                            if op.get('status') == 'open' and op.get('symbol') == SYMBOL:
                                amount = float(op.get('quantity', 0))
                                break
                except:
                    amount = (POSITION_SIZE_USD * LEVERAGE) / entry_price

        # Calcula PnL
        pnl = (exit_price - entry_price) / entry_price * 100 if position_side == 'long' else (entry_price - exit_price) / entry_price * 100
        pnl_usd = ((exit_price - entry_price) * amount) if position_side == 'long' else ((entry_price - exit_price) * amount)

        # Atualiza saldo demo se necessário
        if USE_DEMO and pnl_usd != 0:
            current_balance = load_demo_balance()
            new_balance = current_balance + pnl_usd
            save_demo_balance(new_balance)
            log.info(f"[DEMO] Saldo atualizado: ${new_balance:.2f} (PnL: ${pnl_usd:+.2f})")

        entry_time_str = entry_time.strftime("%H:%M") if entry_time else datetime.now().strftime("%H:%M")
        exit_time_str = datetime.now().strftime("%H:%M")

        # Calcula duração
        duration_min = (datetime.now() - entry_time).total_seconds() / 60 if entry_time else 0
        duration_str = f"{int(duration_min)}min" if duration_min > 0 else "0min"

        # Busca o ID da operação aberta para poder removê-la corretamente
        operation_id = None
        if os.path.exists('operations.json'):
            try:
                with open('operations.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for op in data.get('open_operations', []):
                        if (op.get('status') == 'open' and 
                            op.get('symbol') == SYMBOL and 
                            op.get('side') == position_side.upper() and
                            abs(op.get('entry_price', 0) - entry_price) < 0.01):  # Mesmo preço de entrada
                            operation_id = op.get('id')
                            break
            except:
                pass

        # Salva operação fechada
        operation = {
            "id": operation_id,  # Inclui ID para poder remover da lista aberta
            "symbol": SYMBOL,
            "side": position_side.upper(),
            "entry_price": float(entry_price),
            "exit_price": float(exit_price),
            "quantity": float(amount),
            "leverage": LEVERAGE,
            "entry_time": entry_time_str,
            "exit_time": exit_time_str,
            "duration": duration_str,
            "pnl": float(pnl_usd),
            "pnl_percent": float(pnl),
            "reason": reason,
            "status": "closed"
        }
        save_operation_to_file(operation)

        log.info(f"SAÍDA {position_side.upper()} ({get_log_mode()}) | {reason} | PnL: {pnl:+.2f}% | Preço: ${exit_price:.2f}")
        in_position = False
        position_side = None
        entry_price = 0.0
        entry_time = None
        return {"success": True, "pnl": pnl_usd}
    except Exception as e:
        log.error(f"Erro ao sair da posição: {e}")
        return None

def update_open_operations_pnl():
    """Atualiza PnL das operações abertas em tempo real"""
    try:
        if not os.path.exists('operations.json'):
            return

        with open('operations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        updated = False
        for op in data['open_operations']:
            try:
                current_price = 0.0
                if not USE_DEMO and exchange:
                    # Modo REAL - busca preço da Binance
                    ticker = exchange.fetch_ticker(op['symbol'])
                    current_price = ticker['last']
                else:
                    # Modo DEMO - busca preço simulado
                    try:
                        # Inicializa exchange apenas para dados de mercado
                        temp_exchange = ccxt.binance({
                            'enableRateLimit': True,
                            'options': {'defaultType': 'future'},
                            'timeout': 10000
                        })
                        ticker = temp_exchange.fetch_ticker(op['symbol'])
                        current_price = ticker['last']
                    except:
                        # Fallback: usa último preço salvo
                        current_price = op.get('current_price', op['entry_price'])

                # Calcula PnL
                if op['side'] == 'LONG':
                    pnl = (current_price - op['entry_price']) / op['entry_price'] * 100
                    pnl_usd = (current_price - op['entry_price']) * op['quantity']
                else:  # SHORT
                    pnl = (op['entry_price'] - current_price) / op['entry_price'] * 100
                    pnl_usd = (op['entry_price'] - current_price) * op['quantity']

                op['current_price'] = float(current_price)
                op['pnl'] = float(pnl_usd)
                op['pnl_percent'] = float(pnl)
                updated = True
            except Exception as e:
                log.debug(f"Erro ao atualizar PnL da operação: {e}")
                pass

        if updated:
            with open('operations.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log.debug(f"Erro em update_open_operations_pnl: {e}")
        pass  # Silently fail

def cleanup_open_operations():
    """Limpa operações abertas ao iniciar o bot para evitar estado corrompido"""
    global in_position, position_side, entry_price, entry_time

    try:
        if os.path.exists('operations.json'):
            with open('operations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            open_ops = data.get('open_operations', [])
            if open_ops:
                log.warning(f"Encontradas {len(open_ops)} operações abertas ao iniciar. Limpando estado...")

                # Move todas para operações fechadas
                for op in open_ops:
                    op['status'] = 'closed'
                    op['reason'] = 'Cleanup Bot Restart'
                    op['exit_time'] = datetime.now().strftime('%H:%M')
                    op['exit_price'] = op.get('current_price', op.get('entry_price'))

                    # Calcula PnL final
                    if op['side'] == 'LONG':
                        pnl = (op['exit_price'] - op['entry_price']) / op['entry_price'] * 100
                        pnl_usd = (op['exit_price'] - op['entry_price']) * op['quantity']
                    else:
                        pnl = (op['entry_price'] - op['exit_price']) / op['entry_price'] * 100
                        pnl_usd = (op['entry_price'] - op['exit_price']) * op['quantity']

                    op['pnl'] = float(pnl_usd)
                    op['pnl_percent'] = float(pnl)

                    data['closed_operations'].append(op)
                    log.info(f"Operação limpa: {op['side']} {op['symbol']} | PnL: ${pnl_usd:+.2f} ({pnl:+.2f}%)")

                # Limpa operações abertas
                data['open_operations'] = []

                # Salva arquivo atualizado
                with open('operations.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                log.info("Estado das operações limpo com sucesso!")

        # Reseta estado global
        in_position = False
        position_side = None
        entry_price = 0.0
        entry_time = None
        highest_price = 0.0
        lowest_price = 0.0

    except Exception as e:
        log.error(f"Erro ao limpar operações abertas: {e}")

def check_exit_conditions(df):
    if not in_position:
        return

    last = df.iloc[-1]
    current_price = last['close']

    global highest_price, lowest_price

    if position_side == 'long':
        highest_price = max(highest_price, last['high'])

        # Calcula thresholds para debug
        stop_loss_price = entry_price * (1 - STOP_LOSS)
        take_profit_price = entry_price * (1 + TAKE_PROFIT)
        trailing_stop_price = highest_price * (1 - TRAIL_OFFSET)

        # Logs detalhados das condições
        should_exit = False
        exit_reasons = []

        if USE_FIXED_EXIT:
            if current_price <= stop_loss_price:
                should_exit = True
                exit_reasons.append(f"Stop Loss: ${current_price:.2f} <= ${stop_loss_price:.2f}")
            if current_price >= take_profit_price:
                should_exit = True
                exit_reasons.append(f"Take Profit: ${current_price:.2f} >= ${take_profit_price:.2f}")

        if USE_TRAILING:
            if current_price <= trailing_stop_price:
                should_exit = True
                exit_reasons.append(f"Trailing Stop: ${current_price:.2f} <= ${trailing_stop_price:.2f}")

        # EMA Crossunder - mais conservador: só fecha se confirmado
        if last['ema_short'] < last['ema_mid']:
            # Só fecha por crossunder se já está em lucro ou perto do TP
            if current_price >= entry_price * 1.01:  # Pelo menos 1% de lucro
                should_exit = True
                exit_reasons.append(f"EMA Crossunder: {last['ema_short']:.2f} < {last['ema_mid']:.2f}")
        
        # MACD Negativo - mais inteligente: não fecha imediatamente, precisa confirmação
        # Só fecha se MACD negativo E (preço abaixo do pico OU perto do trailing stop)
        if last['macd_hist'] < 0:
            # Calcula drawdown do pico
            drawdown_from_peak = (highest_price - current_price) / highest_price if highest_price > entry_price else 0
            # Só fecha se: MACD negativo E (preço recuou do pico OU está abaixo do entry com loss)
            macd_exit_threshold = TRAILING_STOP * 2  # Permite um pouco mais de movimento
            
            if (current_price < highest_price * (1 - macd_exit_threshold) or  # Recuou do pico
                current_price < entry_price * 0.995):  # Ou está em pequena perda
                should_exit = True
                exit_reasons.append(f"MACD Negativo + Confirmação: {last['macd_hist']:.4f}")
            # Caso contrário, ignora MACD negativo se ainda está subindo/congelado próximo ao pico

        # Filtro RSI de saída
        if USE_EXIT_RSI and last['rsi'] >= EXIT_RSI_LONG:
            should_exit = True
            exit_reasons.append(f"RSI Sobrecompra: {last['rsi']:.1f} >= {EXIT_RSI_LONG}")

        # Filtro ADX de saída (força da tendência diminuindo)
        if USE_EXIT_ADX and last['adx'] < EXIT_ADX_THRESHOLD:
            should_exit = True
            exit_reasons.append(f"ADX Fraco: {last['adx']:.1f} < {EXIT_ADX_THRESHOLD}")

        # Filtro temporal (tempo máximo em posição)
        if USE_TIME_EXIT and entry_time:
            duration_minutes = (datetime.now() - entry_time).total_seconds() / 60
            if duration_minutes >= EXIT_AFTER_MINUTES:
                should_exit = True
                exit_reasons.append(f"Timeout: {duration_minutes:.0f}min >= {EXIT_AFTER_MINUTES}min")

        # Filtro de volume spike (exaustão)
        if EXIT_ON_VOLUME_SPIKE:
            volume_spike = last['volume'] > last['vol_ma'] * EXIT_VOLUME_MULTIPLIER
            if volume_spike:
                should_exit = True
                exit_reasons.append(f"Volume Spike: {last['volume']:.0f} > {last['vol_ma'] * EXIT_VOLUME_MULTIPLIER:.0f}")

        # Log das condições (apenas se houver interesse ou se for sair)
        if should_exit or int(time.time()) % 300 == 0:  # A cada 5 minutos também loga
            log.info(f"[CHECK] LONG | Entry: ${entry_price:.2f} | Current: ${current_price:.2f} | PnL: ${((current_price - entry_price) * (POSITION_SIZE_USD * LEVERAGE / entry_price)):+.2f}")
            log.info(f"[CHECK] Stop: ${stop_loss_price:.2f} | TP: ${take_profit_price:.2f} | Trail: ${trailing_stop_price:.2f} | Highest: ${highest_price:.2f}")
            if USE_EXIT_RSI:
                log.info(f"[CHECK] RSI: {last['rsi']:.1f} | Exit_RSI: {EXIT_RSI_LONG}")
            if USE_EXIT_ADX:
                log.info(f"[CHECK] ADX: {last['adx']:.1f} | Exit_ADX: {EXIT_ADX_THRESHOLD}")
            if USE_TIME_EXIT and entry_time:
                duration_minutes = (datetime.now() - entry_time).total_seconds() / 60
                log.info(f"[CHECK] Tempo: {duration_minutes:.0f}min / {EXIT_AFTER_MINUTES}min")

        if should_exit:
            reason = " | ".join(exit_reasons)
            log.warning(f"[SAÍDA LONG] {reason}")
            exit_position(reason=reason)

    elif position_side == 'short':
        lowest_price = min(lowest_price, last['low'])

        # Calcula thresholds para debug
        stop_loss_price = entry_price * (1 + STOP_LOSS)
        take_profit_price = entry_price * (1 - TAKE_PROFIT)
        trailing_stop_price = lowest_price * (1 + TRAIL_OFFSET)

        # Logs detalhados das condições
        should_exit = False
        exit_reasons = []

        if USE_FIXED_EXIT:
            if current_price >= stop_loss_price:
                should_exit = True
                exit_reasons.append(f"Stop Loss: ${current_price:.2f} >= ${stop_loss_price:.2f}")
            if current_price <= take_profit_price:
                should_exit = True
                exit_reasons.append(f"Take Profit: ${current_price:.2f} <= ${take_profit_price:.2f}")

        if USE_TRAILING:
            if current_price >= trailing_stop_price:
                should_exit = True
                exit_reasons.append(f"Trailing Stop: ${current_price:.2f} >= ${trailing_stop_price:.2f}")

        # EMA Crossover - mais conservador: só fecha se confirmado
        if last['ema_short'] > last['ema_mid']:
            # Só fecha por crossover se já está em lucro ou perto do TP
            if current_price <= entry_price * 0.99:  # Pelo menos 1% de lucro
                should_exit = True
                exit_reasons.append(f"EMA Crossover: {last['ema_short']:.2f} > {last['ema_mid']:.2f}")
        
        # MACD Positivo - mais inteligente: não fecha imediatamente, precisa confirmação
        # Só fecha se MACD positivo E (preço acima do mínimo OU perto do trailing stop)
        if last['macd_hist'] > 0:
            # Calcula recuperação do mínimo
            recovery_from_low = (current_price - lowest_price) / lowest_price if lowest_price < entry_price else 0
            # Só fecha se: MACD positivo E (preço subiu do mínimo OU está acima do entry com loss)
            macd_exit_threshold = TRAILING_STOP * 2  # Permite um pouco mais de movimento
            
            if (current_price > lowest_price * (1 + macd_exit_threshold) or  # Recuperou do mínimo
                current_price > entry_price * 1.005):  # Ou está em pequeno lucro
                should_exit = True
                exit_reasons.append(f"MACD Positivo + Confirmação: {last['macd_hist']:.4f}")
            # Caso contrário, ignora MACD positivo se ainda está descendo/congelado próximo ao mínimo

        # Filtro RSI de saída
        if USE_EXIT_RSI and last['rsi'] <= EXIT_RSI_SHORT:
            should_exit = True
            exit_reasons.append(f"RSI Sobrevenda: {last['rsi']:.1f} <= {EXIT_RSI_SHORT}")

        # Filtro ADX de saída (força da tendência diminuindo)
        if USE_EXIT_ADX and last['adx'] < EXIT_ADX_THRESHOLD:
            should_exit = True
            exit_reasons.append(f"ADX Fraco: {last['adx']:.1f} < {EXIT_ADX_THRESHOLD}")

        # Filtro temporal (tempo máximo em posição)
        if USE_TIME_EXIT and entry_time:
            duration_minutes = (datetime.now() - entry_time).total_seconds() / 60
            if duration_minutes >= EXIT_AFTER_MINUTES:
                should_exit = True
                exit_reasons.append(f"Timeout: {duration_minutes:.0f}min >= {EXIT_AFTER_MINUTES}min")

        # Filtro de volume spike (exaustão)
        if EXIT_ON_VOLUME_SPIKE:
            volume_spike = last['volume'] > last['vol_ma'] * EXIT_VOLUME_MULTIPLIER
            if volume_spike:
                should_exit = True
                exit_reasons.append(f"Volume Spike: {last['volume']:.0f} > {last['vol_ma'] * EXIT_VOLUME_MULTIPLIER:.0f}")

        # Log das condições (apenas se houver interesse ou se for sair)
        if should_exit or int(time.time()) % 300 == 0:  # A cada 5 minutos também loga
            log.info(f"[CHECK] SHORT | Entry: ${entry_price:.2f} | Current: ${current_price:.2f} | PnL: ${((entry_price - current_price) * (POSITION_SIZE_USD * LEVERAGE / entry_price)):+.2f}")
            log.info(f"[CHECK] Stop: ${stop_loss_price:.2f} | TP: ${take_profit_price:.2f} | Trail: ${trailing_stop_price:.2f} | Lowest: ${lowest_price:.2f}")
            if USE_EXIT_RSI:
                log.info(f"[CHECK] RSI: {last['rsi']:.1f} | Exit_RSI: {EXIT_RSI_SHORT}")
            if USE_EXIT_ADX:
                log.info(f"[CHECK] ADX: {last['adx']:.1f} | Exit_ADX: {EXIT_ADX_THRESHOLD}")
            if USE_TIME_EXIT and entry_time:
                duration_minutes = (datetime.now() - entry_time).total_seconds() / 60
                log.info(f"[CHECK] Tempo: {duration_minutes:.0f}min / {EXIT_AFTER_MINUTES}min")

        if should_exit:
            reason = " | ".join(exit_reasons)
            log.warning(f"[SAÍDA SHORT] {reason}")
            exit_position(reason=reason)

# ===================== LOOP PRINCIPAL =====================
def main():
    log.info(f"DA VINCI SNIPER BOT INICIADO ({get_log_mode()})")

    # Inicializa arquivos necessários
    initialize_files()

    log.info(f"Configuração: {SYMBOL} | Timeframe: {TIMEFRAME} | Tamanho: ${POSITION_SIZE_USD} | Alavancagem: {LEVERAGE}x")

    # Log dos filtros ativos
    log.info(f"Filtros ENTRADA: Volume={USE_VOL} | ADX={USE_ADX} | RSI Long={RSI_LONG} | RSI Short={RSI_SHORT}")
    log.info(f"Filtros SAÍDA: Stop Loss={STOP_LOSS:.1%} | Take Profit={TAKE_PROFIT:.1%} | Trailing={TRAIL_OFFSET:.1%}")
    log.info(f"Saída RSI: {USE_EXIT_RSI} (Long:{EXIT_RSI_LONG} Short:{EXIT_RSI_SHORT}) | Saída ADX: {USE_EXIT_ADX} ({EXIT_ADX_THRESHOLD})")
    log.info(f"Saída Tempo: {USE_TIME_EXIT} ({EXIT_AFTER_MINUTES}min) | Volume Spike: {EXIT_ON_VOLUME_SPIKE} ({EXIT_VOLUME_MULTIPLIER}x)")

    # Verifica e limpa operações abertas ao iniciar
    cleanup_open_operations()

    set_leverage()
    get_balance()

    while True:
        try:
            # Recarrega configuração para pegar mudanças da interface
            reload_config()

            df = fetch_ohlcv()
            if df is None or len(df) == 0:
                time.sleep(CHECK_INTERVAL)
                continue

            df = calculate_indicators(df)

            # VERIFICAÇÃO A CADA 1 MINUTO
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 2 else df.iloc[-1]
            last_price = last['close']

            is_new = is_new_candle(df)
            long_sig, short_sig = generate_signal(df)
            crossover = prev['ema_short'] <= prev['ema_mid'] and last['ema_short'] > last['ema_mid']
            crossunder = prev['ema_short'] >= prev['ema_mid'] and last['ema_short'] < last['ema_mid']

            # Log a cada minuto - sempre mostra status completo para monitoramento
            status = f"POSICAO: {position_side.upper()} PnL: " if in_position else "SEM POSICAO"
            if in_position and os.path.exists('operations.json'):
                try:
                    with open('operations.json', 'r') as f:
                        data = json.load(f)
                        for op in data.get('open_operations', []):
                            if op.get('symbol') == SYMBOL:
                                status += f"${op.get('pnl', 0):+.2f} ({op.get('pnl_percent', 0):+.2f}%)"
                                break
                except:
                    pass

            timestamp = datetime.now().strftime('%H:%M:%S')
            log_line = f"[{timestamp}] {SYMBOL} ({TIMEFRAME}) | {status} | ${last_price:.2f}"
            log_line += f" | EMA8={last['ema_short']:.2f} EMA21={last['ema_mid']:.2f}"
            log_line += f" | RSI={last['rsi']:.1f} | ADX={last['adx']:.1f}"

            if is_new:
                log_line += " | [NOVO CANDLE]"

            log.info(log_line)

            # Logs apenas para eventos importantes
            if crossover:
                log.warning(f"*** CROSSOVER (LONG) *** EMA8 > EMA21 | Preço: ${last_price:.2f}")
            if crossunder:
                log.warning(f"*** CROSSUNDER (SHORT) *** EMA8 < EMA21 | Preço: ${last_price:.2f}")

            if long_sig:
                log.warning(f">>> ENTRADA LONG <<< Preço: ${last_price:.2f} | RSI: {last['rsi']:.1f}")
                if in_position:
                    log.info("--- IGNORADO: Posicao ativa ---")

            if short_sig:
                log.warning(f">>> ENTRADA SHORT <<< Preço: ${last_price:.2f} | RSI: {last['rsi']:.1f}")
                if in_position:
                    log.info("--- IGNORADO: Posicao ativa ---")

            # Entra em posição quando detecta sinal
            if long_sig and not in_position:
                enter_position('buy')
            elif short_sig and not in_position:
                enter_position('sell')

            check_exit_conditions(df)

            # Atualiza PnL das operações abertas
            update_open_operations_pnl()

        except Exception as e:
            log.error(f"Erro crítico no loop: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()