#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de reset para limpar posição travada no modo demo
"""

import json
import os
from datetime import datetime

def reset_operation():
    """Limpa a operação atual e reseta o estado do bot"""
    try:
        # Limpa operations.json
        operations_file = 'operations.json'
        if os.path.exists(operations_file):
            # Carrega operações existentes
            with open(operations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Fecha a operação aberta atual
            if data.get('open_operations'):
                for op in data['open_operations']:
                    if op.get('status') == 'open':
                        # Fecha a operação com preço atual estimado
                        op['status'] = 'closed'
                        op['exit_price'] = op.get('current_price', op.get('entry_price'))
                        op['exit_time'] = datetime.now().strftime('%H:%M')
                        op['reason'] = 'Reset Manual'

                        # Calcula PnL final
                        if op['side'] == 'LONG':
                            pnl = (op['exit_price'] - op['entry_price']) / op['entry_price'] * 100
                            pnl_usd = (op['exit_price'] - op['entry_price']) * op['quantity']
                        else:
                            pnl = (op['entry_price'] - op['exit_price']) / op['entry_price'] * 100
                            pnl_usd = (op['entry_price'] - op['exit_price']) * op['quantity']

                        op['pnl'] = float(pnl_usd)
                        op['pnl_percent'] = float(pnl)

                        # Move para operações fechadas
                        data['closed_operations'].append(op)
                        print(f"Operação fechada: {op['side']} {op['symbol']} | PnL: ${pnl_usd:+.2f} ({pnl:+.2f}%)")

                # Limpa operações abertas
                data['open_operations'] = []

                # Salva arquivo atualizado
                with open(operations_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

                print("Operacao limpa com sucesso!")
            else:
                print("Nenhuma operacao aberta encontrada.")
        else:
            print("Arquivo operations.json nao encontrado.")

        # Reseta saldo demo se necessário
        config_file = 'bot_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            initial_balance = config.get('DEMO_BALANCE', 1000.0)

            # Atualiza saldo demo
            demo_balance_file = 'demo_balance.json'
            with open(demo_balance_file, 'w', encoding='utf-8') as f:
                json.dump({'balance': initial_balance}, f, indent=4)

            print(f"Saldo demo resetado para ${initial_balance:.2f}")

        print("\nReset concluido! O bot pode ser reiniciado com estado limpo.")

    except Exception as e:
        print(f"Erro durante o reset: {e}")

if __name__ == "__main__":
    print("DA VINCI BOT - RESET DE OPERACAO")
    print("=" * 50)
    reset_operation()