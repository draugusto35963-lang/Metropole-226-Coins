import requests
import time
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Cockpit Persistente - Metrópole 226 & Malha 7770777", version="4.0")

DB_PATH = "C:/226Coins/vendas.db"

def inicializar_banco_persistente():
    """Cria a tabela do cofre no banco de dados vendas.db se não existir (Compliance Total)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vault_persistente (
            id TEXT PRIMARY KEY,
            btc REAL,
            eth REAL,
            sol REAL,
            saldo_226 REAL
        )
    ''')
    # Inicializa o registro do usuário global padrão se estiver vazio
    cursor.execute("SELECT id FROM vault_persistente WHERE id='usuario_global'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO vault_persistente VALUES ('usuario_global', 0.0, 0.0, 0.0, 0.0)")
    conn.commit()
    conn.close()

inicializar_banco_persistente()

ESTADO_MALHA = {
    "orquestrador_malha": {"arquivo": "orquestrador_malha.py", "status": "ATIVO", "pid": 7770},
    "agente_autonomo": {"arquivo": "agente_autonomo_integrado.py", "status": "CONGRUENTE", "ciclos": 4080},
    "agente_elias": {"arquivo": "agente_elias_integrado.py", "status": "PROCESSANDO", "vault": "PERSISTENTE_DB"},
    "conversor_quantico": {"arquivo": "conversor_quantico.py", "status": "PRONTO", "mid": "conversor_quantico.mid"}
}

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
            "BTC": res_crypto["bitcoin"]["usd"], "ETH": res_crypto["ethereum"]["usd"], "SOL": res_crypto["solana"]["usd"],
            "BRL": res_fiat["rates"]["BRL"], "INR": res_fiat["rates"]["INR"], "USD": 1.0
        }
    except Exception:
        return {"BTC": 67000.0, "ETH": 2500.0, "SOL": 150.0, "BRL": 5.60, "INR": 84.0, "USD": 1.0}

@app.get("/", response_class=HTMLResponse)
def obter_cockpit_supremo():
    caminho_html = "C:/226Coins/index.html"
    if not os.path.exists(caminho_html):
        raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado.")
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

@app.get("/status-malha")
def obter_status_agentes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT btc, eth, sol, saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    row = cursor.fetchone()
    conn.close()
    return {
        "evento": "Telemetria Persistente Coletada",
        "origem_disco": DB_PATH,
        "balanco_real_vault": {"BTC": row[0], "ETH": row[1], "SOL": row[2], "226Coins": row[3]},
        "malha": ESTADO_MALHA
    }

@app.post("/depositar-lastro")
def depositar_e_emitir(dados: TransacaoCofre):
    telemetria = obter_telemetria_mercado()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT btc, eth, sol, saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    c_btc, c_eth, c_sol, c_saldo = cursor.fetchone()
    
    # Atualiza somando no banco físico
    n_btc = c_btc + dados.btc
    n_eth = c_eth + dados.eth
    n_sol = c_sol + dados.sol
    
    valor_usd = (dados.btc * telemetria["BTC"]) + (dados.eth * telemetria["ETH"]) + (dados.sol * telemetria["SOL"])
    n_saldo = c_saldo + valor_usd
    
    cursor.execute("UPDATE vault_persistente SET btc=?, eth=?, sol=?, saldo_226=? WHERE id='usuario_global'", 
                   (n_btc, n_eth, n_sol, n_saldo))
    conn.commit()
    conn.close()
    
    return {
        "gateway": "Chronolog Congruente",
        "status_banco": "Escrita no Disco Concluida",
        "cofre_fisico_vendas_db": {"BTC": n_btc, "ETH": n_eth, "SOL": n_sol},
        "saldo_total_persistente_226": round(n_saldo, 4)
    }

@app.post("/consumir-saldo")
def consumir_saldo_comercio(compra: PagamentoComercio):
    telemetria = obter_telemetria_mercado()
    if compra.moeda_destino not in telemetria:
        raise HTTPException(status_code=400, detail="Par de conversão não suportado.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT btc, eth, sol, saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    c_btc, c_eth, c_sol, c_saldo = cursor.fetchone()
    
    taxa_cambio = telemetria[compra.moeda_destino]
    custo_em_226 = compra.valor_compra / taxa_cambio
    
    if c_saldo < custo_em_226:
        conn.close()
        raise HTTPException(status_code=400, detail="Saldo insuficiente no banco de dados físico.")
        
    n_saldo = c_saldo - custo_em_226
    cursor.execute("UPDATE vault_persistente SET saldo_226=? WHERE id='usuario_global'", (n_saldo,))
    conn.commit()
    conn.close()
    
    return {
        "status": "Liquidado e Gravado no Disco",
        "compra_debitada": f"{compra.valor_compra} {compra.moeda_destino}",
        "saldo_restante_persistente_226": round(n_saldo, 4),
        "telemetria_aplicada": f"1 USD = {taxa_cambio} {compra.moeda_destino}"
    }

if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)
