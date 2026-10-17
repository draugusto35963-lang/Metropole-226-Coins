import requests
import time
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Cockpit Supremo - Metrópole 226 & Malha 7770777", version="3.0")

# --- REGISTRO DE MEMÓRIA PROTEGIDA E ESTADOS DA MALHA ---
COFRE_CUSTODIA = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0}
SALDO_226 = {"usuario_global": 0.0}

ESTADO_MALHA = {
    "orquestrador_malha": {"arquivo": "orquestrador_malha.py", "status": "ATIVO", "pid": 7770},
    "agente_autonomo": {"arquivo": "agente_autonomo_integrado.py", "status": "CONGRUENTE", "ciclos": 4080},
    "agente_elias": {"arquivo": "agente_elias_integrado.py", "status": "PROCESSANDO", "vault": "SINCRONIZADO"},
    "agente_cineasta": {"arquivo": "agente_cineasta.py", "status": "STANDBY", "modo": "RENDER"},
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
    """Puxador de dados do mercado cripto e fiat com barramento de contingência rápido."""
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

# --- INJEÇÃO DA INTERFACE VIVA DIRETAMENTE DO DISCO ---
@app.get("/", response_class=HTMLResponse)
def obter_cockpit_supremo():
    caminho_html = "C:/226Coins/index.html"
    if not os.path.exists(caminho_html):
        raise HTTPException(status_code=404, detail="Arquivo index.html nao encontrado em C:/226Coins/")
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

@app.get("/status-malha")
def obter_status_agentes():
    return {"evento": "Telemetria Quântica Coletada", "origem": "c:\\7770777", "malha": ESTADO_MALHA}

@app.post("/depositar-lastro")
def depositar_e_emitir(dados: TransacaoCofre):
    telemetria = obter_telemetria_mercado()
    COFRE_CUSTODIA["BTC"] += dados.btc
    COFRE_CUSTODIA["ETH"] += dados.eth
    COFRE_CUSTODIA["SOL"] += dados.sol
    
    valor_usd = (dados.btc * telemetria["BTC"]) + (dados.eth * telemetria["ETH"]) + (dados.sol * telemetria["SOL"])
    novos_titulos = valor_usd / 1.0 
    SALDO_226["usuario_global"] += novos_titulos
    
    return {
        "gateway": "Chronolog Congruente",
        "status_malha": "Sincronizada",
        "cofre_7770777_atualizado": COFRE_CUSTODIA,
        "novas_226_coins_emitidas": round(novos_titulos, 4),
        "saldo_total_226": round(SALDO_226["usuario_global"], 4)
    }

@app.post("/consumir-saldo")
def consumir_saldo_comercio(compra: PagamentoComercio):
    telemetria = obter_telemetria_mercado()
    if compra.moeda_destino not in telemetria:
        raise HTTPException(status_code=400, detail="Par de conversão não suportado.")
    taxa_cambio = telemetria[compra.moeda_destino]
    custo_em_226 = compra.valor_compra / taxa_cambio
    if SALDO_226["usuario_global"] < custo_em_226:
        raise HTTPException(status_code=400, detail="Saldo insuficiente na malha 226.")
    SALDO_226["usuario_global"] -= custo_em_226
    return {
        "status": "Transação Liquidada via Orquestrador",
        "compra_original": f"{compra.valor_compra} {compra.moeda_destino}",
        "debitado_226_coins": round(custo_em_226, 4),
        "saldo_restante_226": round(SALDO_226["usuario_global"], 4),
        "telemetria_aplicada": f"1 USD = {taxa_cambio} {compra.moeda_destino}"
    }

if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)
