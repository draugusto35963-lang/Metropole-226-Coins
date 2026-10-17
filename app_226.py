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
from pydantic import BaseModel
from decimal import Decimal, getcontext

# Ativação do ANTI-NAN SHIELD
getcontext().prec = 300

app = FastAPI(title="Cockpit Supremo Persistente - Metrópole 226 & Malha 7770777", version="4.0")

DB_PATH = "C:/226Coins/vendas.db"
DIRETORIO_MALHA = "C:/7770777"
PROCESSOS_ATIVOS = []
moedas_acumuladas = Decimal('0.0')

# Constantes Winamp API via Windows Messaging
WM_COMMAND = 0x0111
WINAMP_PLAY = 40045
WINAMP_STOP = 40047

TERMO_FUNDO = "Bij-Je-Zijn"
TERMO_EFEITO = "Jackpot"

def inicializar_banco_persistente():
    """Garante a estrutura física do cofre e do Anti-NaN Shield no banco vendas.db."""
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
        cursor.execute("INSERT INTO vault_persistente VALUES ('usuario_global', 0.0, 0.0, 0.0, '5000.0', '0.0')")
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

# --- MÓDULOS NATIVOS DE CONTROLE DO WINAMP (CTYPES) ---
def cortar_efeito_timer(hwnd_ef):
    if hwnd_ef:
        ctypes.windll.user32.SendMessageW(hwnd_ef, WM_COMMAND, WINAMP_STOP, 0)

def buscar_winamp_por_musica(termo):
    hwnd_encontrado = 0
    def enum_windows_proc(hwnd, lParam):
        nonlocal hwnd_encontrado
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            if "Winamp" in buff.value and termo.lower() in buff.value.lower():
                hwnd_encontrado = hwnd
                return False
        return True
    cb_enum = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)(enum_windows_proc)
    ctypes.windll.user32.EnumWindows(cb_enum, 0)
    return hwnd_encontrado

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

# --- ROTAS BANCÁRIAS E DA ORQUESTRA ---
@app.get("/", response_class=HTMLResponse)
def obter_cockpit_supremo():
    caminho_html = "C:/226Coins/index.html"
    if not os.path.exists(caminho_html):
        raise HTTPException(status_code=404, detail="index.html ausente.")
    with open(caminho_html, "r", encoding="utf-8") as arquivo:
        return arquivo.read()

@app.get("/status-malha")
def obter_status_agentes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT saldo_226, retido_226 FROM vault_persistente WHERE id='usuario_global'")
    row = cursor.fetchone()
    conn.close()
    
    scripts = ["multiplicador_autonomo.py", "agente_elias_integrado.py", "agente_autonomo.py", "agente_cineasta.py", "agente_autonomo_integrado.py"]
    telemetria_arquivos = {}
    for script in scripts:
        caminho = os.path.join(DIRETORIO_MALHA, script)
        existe = os.path.exists(caminho)
        telemetria_arquivos[script] = "COMPLIANCE_OK" if existe else "AUSENTE"
        
    return {
        "gateway": "Chronolog Congruente",
        "origem_malha": DIRETORIO_MALHA,
        "saldo_persistente": row[0],
        "retido_elias": row[1],
        "batalhao_status": "LIGADO" if len(PROCESSOS_ATIVOS) > 0 else "DESMOBILIZADO",
        "verificacao_disco": telemetria_arquivos
    }

@app.post("/ligar-malha")
def acoplar_e_ligar_batalhao():
    global PROCESSOS_ATIVOS
    if len(PROCESSOS_ATIVOS) > 0:
        return {"status": "ORQUESTRA_ATIVA", "agentes_rodando": len(PROCESSOS_ATIVOS)}
        
    scripts_alvo = ["multiplicador_autonomo.py", "agente_elias_integrado.py", "agente_autonomo.py", "agente_cineasta.py", "agente_autonomo_integrado.py"]
    processos_iniciados = []
    
    antigo_dir = os.getcwd()
    if os.path.exists(DIRETORIO_MALHA):
        os.chdir(DIRETORIO_MALHA)
        
    for agente in scripts_alvo:
        if os.path.exists(agente):
            p = subprocess.Popen([sys.executable, agente], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            PROCESSOS_ATIVOS.append(p)
            processos_iniciados.append(agente)
            
    os.chdir(antigo_dir)
    return {"status": "ORQUESTRA_ATIVA", "ciclo": 2105, "agentes_rodando": processos_iniciados}

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
    
    # Execução da fórmula do Jackpot do Elias
    valor_usd = (dados.btc * telemetria["BTC"]) + (dados.eth * telemetria["ETH"]) + (dados.sol * telemetria["SOL"])
    if valor_usd > 0:
        lucro_bruto = Decimal(str(valor_usd)) * Decimal(str(random.uniform(0.025, 0.06)))
        taxa_elias = lucro_bruto * Decimal('0.10')
        lucro_liquido = lucro_bruto - taxa_elias
        
        coins_base += lucro_liquido
        moedas_acumuladas += taxa_elias
        
        # Disparo Automático do Efeito Winamp
        hwnd_efeito = buscar_winamp_por_musica(TERMO_EFEITO)
        if hwnd_efeito:
            ctypes.windll.user32.SendMessageW(hwnd_efeito, WM_COMMAND, WINAMP_PLAY, 0)
            threading.Timer(1.5, cortar_efeito_timer, args=[hwnd_efeito]).start()
            
    cursor.execute("UPDATE vault_persistente SET btc=?, eth=?, sol=?, saldo_226=?, retido_226=? WHERE id='usuario_global'", 
                   (n_btc, n_eth, n_sol, str(coins_base), str(moedas_acumuladas)))
    conn.commit()
    conn.close()
    
    return {
        "status": "CONGRUENTE",
        "gateway": "Chronolog Congruente",
        "saldo_total_persistente_226": float(coins_base),
        "acumulado_taxa_elias": float(moedas_acumuladas)
    }

@app.post("/consumir-saldo")
def consumir_saldo_comercio(compra: PagamentoComercio):
    telemetria = obter_telemetria_mercado()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT saldo_226 FROM vault_persistente WHERE id='usuario_global'")
    c_saldo_str = cursor.fetchone()[0]
    coins_base = Decimal(c_saldo_str)
    
    taxa_cambio = telemetria[compra.moeda_destino]
    custo_em_226 = Decimal(str(compra.valor_compra)) / Decimal(str(taxa_cambio))
    
    if coins_base < custo_em_226:
        conn.close()
        raise HTTPException(status_code=400, detail="Saldo insuficiente no Anti-NaN Shield.")
        
    coins_base -= custo_em_226
    cursor.execute("UPDATE vault_persistente SET saldo_226=? WHERE id='usuario_global'", (str(coins_base),))
    conn.commit()
    conn.close()
    
    return {
        "status": "Liquidado e Gravado no Disco",
        "saldo_restante_persistente_226": float(coins_base)
    }

@app.post("/winamp/{acao}")
def winamp_control(acao: str):
    cmd = WINAMP_PLAY if acao == 'play' else WINAMP_STOP
    hwnd_fundo = buscar_winamp_por_musica(TERMO_FUNDO)
    if hwnd_fundo:
        ctypes.windll.user32.SendMessageW(hwnd_fundo, WM_COMMAND, cmd, 0)
        return {"status": "FUNDO_COMANDADO"}
    return {"status": "PLAY_FUNDO_AGUARDANDO"}

if __name__ == "__main__":
    import uvicorn
    porta = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=porta)
