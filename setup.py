#!/usr/bin/env python3
"""
Script auxiliar: cria a pasta de saída antes de rodar a análise.
Execute: python setup.py && python analise.py
"""
import os
os.makedirs("graficos", exist_ok=True)
print("✅ Pasta 'graficos/' criada com sucesso.")
