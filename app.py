
from flask import Flask, request, jsonify, Response, send_file
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"consumi": [], "carichi": []}, f)

def carica_dati():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

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

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/inserisci")
def inserisci():
    return send_file("inserisci.html")

@app.route("/carichi")
def carichi():
    return send_file("carichi.html")

@app.route("/magazzino")
def magazzino():
    return send_file("magazzino.html")

@app.route("/report")
def report():
    return send_file("report.html")

@app.route("/api/consumi", methods=["POST"])
def salva_consumi():
    dati = request.json
    struttura = dati.get("struttura", "").strip()
    if not struttura:
        return jsonify({"error": "Struttura mancante"}), 400
    tutti_dati = carica_dati()
    dati["timestamp"] = datetime.now().isoformat()
    tutti_dati["consumi"].append(dati)
    salva_dati(tutti_dati)
    return jsonify({"ok": True})

@app.route("/api/carichi", methods=["POST"])
def salva_carichi():
    dati = request.json
    struttura = dati.get("struttura", "").strip()
    if not struttura:
        return jsonify({"error": "Struttura mancante"}), 400
    dati["timestamp"] = datetime.now().isoformat()
    dati["totale"] = sum(dati.get(k, 0) * PREZZI.get(k, 0) for k in PREZZI)
    tutti_dati = carica_dati()
    tutti_dati["carichi"].append(dati)
    salva_dati(tutti_dati)
    return jsonify({"ok": True, "totale": dati["totale"]})

@app.route("/api/giacenze")
def api_giacenze():
    sede = request.args.get("sede", "").capitalize()
    if sede not in ["Prati", "Trastevere"]:
        return jsonify({"error": "Sede non valida"}), 400
    dati = carica_dati()
    articoli = list(PREZZI.keys())
    giacenze = {}
    for articolo in articoli:
        carico = sum(c.get(articolo, 0) for c in dati["carichi"] if c.get("struttura") == sede)
        consumo = sum(c.get(articolo, 0) for c in dati["consumi"] if c.get("struttura") == sede)
        giacenze[articolo] = carico - consumo
    return jsonify(giacenze)

@app.route("/api/report")
def api_report():
    sede = request.args.get("sede", "").capitalize()
    mese = request.args.get("mese")
    if sede not in ["Prati", "Trastevere"]:
        return jsonify({"error": "Sede non valida"}), 400
    if not mese:
        return jsonify({"error": "Mese mancante"}), 400
    dati = carica_dati()
    totale = 0
    for carico in dati["carichi"]:
        if carico.get("struttura") == sede and carico.get("timestamp", "").startswith(mese):
            totale += carico.get("totale", 0)
    return jsonify({"totale_mensile": round(totale, 2)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
