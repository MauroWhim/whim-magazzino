from flask import Flask, render_template, request, redirect, jsonify
import json
from datetime import datetime

app = Flask(__name__)

ARTICOLI = [
    "bianche_matrimoniali", "bianche_singole", "bambu_matrimoniali", "bambu_singole",
    "federe", "bidet", "viso", "doccia", "tappeto",
    "cialde", "salati", "dolci", "bevande"
]

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

DATA_FILE = "data.json"

# Funzione per caricare dati
def carica_dati():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"carichi": [], "consumi": []}

# Funzione per salvare dati
def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inserisci")
def inserisci():
    return render_template("inserisci.html", articoli=ARTICOLI)

@app.route("/carichi")
def carichi():
    return render_template("carichi.html", articoli=ARTICOLI, prezzi=PREZZI)

@app.route("/magazzino")
def magazzino():
    return render_template("magazzino.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/api/inserisci", methods=["POST"])
def api_inserisci():
    dati = carica_dati()
    nuovo = request.json
    nuovo["timestamp"] = datetime.now().isoformat()
    dati["consumi"].append(nuovo)
    salva_dati(dati)
    return "OK"

@app.route("/api/carichi", methods=["POST"])
def api_carichi():
    dati = carica_dati()
    nuovo = request.json
    nuovo["timestamp"] = datetime.now().isoformat()
    dati["carichi"].append(nuovo)
    salva_dati(dati)
    return "OK"

@app.route("/api/giacenze")
def api_giacenze():
    sede = request.args.get("sede")
    dati = carica_dati()
    giacenze = {art: 0 for art in ARTICOLI}

    for carico in dati["carichi"]:
        if carico["struttura"] == sede:
            for art in ARTICOLI:
                giacenze[art] += carico.get(art, 0)

    for consumo in dati["consumi"]:
        if consumo["struttura"] == sede:
            for art in ARTICOLI:
                giacenze[art] -= consumo.get(art, 0)

    return jsonify(giacenze)

@app.route("/api/report_mensile")
def api_report_mensile():
    mese = request.args.get("mese")
    sede = request.args.get("sede")
    dati = carica_dati()
    totale = 0.0

    for carico in dati["carichi"]:
        if carico["struttura"] == sede and carico["timestamp"].startswith(mese):
            for art in ARTICOLI:
                totale += carico.get(art, 0) * PREZZI.get(art, 0)

    return jsonify({"totale": round(totale, 2)})

if __name__ == "__main__":
    app.run(debug=True)