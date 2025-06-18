from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

FILE_PATH = 'data.json'
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
    "cialde": 0.00,
    "bevande": 0.00,
    "dolci": 0.00,
    "salati": 0.00
}

# Inizializza il file se non esiste
def init_data():
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w') as f:
            json.dump({"carichi": [], "consumi": []}, f)

# Legge i dati dal file
def read_data():
    with open(FILE_PATH, 'r') as f:
        return json.load(f)

# Salva i dati sul file
def save_data(data):
    with open(FILE_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/inserisci')
def inserisci():
    return render_template('inserisci.html')

@app.route('/carichi')
def carichi():
    return render_template('carichi.html')

@app.route('/magazzino')
def magazzino():
    return render_template('magazzino.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/api/invia_consumi', methods=['POST'])
def invia_consumi():
    dati = request.json
    data = read_data()
    dati['data'] = datetime.now().isoformat()
    data['consumi'].append(dati)
    save_data(data)
    return jsonify({"successo": True})

@app.route('/api/invia_carichi', methods=['POST'])
def invia_carichi():
    dati = request.json
    data = read_data()
    dati['data'] = datetime.now().isoformat()
    data['carichi'].append(dati)
    save_data(data)
    return jsonify({"successo": True})

@app.route('/api/giacenze')
def giacenze():
    sede = request.args.get("sede")
    data = read_data()
    inventario = {k: 0 for k in PREZZI.keys()}
    for carico in data['carichi']:
        if carico['struttura'] == sede:
            for k in PREZZI:
                inventario[k] += int(carico.get(k, 0))
    for consumo in data['consumi']:
        if consumo['struttura'] == sede:
            for k in PREZZI:
                inventario[k] -= int(consumo.get(k, 0))
    return jsonify(inventario)

@app.route('/api/report_mensile')
def report_mensile():
    mese = request.args.get("mese")
    struttura = request.args.get("struttura")
    data = read_data()
    totale = 0.0
    for carico in data['carichi']:
        data_carico = datetime.fromisoformat(carico['data'])
        mese_str = data_carico.strftime("%Y-%m")
        if mese_str == mese and carico['struttura'] == struttura:
            for k in PREZZI:
                totale += int(carico.get(k, 0)) * PREZZI[k]
    return jsonify({"totale": round(totale, 2)})

if __name__ == '__main__':
    init_data()
    app.run(debug=True)