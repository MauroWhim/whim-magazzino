from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"carichi": [], "consumi": []}, f)

def carica_dati():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

@app.route("/")
def home():
    return open("index.html").read()

@app.route("/carichi")
def carichi():
    return open("carichi.html").read()

@app.route("/magazzino")
def magazzino():
    return open("magazzino.html").read()

@app.route("/inserisci")
def inserisci():
    return open("inserisci.html").read()

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
    dati["data"] = datetime.now().strftime("%Y-%m-%d")
    tutti_dati = carica_dati()
    tutti_dati["carichi"].append(dati)
    salva_dati(tutti_dati)
    return jsonify({"ok": True})

@app.route("/api/giacenze")
def api_giacenze():
    sede = request.args.get("sede", "").capitalize()
    if sede not in ["Prati", "Trastevere"]:
        return jsonify({"error": "Sede non valida"}), 400
    dati = carica_dati()
    articoli = [
        "bianche_matrimoniali", "bianche_singole",
        "bambu_matrimoniali", "bambu_singole",
        "federe", "bidet", "viso", "doccia", "tappeto",
        "cialde", "bevande", "dolci", "salati"
    ]
    giacenze = {}
    for articolo in articoli:
        carico = sum(c.get(articolo, 0) for c in dati["carichi"] if c.get("struttura") == sede)
        consumo = sum(c.get(articolo, 0) for c in dati["consumi"] if c.get("struttura") == sede)
        giacenze[articolo] = carico - consumo
    return jsonify(giacenze)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)