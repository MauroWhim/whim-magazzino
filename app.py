from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates")

DATA_FILE = "data.json"

# Inizializza file se non esiste
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"consumi": [], "carichi": []}, f)

# Carica e salva dati
def carica_dati():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

# Pagine HTML
@app.route("/")
def index():
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

# API: salva consumi
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

# API: salva carichi
@app.route("/api/carichi", methods=["POST"])
def salva_carichi():
    dati = request.json
    struttura = dati.get("struttura", "").strip()
    if not struttura:
        return jsonify({"error": "Struttura mancante"}), 400
    tutti_dati = carica_dati()
    tutti_dati["carichi"].append(dati)
    salva_dati(tutti_dati)
    return jsonify({"ok": True})

# API: giacenze
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

# API: report mensile
@app.route("/api/report-mensile")
def report_mensile():
    mese = request.args.get("mese")
    sede = request.args.get("sede")

    if not mese or not sede:
        return jsonify({"error": "Dati mancanti"}), 400

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
        "cialde": 0.22,
        "salati": 0.31,
        "dolci": 0.06,
        "bevande": 0.45
    }

    try:
        dati = carica_dati()
        totale = 0.0
        for carico in dati["carichi"]:
            if carico.get("struttura") != sede:
                continue
            data_carico = carico.get("data")
            if not data_carico or not data_carico.startswith(mese):
                continue
            for articolo, prezzo in prezzi.items():
                quantita = carico.get(articolo, 0)
                totale += quantita * prezzo

        return jsonify({"totale": round(totale, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Avvio app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)