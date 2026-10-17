import requests
import time
import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI(title="Metrópole 226 Coins - Ecossistema Global", version="2.0")

# --- SEGURANÇA INTEGRAL ---
API_KEY = "CHAVE_SECRETA_226_GLOBAL"
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

def verificar_autorizacao(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return True
    raise HTTPException(status_code=403, detail="Acesso negado. Token inválido.")

# Registro de Balanço em Memória Protegida (Cofre Digital)
COFRE_CUSTODIA = {"BTC": 0.0, "ETH": 0.0, "SOL": 0.0}
SALDO_226 = {"usuario_global": 0.0}

class TransacaoCofre(BaseModel):
    btc: float = 0.0
    eth: float = 0.0
    sol: float = 0.0

class PagamentoComercio(BaseModel):
    valor_compra: float
    moeda_destino: str

def obter_telemetria_mercado():
    """Puxador de dados do mercado cripto e fiat com barramento de contingência."""
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

# --- INTERFACE VISUAL EMBUTIDA (CÓDIGO CHEIO) ---
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metrópole 226 Coins - Painel Global</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .container { max-width: 800px; width: 100%; }
        h1 { color: #58a6ff; text-align: center; border-bottom: 1px solid #21262d; padding-bottom: 10px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; margin-bottom: 20px; }
        .row { display: flex; gap: 10px; margin-bottom: 10px; }
        input, select, button { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 10px; border-radius: 6px; flex: 1; font-size: 14px; }
        button { background-color: #238636; color: white; cursor: pointer; font-weight: bold; border: none; }
        button:hover { background-color: #2ea44f; }
        button.secundario { background-color: #21262d; border: 1px solid #30363d; }
        button.secundario:hover { background-color: #30363d; }
        pre { background-color: #010409; padding: 15px; border-radius: 6px; border: 1px solid #30363d; overflow-x: auto; color: #7ee787; font-family: monospace; }
        .status-badge { display: inline-block; padding: 5px 10px; border-radius: 20px; background-color: #238636; color: white; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 Metrópole 226 Coins</h1>
        <p style="text-align: center; color: #8b949e;">A Ponte através da qual a Abundância flui</p>

        <div class="card">
            <h2>💰 Seu Terminal 226 Coin</h2>
            <div class="row">
                <div>Status do Sistema: <span class="status-badge">Operacional</span></div>
            </div>
            <div id="saldo-display" style="font-size: 24px; font-weight: bold; color: #58a6ff; margin-top: 10px;">
                Saldo: 0.0000 226 Coins
            </div>
        </div>

        <div class="card">
            <h3>📥 Depositar Moedas no Cofre (Emitir Lastro)</h3>
            <div class="row">
                <input type="number" id="dep-btc" placeholder="Qtd Bitcoin (BTC)" step="0.0001">
                <input type="number" id="dep-eth" placeholder="Qtd Ethereum (ETH)" step="0.01">
                <input type="number" id="dep-sol" placeholder="Qtd Solana (SOL)" step="0.1">
            </div>
            <button onclick="executarTransacao('depositar-lastro')">Confirmar Depósito e Emitir Título</button>
        </div>

        <div class="card">
            <h3>🛍️ Simular Compra Comercial (Pix Cripto Global)</h3>
            <div class="row">
                <input type="number" id="compra-valor" placeholder="Valor da Compra">
                <select id="compra-moeda">
                    <option value="BRL">Real (BRL)</option>
                    <option value="USD">Dólar (USD)</option>
                    <option value="INR">Rúpias (INR)</option>
                </select>
            </div>
            <button class="secundario" onclick="executarCompra()">Autorizar Pagamento Instantâneo</button>
        </div>

        <div class="card">
            <h3>📊 Telemetria Exata do Sistema (JSON Logs)</h3>
            <pre id="json-output">// Aguardando comandos do núcleo bancário...</pre>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        async function executarTransacao(endpoint) {
            const dados = {
                btc: parseFloat(document.getElementById('dep-btc').value) || 0,
                eth: parseFloat(document.getElementById('dep-eth').value) || 0,
                sol: parseFloat(document.getElementById('dep-sol').value) || 0
            };

            try {
                const resposta = await fetch(`${API_BASE}/${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dados)
                });
                
                const resultado = await resposta.json();
                document.getElementById('json-output').innerText = JSON.stringify(resultado, null, 4);
                
                if (resultado.saldo_total_226 !== undefined) {
                    document.getElementById('saldo-display').innerText = `Saldo: ${resultado.saldo_total_226.toFixed(4)} 226 Coins`;
                }
            } catch (erro) {
                document.getElementById('json-output').innerText = "Erro crítico na comunicação com o barramento do motor.";
            }
        }

        async function executarCompra() {
            const dados = {
                valor_compra: parseFloat(document.getElementById('compra-valor').value) || 0,
                moeda_destino: document.getElementById('compra-moeda').value
            };

            try {
                const resposta = await fetch(`${API_BASE}/consumir-saldo`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dados)
                });
                
                const resultado = await resposta.json();
                document.getElementById('json-output').innerText = JSON.stringify(resultado, null, 4);
                
                if (resultado.saldo_restante_226 !== undefined) {
                    document.getElementById('saldo-display').innerText = `Saldo: ${resultado.saldo_restante_226.toFixed(4)} 226 Coins`;
                }
            } catch (erro) {
                document.getElementById('json-output').innerText = "Erro crítico ao autorizar o pagamento internacional.";
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def obter_dashboard_vivo():
    return HTML_DASHBOARD

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
        "evento": "Lastro Depositado com Sucesso",
        "status_rede": "Operacional",
        "cofre_atualizado": COFRE_CUSTODIA,
        "novas_226_coins_emitidas": round(novos_titulos, 4),
        "saldo_total_226": round(SALDO_226["usuario_global"], 4)
    }

@app.post("/consumir-saldo")
def consumir_saldo_comercio(compra: PagamentoComercio):
    telemetria = obter_telemetria_mercado()
    
    if compra.moeda_destino not in telemetria:
        raise HTTPException(status_code=400, detail="Moeda fiduciária não suportada.")
        
    taxa_cambio = telemetria[compra.moeda_destino]
    custo_em_226 = compra.valor_compra / taxa_cambio
    
    if SALDO_226["usuario_global"] < custo_em_226:
        raise HTTPException(status_code=400, detail="Saldo de 226 Coins insuficiente.")
        
    SALDO_226["usuario_global"] -= custo_em_226
    
    return {
        "status": "Transação Global Aprovada",
        "compra_original": f"{compra.valor_compra} {compra.moeda_destino}",
        "debitado_226_coins": round(custo_em_226, 4),
        "saldo_restante_226": round(SALDO_226["usuario_global"], 4)
    }

if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)
