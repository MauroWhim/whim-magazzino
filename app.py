
from flask import Flask, request, jsonify, Response
import json, os, io
from datetime import datetime
import csv

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"consumi": [], "carichi": []}, f)

def carica_dati():
    with open(DATA_FILE) as f:
        return json.load(f)

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f)

@app.route("/")
def index():
    return open("index.html").read()

@app.route("/inserisci")
def inserisci(): return open("inserisci.html").read()

@app.route("/carichi")
def carichi(): return open("carichi.html").read()

@app.route("/magazzino")
def magazzino(): return open("magazzino.html").read()

@app.route("/report")
def report(): return open("report.html").read()

@app.route("/api/consumi", methods=["POST"])
def api_consumi():
    dati = carica_dati()
    nuovi = request.json
    dati["consumi"].append(nuovi)
    salva_dati(dati)
    return jsonify({"ok": True})

@app.route("/api/carichi", methods=["POST"])
def api_carichi():
    dati = carica_dati()
    nuovi = request.json
    dati["carichi"].append(nuovi)
    salva_dati(dati)
    return jsonify({"ok": True})

@app.route("/api/giacenze")
def giacenze():
    sede = request.args.get("sede", "")
    dati = carica_dati()
    articoli = ["bianche_matrimoniali"]
    giacenze = {}
    for a in articoli:
        carico = sum(c.get(a,0) for c in dati["carichi"] if c.get("struttura")==sede)
        consumo = sum(c.get(a,0) for c in dati["consumi"] if c.get("struttura")==sede)
        giacenze[a] = carico - consumo
    return jsonify(giacenze)

@app.route("/export-csv")
def export_csv():
    sede = request.args.get("sede", "")
    dati = carica_dati()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Data", "Struttura", "Articolo", "Quantità"])
    for r in dati["carichi"]:
        if r.get("struttura") == sede:
            for k in r:
                if k != "struttura":
                    writer.writerow([datetime.now().strftime("%Y-%m-%d"), sede, k, r[k]])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
