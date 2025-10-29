import os
import json
import threading
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CONFIG_FILE = 'bot_config.json'

def load_config():
    """Carrega configuração do arquivo JSON ou usa padrão se não existir"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Retorna configuração padrão compatível com a criada pelo bot
    return {
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
    demo_file = 'demo_balance.json'
    if os.path.exists(demo_file):
        try:
            with open(demo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('balance', 1000.0)
        except:
            pass
    return 1000.0  # Saldo inicial padrão

def save_demo_balance(balance):
    """Salva saldo demo no arquivo JSON"""
    demo_file = 'demo_balance.json'
    try:
        with open(demo_file, 'w', encoding='utf-8') as f:
            json.dump({'balance': balance}, f, indent=4)
        return True
    except:
        return False

def save_config(config):
    """Salva configuração no arquivo JSON"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Retorna configuração atual"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Atualiza configuração"""
    try:
        data = request.get_json()
        current_config = load_config()
        
        # Valida e atualiza apenas campos permitidos
        allowed_keys = ['SYMBOL', 'TIMEFRAME', 'POSITION_SIZE_USD', 'LEVERAGE', 'USE_DEMO', 'DEMO_BALANCE', 'RSI_LONG', 'RSI_SHORT', 'USE_VOL', 'USE_ADX', 'ADX_THRESH', 'SIGNAL_COOLDOWN', 'LOG_LEVEL',
                   'STOP_LOSS', 'TAKE_PROFIT', 'TRAILING_STOP', 'USE_FIXED_EXIT', 'USE_TRAILING',
                   'EXIT_RSI_LONG', 'EXIT_RSI_SHORT', 'USE_EXIT_RSI', 'EXIT_ADX_THRESHOLD', 'USE_EXIT_ADX',
                   'EXIT_AFTER_MINUTES', 'USE_TIME_EXIT', 'EXIT_ON_VOLUME_SPIKE', 'EXIT_VOLUME_MULTIPLIER']
        for key in allowed_keys:
            if key in data:
                current_config[key] = data[key]
        
        save_config(current_config)
        return jsonify({"success": True, "message": "Configuração atualizada!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retorna status do bot (se está em execução)"""
    try:
        import psutil
        bot_running = False
        
        # Verifica processos rodando
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if 'davinci_bot.py' in cmdline and 'python' in cmdline.lower():
                    bot_running = True
                    break
            except:
                pass
        
        # Fallback: verifica log se processo não encontrado
        if not bot_running and os.path.exists('davinci_bot.log'):
            try:
                with open('davinci_bot.log', 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                    if logs and any('DA VINCI SNIPER BOT INICIADO' in line for line in logs[-5:]):
                        # Verifica se é recente (últimas 2 horas)
                        from datetime import datetime, timedelta
                        cutoff = datetime.now() - timedelta(hours=2)
                        
                        for line in logs[-10:]:
                            try:
                                date_str = line.split(' | ')[0]
                                log_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
                                if log_time > cutoff and 'INICIADO' in line:
                                    bot_running = True
                                    break
                            except:
                                pass
            except:
                pass
        
        return jsonify({"running": bot_running})
    except Exception as e:
        return jsonify({"running": False})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Retorna últimos logs do bot"""
    logs = []
    log_sources = ['davinci_bot.log', 'bot_output.log']
    
    for log_file in log_sources:
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Filtra apenas logs das últimas 24 horas ou últimos 50 linhas
                    from datetime import datetime, timedelta
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    
                    for line in lines[-100:]:  # Últimas 100 linhas
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Tenta parsear a data
                        try:
                            # Formato: 2025-10-27 16:32:48,323
                            date_str = line.split(' | ')[0]
                            log_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
                            
                            # Filtra logs antigos (mais de 24 horas)
                            if log_time < cutoff_time:
                                continue
                        except:
                            pass  # Se não conseguir parsear, inclui mesmo assim
                        
                        # Parse do log com cores específicas - REMOVE prefixo de timestamp
                        clean_line = line
                        if ' | INFO | ' in line or ' | WARNING | ' in line or ' | ERROR | ' in line:
                            parts = line.split(' | ')
                            if len(parts) >= 3:
                                clean_line = ' | '.join(parts[2:])
                        
                        # Parse do log com cores específicas
                        if '>>> ENTRADA LONG <<<' in clean_line:
                            logs.append({"message": clean_line, "type": "entry-long"})
                        elif '>>> ENTRADA SHORT <<<' in clean_line:
                            logs.append({"message": clean_line, "type": "entry-short"})
                        elif '*** CROSSOVER' in clean_line:
                            logs.append({"message": clean_line, "type": "entry-long"})
                        elif '*** CROSSUNDER' in clean_line:
                            logs.append({"message": clean_line, "type": "entry-short"})
                        elif '| ERROR |' in line or 'Erro' in clean_line:
                            logs.append({"message": clean_line, "type": "error"})
                        elif '| WARNING |' in line:
                            logs.append({"message": clean_line, "type": "warning"})
                        elif 'ENTRADA' in clean_line and ('LONG' in clean_line or 'SHORT' in clean_line):
                            logs.append({"message": clean_line, "type": "success"})
                        elif 'DA VINCI SNIPER BOT INICIADO' in clean_line:
                            logs.append({"message": clean_line, "type": "success"})
                        elif 'Started HTTP' in clean_line or 'Debug mode' in clean_line:
                            continue  # Ignora logs do Flask
                        elif line.strip() == '':
                            continue  # Ignora linhas vazias
                        else:
                            logs.append({"message": clean_line, "type": "info"})
            except Exception as e:
                print(f"Erro ao ler logs de {log_file}: {e}")
    
    return jsonify({"logs": logs})

@app.route('/api/operations', methods=['GET'])
def get_operations():
    """Retorna operações abertas e fechadas"""
    if os.path.exists('operations.json'):
        try:
            with open('operations.json', 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        except:
            pass
    
    # Retorna estrutura vazia se arquivo não existir
    return jsonify({
        "open_operations": [],
        "closed_operations": []
    })

@app.route('/api/price/<path:symbol>', methods=['GET'])
def get_price(symbol):
    """Retorna preço atual do símbolo"""
    try:
        import ccxt
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
            'timeout': 10000
        })
        
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        change_24h = ticker.get('percentage', 0)
        
        return jsonify({
            "price": float(price),
            "change_24h": float(change_24h)
        })
    except Exception as e:
        print(f"Erro ao buscar preço: {e}")
        return jsonify({"error": str(e), "price": 0, "change_24h": 0}), 400

@app.route('/api/start-bot', methods=['POST'])
def start_bot():
    """Inicia o bot em background"""
    import subprocess
    import sys
    import time
    
    try:
        # Verifica se o bot já está rodando e PARAR versões antigas
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'davinci_bot.py' in cmdline:
                        print(f"Encontrado bot rodando, parando PID: {proc.info['pid']}")
                        proc.terminate()
                        time.sleep(1)
                except:
                    pass
        except ImportError:
            print("psutil não disponível, pulando verificação de processo")
        
        # Verifica se o arquivo existe
        bot_path = os.path.join(os.getcwd(), 'davinci_bot.py')
        if not os.path.exists(bot_path):
            return jsonify({"success": False, "message": f"Arquivo davinci_bot.py não encontrado em {os.getcwd()}"}), 500
        
        # Inicia o bot em background (sem criar nova janela)
        print(f"Iniciando bot: {sys.executable} {bot_path}")
        
        # Cria arquivo de log para o bot
        log_file = open('bot_output.log', 'a')
        
        subprocess.Popen(
            [sys.executable, 'davinci_bot.py'],
            cwd=os.getcwd(),
            stdout=log_file,
            stderr=log_file,
            shell=False
        )
        
        print("Bot iniciado com sucesso")
        return jsonify({"success": True, "message": "Bot iniciado com sucesso!"})
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Erro ao iniciar bot: {error_msg}")
        return jsonify({"success": False, "message": str(e), "error": error_msg}), 500

@app.route('/api/chart/<path:symbol>', methods=['GET'])
def get_chart_data(symbol):
    """Retorna dados OHLCV para o gráfico"""
    try:
        import ccxt
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
            'timeout': 10000
        })
        
        # Lê timeframe do config
        if os.path.exists('bot_config.json'):
            with open('bot_config.json', 'r') as f:
                config = json.load(f)
                timeframe = config.get('TIMEFRAME', '5m')
        else:
            timeframe = '5m'
        
        # Busca candles
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        
        candles = []
        for candle in ohlcv:
            candles.append({
                'timestamp': candle[0],
                'open': float(candle[1]),
                'high': float(candle[2]),
                'low': float(candle[3]),
                'close': float(candle[4]),
                'volume': float(candle[5])
            })
        
        # Calcula EMAs simples
        import pandas as pd
        import numpy as np
        df = pd.DataFrame(candles)
        
        def calculate_ema(values, period):
            ema = values.ewm(span=period, adjust=False).mean()
            # Preenche NaN com o primeiro valor válido
            ema = ema.fillna(values.iloc[0])
            return ema
        
        df['ema_short'] = calculate_ema(df['close'], 8)
        df['ema_mid'] = calculate_ema(df['close'], 21)
        
        return jsonify({
            "candles": candles,
            "ema_short": df['ema_short'].fillna(0).tolist(),
            "ema_mid": df['ema_mid'].fillna(0).tolist()
        })
    except Exception as e:
        print(f"Erro ao buscar dados do gráfico: {e}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/stop-bot', methods=['POST'])
def stop_bot():
    """Para o bot"""
    try:
        import psutil
        
        stopped = False
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'davinci_bot.py' in cmdline:
                        proc.terminate()
                        stopped = True
                except:
                    pass
        except ImportError:
            return jsonify({"success": False, "message": "psutil não disponível"}), 500
        
        if stopped:
            return jsonify({"success": True, "message": "Bot parado com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Nenhum bot em execução encontrado!"})
    except Exception as e:
        import traceback
        print(f"Erro ao parar bot: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    """Limpa os arquivos de log"""
    try:
        log_files = ['davinci_bot.log', 'bot_output.log']
        cleared_files = []
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'w') as f:
                        f.write('')  # Limpa o arquivo
                    cleared_files.append(log_file)
                except Exception as e:
                    print(f"Erro ao limpar {log_file}: {e}")
                    return jsonify({"success": False, "message": f"Erro ao limpar {log_file}: {str(e)}"}), 500
        
        if cleared_files:
            return jsonify({"success": True, "message": f"Logs limpos: {', '.join(cleared_files)}"})
        else:
            return jsonify({"success": False, "message": "Nenhum arquivo de log encontrado"})
    except Exception as e:
        import traceback
        print(f"Erro ao limpar logs: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/demo-balance', methods=['GET'])
def get_demo_balance():
    """Retorna saldo demo atual"""
    try:
        balance = load_demo_balance()
        return jsonify({"balance": balance})
    except Exception as e:
        return jsonify({"balance": 1000.0})

@app.route('/api/reset-demo', methods=['POST'])
def reset_demo():
    """Reseta saldo demo para valor inicial"""
    try:
        config = load_config()
        initial_balance = config.get('DEMO_BALANCE', 1000.0)
        save_demo_balance(initial_balance)

        # Limpa operações demo
        if os.path.exists('operations.json'):
            with open('operations.json', 'w', encoding='utf-8') as f:
                json.dump({"open_operations": [], "closed_operations": []}, f, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "message": f"Saldo demo resetado para ${initial_balance:.2f}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/pnl', methods=['GET'])
def get_pnl():
    """Retorna PnL total do dia"""
    try:
        if os.path.exists('operations.json'):
            with open('operations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            total_pnl = 0.0
            total_operations = 0
            winning_ops = 0
            losing_ops = 0

            # Soma operações fechadas
            for op in data.get('closed_operations', []):
                if op.get('pnl'):
                    total_pnl += float(op['pnl'])
                    total_operations += 1
                    if float(op['pnl']) > 0:
                        winning_ops += 1
                    elif float(op['pnl']) < 0:
                        losing_ops += 1

            # Soma operações abertas
            open_pnl = 0.0
            for op in data.get('open_operations', []):
                if op.get('pnl'):
                    open_pnl += float(op['pnl'])

            # Saldo demo se disponível
            demo_balance = None
            if os.path.exists('demo_balance.json'):
                with open('demo_balance.json', 'r', encoding='utf-8') as f:
                    demo_data = json.load(f)
                    demo_balance = demo_data.get('balance')

            # Win rate
            win_rate = (winning_ops / total_operations * 100) if total_operations > 0 else 0

            return jsonify({
                "total_pnl": total_pnl,
                "open_pnl": open_pnl,
                "all_pnl": total_pnl + open_pnl,
                "total_operations": total_operations,
                "winning_ops": winning_ops,
                "losing_ops": losing_ops,
                "win_rate": round(win_rate, 1),
                "demo_balance": demo_balance
            })
        else:
            return jsonify({
                "total_pnl": 0.0,
                "open_pnl": 0.0,
                "all_pnl": 0.0,
                "total_operations": 0,
                "winning_ops": 0,
                "losing_ops": 0,
                "win_rate": 0.0,
                "demo_balance": None
            })
    except Exception as e:
        return jsonify({
            "total_pnl": 0.0,
            "open_pnl": 0.0,
            "all_pnl": 0.0,
            "total_operations": 0,
            "winning_ops": 0,
            "losing_ops": 0,
            "win_rate": 0.0,
            "demo_balance": None,
            "error": str(e)
        })

if __name__ == '__main__':
    # Cria diretório templates se não existir
    os.makedirs('templates', exist_ok=True)
    app.run(host='127.0.0.1', port=5000, debug=True)
