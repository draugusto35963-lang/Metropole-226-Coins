import requests
import time
import os
import sqlite3
import subprocess
import sys
import ctypes
import random
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decimal import Decimal, getcontext

getcontext().prec = 300

app = FastAPI(title="Metrópole 226 Coins - Stealth Core Persistente", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "C:/226Coins/vendas.db"
DIRETORIO_NINJA = "C:/7770777"
PROCESSOS_OCULTOS = []

WM_COMMAND = 0x0111
WINAMP_PLAY = 40045
WINAMP_STOP = 40047
TERMO_FUNDO = "Bij-Je-Zijn"
TERMO_EFEITO = "Jackpot"

def inicializar_banco_persistente():
    os.makedirs("C:/226Coins", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault_persistente (
            id TEXT PRIMARY KEY,
            btc REAL,
            eth REAL,
            sol REAL,
            saldo_226 TEXT,
            retido_226 TEXT
        )
    ''')
    cursor.execute("SELECT id FROM vault_persistente WHERE id='usuario_global'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO vault_persistente VALUES ('usuario_global', 0.0, 0.0, 0.0, '24000.0', '0.0')")
    conn.commit()
    conn.close()

inicializar_banco_persistente()

class TransacaoCofre(BaseModel):
    btc: float = 0.0
    eth: float = 0.0
    sol: float = 0.0

class PagamentoComercio(BaseModel):
    valor_compra: float
    moeda_destino: str

def obter_telemetria_mercado():
    url_crypto = "https://coingecko.com"
    url_fiat = "https://er-api.com"
    try:
        res_crypto = requests.get(url_crypto, timeout=5).json()
        res_fiat = requests.get(url_fiat, timeout=5).json()
        return {
            "BTC": res_crypto["bitcoin"]["usd"], 
            "ETH": res_crypto["ethereum"]["usd"], 
            "SOL": res_crypto["solana"]["usd"],
            "BRL": res_fiat["rates"]["BRL"], 
            "INR": res_fiat["rates"]["INR"], 
            "USD": 1.0
        }
    except Exception:
        return {"BTC": 67000.0, "ETH": 2500.0, "SOL": 150.0, "BRL": 5.60, "INR": 84.0, "USD": 1.0}

@app.get("/", response_class=HTMLResponse)
def obter_cockpit_stealth():
    caminho_html = "C:/226Coins/index.html"
    if not os.path.exists(caminho_html):
        raise HTTPException(status_code=404, detail="index.html ausente.")
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

@app.get("/status-inicial")
def obter_status_inicial():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    resultado = cursor.fetchone()
    saldo = float(resultado[0]) if resultado else 0.0
    conn.close()
    return {"saldo_atual": saldo}

@app.post("/depositar-lastro")
def depositar_e_emitir(dados: TransacaoCofre):
    telemetria = obter_telemetria_mercado()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT btc, eth, sol, saldo_226, retido_226 FROM vault_persistente WHERE id='usuario_global'")
    c_btc, c_eth, c_sol, c_saldo_str, c_retido_str = cursor.fetchone()
    
    coins_base = Decimal(c_saldo_str)
    moedas_acumuladas = Decimal(c_retido_str)
    
    n_btc = c_btc + dados.btc
    n_eth = c_eth + dados.eth
    n_sol = c_sol + dados.sol
    
    valor_usd = (dados.btc * telemetria["BTC"]) + (dados.eth * telemetria["ETH"]) + (dados.sol * telemetria["SOL"])
    if valor_usd > 0:
        lucro_bruto = Decimal(str(valor_usd)) * Decimal(str(random.uniform(0.025, 0.06)))
        taxa_elias = lucro_bruto * Decimal('0.10')
        coins_base += (lucro_bruto - taxa_elias)
        moedas_acumuladas += taxa_elias
            
    cursor.execute("UPDATE vault_persistente SET btc=?, eth=?, sol=?, saldo_226=?, retido_226=? WHERE id='usuario_global'", 
                   (n_btc, n_eth, n_sol, str(coins_base), str(moedas_acumuladas)))
    conn.commit()
    conn.close()
    
    return {
        "status": "CONGRUENTE",
        "gateway": "Chronolog Ninjas Active",
        "saldo_total_persistente_226": float(coins_base)
    }

@app.post("/consumir-saldo")
def consumir_saldo_comercio(compra: PagamentoComercio):
    telemetria = obter_telemetria_mercado()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    resultado = cursor.fetchone()
    coins_base = Decimal(resultado[0])
    
    taxa_cambio = telemetria[compra.moeda_destino]
    custo_em_226 = Decimal(str(compra.valor_compra)) / Decimal(str(taxa_cambio))
    
    if coins_base < custo_em_226:
        conn.close()
        raise HTTPException(status_code=400, detail="Saldo insuficiente.")
        
    coins_base -= custo_em_226
    cursor.execute("UPDATE vault_persistente SET saldo_226=? WHERE id='usuario_global'", (str(coins_base),))
    conn.commit()
    conn.close()
    
    return {"status": "Liquidado e Gravado no Disco", "saldo_restante_persistente_226": float(coins_base)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
