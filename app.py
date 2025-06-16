
from flask import Flask, request, jsonify, Response
import json
import os
from datetime import datetime
import csv
import io

app = Flask(__name__)
DATA_FILE = "data.json"

# Inizializza file se non esiste
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"consumi": [], "carichi": []}, f)

def carica_dati():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

@app.route("/")
def index():
    return open("index.html").read()

@app.route("/inserisci")
def inserisci():
    return open("inserisci.html").read()

@app.route("/carichi")
def carichi():
    return open("carichi.html").read()

@app.route("/magazzino")
def magazzino():
    return open("magazzino.html").read()

@app.route("/report")
def report():
    return open("report.html").read()

@app.route("/api/consumi", methods=["POST"])
def salva_consumi():
    dati = request.json
    struttura = dati.get("struttura", "").strip()
    if not struttura:
        return jsonify({"error": "Struttura mancante"}), 400
    tutti_dati = carica_dati()
    tutti_dati["consumi"].append(dati)
    salva_dati(tutti_dati)
    return jsonify({"ok": True})

@app.route("/api/carichi", methods=["POST"])
def salva_carichi():
    dati = request.json
    struttura = dati.get("struttura", "").strip()
    if not struttura:
        return jsonify({"error": "Struttura mancante"}), 400
    tutti_dati = carica_dati()
    tutti_dati["carichi"].append(dati)
    salva_dati(tutti_dati)
    # Calcola costo
    prezzi = {
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
    costo = sum(dati.get(k, 0) * prezzi.get(k, 0) for k in prezzi)
    return jsonify({"ok": True, "costo": costo})

@app.route("/api/giacenze")
def api_giacenze():
    sede = request.args.get("sede", "").capitalize()
    if sede not in ["Prati", "Trastevere"]:
        return jsonify({"error": "Sede non valida"}), 400

    dati = carica_dati()
    articoli = [
        "bianche_matrimoniali", "bianche_singole", "bambu_matrimoniali", "bambu_singole",
        "federe", "bidet", "viso", "doccia", "tappeto",
        "cialde", "bevande", "dolci", "salati"
    ]
    giacenze = {}
    for articolo in articoli:
        carico = sum(c.get(articolo, 0) for c in dati["carichi"] if c.get("struttura") == sede)
        consumo = sum(c.get(articolo, 0) for c in dati["consumi"] if c.get("struttura") == sede)
        giacenze[articolo] = carico - consumo
    return jsonify(giacenze)

@app.route("/api/report")
def api_report():
    sede = request.args.get("sede", "").capitalize()
    mese = request.args.get("mese", "")
    if sede not in ["Prati", "Trastevere"] or not mese:
        return jsonify({"error": "Parametri mancanti"}), 400

    dati = carica_dati()
    prezzi = {
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

    totale = 0
    for carico in dati["carichi"]:
        if carico.get("struttura") == sede:
            data = carico.get("data", datetime.now().isoformat())[:7]
            if data == mese:
                for k in prezzi:
                    totale += carico.get(k, 0) * prezzi[k]

    return jsonify({"sede": sede, "mese": mese, "totale": round(totale, 2)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
