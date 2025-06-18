from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

DATA_FILE = "data.json"

# Prezzi aggiornati
PREZZI = {
    "bianche_matrimoniali": 0.90,
    "bianche_singole": 0.80,
    "bambu_matrimoniali": 1.20,
    "bambu_singole": 1.00,
    "federe": 0.60,
    "bidet": 0.40,
    "viso": 0.60,
    "doccia": 1.20,
    "tappeto": 0.70,
    "cialde": 0.22,
    "salati": 0.31,
    "dolci": 0.06,
    "bevande": 0.45
}

# Inizializza file dati se non esiste
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"carichi": [], "consumi": []}, f)

def carica_dati():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, 'w') as f:
        json.dump(dati, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/carichi')
def pagina_carichi():
    return render_template('carichi.html')

@app.route('/inserisci')
def pagina_inserisci():
    return render_template('inserisci.html')

@app.route('/magazzino')
def pagina_magazzino():
    return render_template('magazzino.html')

@app.route('/report')
def pagina_report():
    return render_template('report.html')

@app.route('/api/carichi', methods=['POST'])
def salva_carichi():
    dati = carica_dati()
    carico = request.json
    dati['carichi'].append(carico)
    salva_dati(dati)
    return jsonify({'ok': True})

@app.route('/api/consumi', methods=['POST'])
def salva_consumi():
    dati = carica_dati()
    consumo = request.json
    dati['consumi'].append(consumo)
    salva_dati(dati)
    return jsonify({'ok': True})

@app.route('/api/giacenze')
def api_giacenze():
    sede = request.args.get('sede')
    dati = carica_dati()
    giacenze = {}
    for articolo in PREZZI:
        totale_carichi = sum(c.get(articolo, 0) for c in dati['carichi'] if c.get('struttura') == sede)
        totale_consumi = sum(c.get(articolo, 0) for c in dati['consumi'] if c.get('struttura') == sede)
        giacenze[articolo] = totale_carichi - totale_consumi
    return jsonify(giacenze)

@app.route('/api/report-mensile')
def report_mensile():
    mese = request.args.get("mese")  # formato "2024-06"
    sede = request.args.get("sede")
    dati = carica_dati()
    totale = 0
    for carico in dati['carichi']:
        if carico.get("struttura") != sede:
            continue
        data_carico = carico.get("data")
        if not data_carico or not data_carico.startswith(mese):
            continue
        for articolo, prezzo in PREZZI.items():
            totale += carico.get(articolo, 0) * prezzo
    return jsonify({"totale": round(totale, 2)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)