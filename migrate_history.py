"""
Script para migrar operações fechadas do operations.json para o histórico permanente
Execute uma vez para migrar todas as operações fechadas existentes
"""
import json
import os
import operations_history

def migrate_closed_operations():
    """Migra todas as operações fechadas do operations.json para o histórico"""
    try:
        if not os.path.exists('operations.json'):
            print("Arquivo operations.json não encontrado.")
            return
        
        with open('operations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        closed_ops = data.get('closed_operations', [])
        
        if not closed_ops:
            print("Nenhuma operação fechada encontrada para migrar.")
            return
        
        print(f"Migrando {len(closed_ops)} operações fechadas para o histórico...")
        
        migrated = 0
        for op in closed_ops:
            if operations_history.save_to_history(op):
                migrated += 1
        
        print(f"✅ {migrated} operações migradas com sucesso para closed_operations_history.json")
        
        # Cria backup também
        operations_history.backup_operations_file()
        print(f"✅ Backup criado na pasta 'backups'")
        
    except Exception as e:
        print(f"❌ Erro ao migrar: {e}")

if __name__ == '__main__':
    migrate_closed_operations()

