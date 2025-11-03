"""
operations_history.py - Gerencia histórico permanente de operações fechadas
"""
import json
import os
import shutil
from datetime import datetime
import logging

log = logging.getLogger(__name__)

HISTORY_FILE = 'closed_operations_history.json'
BACKUP_DIR = 'backups'
OPERATIONS_FILE = 'operations.json'

def ensure_history_file():
    """Garante que o arquivo de histórico existe"""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4, ensure_ascii=False)

def save_to_history(operation):
    """Salva operação fechada no histórico permanente"""
    try:
        ensure_history_file()
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # Verifica se já existe (evita duplicatas)
        operation_id = operation.get('id')
        if operation_id:
            existing = [op for op in history if op.get('id') == operation_id]
            if existing:
                # Atualiza se já existe
                for i, op in enumerate(history):
                    if op.get('id') == operation_id:
                        history[i] = operation
                        break
            else:
                # Adiciona novo
                history.append(operation)
        else:
            # Adiciona mesmo sem ID (melhor que perder)
            history.append(operation)
        
        # Ordena por data mais recente primeiro
        history.sort(key=lambda x: x.get('entry_date', '') + ' ' + x.get('entry_time', ''), reverse=True)
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        
        return True
    except Exception as e:
        log.error(f"Erro ao salvar no histórico: {e}")
        return False

def load_history(limit=None):
    """Carrega histórico de operações fechadas"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return []
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if limit:
            return history[:limit]
        return history
    except Exception as e:
        log.error(f"Erro ao carregar histórico: {e}")
        return []

def backup_operations_file():
    """Cria backup do arquivo operations.json"""
    try:
        if not os.path.exists(OPERATIONS_FILE):
            return
        
        # Cria diretório de backups se não existir
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        
        # Nome do backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"operations_backup_{timestamp}.json"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Copia arquivo
        shutil.copy2(OPERATIONS_FILE, backup_path)
        
        # Mantém apenas os últimos 10 backups
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('operations_backup_')])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
        
        return True
    except Exception as e:
        log.error(f"Erro ao criar backup: {e}")
        return False

def merge_history_with_operations():
    """Merga operações fechadas do operations.json no histórico"""
    try:
        if not os.path.exists(OPERATIONS_FILE):
            return
        
        with open(OPERATIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        closed_ops = data.get('closed_operations', [])
        if not closed_ops:
            return
        
        # Salva cada operação no histórico
        for op in closed_ops:
            save_to_history(op)
        
        log.info(f"Mergidas {len(closed_ops)} operações fechadas no histórico")
        return True
    except Exception as e:
        log.error(f"Erro ao merge histórico: {e}")
        return False

def restore_from_backup():
    """Restaura o último backup se o arquivo principal estiver corrompido"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return False
        
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('operations_backup_')], reverse=True)
        if not backups:
            return False
        
        latest_backup = os.path.join(BACKUP_DIR, backups[0])
        shutil.copy2(latest_backup, OPERATIONS_FILE)
        
        log.info(f"Backup restaurado: {backups[0]}")
        return True
    except Exception as e:
        log.error(f"Erro ao restaurar backup: {e}")
        return False

