"""
extract_qlik_digital.py — Módulo oficial de extração para o Dashboard de Categorias Digital.
MIGRADO OFICIALMENTE PARA O QLIK CLOUD (SaaS: fsj.us.qlikcloud.com).

Encaminha a execução para `extract_qlik_cloud_digital.py` mantendo total
compatibilidade com `atualizar_digital.bat` e rotinas automatizadas.
"""
import asyncio
from extract_qlik_cloud_digital import fetch_qlik_cloud_data, load_fallback_data

async def fetch_qlik_data():
    return await fetch_qlik_cloud_data()

if __name__ == '__main__':
    asyncio.run(fetch_qlik_data())
