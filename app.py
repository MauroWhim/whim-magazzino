from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"carichi": [], "consumi": []}, f)

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
    "bevande": 0.45,
    "dolci": 0.06,
    "salati": 0.31
}

def carica_dati():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/inserisci")
def inserisci():
    return render_template("inserisci.html")

@app.route("/carichi")
def carichi():
    return render_template("carichi.html")

@app.route("/magazzino")
def magazzino():
    return render_template("magazzino.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/api/consumi", methods=["POST"])
def salva_consumi():
    dati = request.json
    tutti = carica_dati()
    tutti["consumi"].append(dati)
    salva_dati(tutti)
    return jsonify(ok=True)

@app.route("/api/carichi", methods=["POST"])
def salva_carico():
    dati = request.json
    tutti = carica_dati()
    tutti["carichi"].append(dati)
    salva_dati(tutti)
    return jsonify(ok=True)

@app.route("/api/giacenze")
def giacenze():
    sede = request.args.get("sede")
    dati = carica_dati()
    articoli = PREZZI.keys()
    giacenze = {}
    for art in articoli:
        carico = sum(c.get(art, 0) for c in dati["carichi"] if c.get("struttura") == sede)
        consumo = sum(c.get(art, 0) for c in dati["consumi"] if c.get("struttura") == sede)
        giacenze[art] = carico - consumo
    return jsonify(giacenze)

@app.route("/api/report-mensile")
def report_mensile():
    mese = request.args.get("mese")
    sede = request.args.get("sede")
    if not mese or not sede:
        return jsonify({"errore": "Parametri mancanti"}), 400

    dati = carica_dati()
    totale = 0.0
    for carico in dati["carichi"]:
        if carico.get("struttura") != sede:
            continue
        data_str = carico.get("data")
        if not data_str:
            continue
        try:
            data = datetime.strptime(data_str[:10], "%Y-%m-%d")
        except Exception:
            continue
        if data.strftime("%Y-%m") != mese:
            continue
        for art, prezzo in PREZZI.items():
            totale += carico.get(art, 0) * prezzo
    return jsonify({"totale": round(totale, 2)})

if __name__ == "__main__":
    app.run(debug=True)