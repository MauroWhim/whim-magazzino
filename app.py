from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data.json'

ARTICOLI = [
    ("bianche_matrimoniali", 0.90),
    ("bianche_singole", 0.80),
    ("bambu_matrimoniali", 1.20),
    ("bambu_singole", 1.00),
    ("federe", 0.60),
    ("bidet", 0.40),
    ("viso", 0.60),
    ("doccia", 1.20),
    ("tappeto", 0.70),
    ("cialde", 0),
    ("bevande", 0),
    ("dolci", 0),
    ("salati", 0)
]

# Assicura che il file esista
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
def index():
    return render_template('index.html')

@app.route('/inserisci')
def inserisci():
    return render_template('inserisci.html', articoli=ARTICOLI)

@app.route('/carichi')
def carichi():
    return render_template('carichi.html', articoli=ARTICOLI)

@app.route('/magazzino')
def magazzino():
    return render_template('magazzino.html')

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/api/aggiungi_consumo', methods=['POST'])
def aggiungi_consumo():
    dati = carica_dati()
    nuovo = request.json
    nuovo["timestamp"] = datetime.now().isoformat()
    dati["consumi"].append(nuovo)
    salva_dati(dati)
    return '', 204

@app.route('/api/aggiungi_carico', methods=['POST'])
def aggiungi_carico():
    dati = carica_dati()
    nuovo = request.json
    nuovo["timestamp"] = datetime.now().isoformat()
    dati["carichi"].append(nuovo)
    salva_dati(dati)
    return '', 204

@app.route('/api/giacenze')
def giacenze():
    sede = request.args.get("sede")
    dati = carica_dati()
    giacenza = {art[0]: 0 for art in ARTICOLI}

    for carico in dati["carichi"]:
        if carico["struttura"] == sede:
            for articolo in giacenza:
                giacenza[articolo] += carico.get(articolo, 0)

    for consumo in dati["consumi"]:
        if consumo["struttura"] == sede:
            for articolo in giacenza:
                giacenza[articolo] -= consumo.get(articolo, 0)

    return jsonify(giacenza)

@app.route('/api/report')
def api_report():
    sede = request.args.get("sede")
    mese = request.args.get("mese")  # Formato: YYYY-MM

    dati = carica_dati()
    totale = 0

    for carico in dati["carichi"]:
        if carico["struttura"] == sede and carico.get("timestamp", "").startswith(mese):
            for nome, prezzo in ARTICOLI:
                totale += carico.get(nome, 0) * prezzo

    return jsonify({"totale": round(totale, 2)})

if __name__ == '__main__':
    app.run(debug=True)