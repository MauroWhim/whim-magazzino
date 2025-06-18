from flask import Flask, render_template, request, redirect, jsonify
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data.json"

PREZZI = {
    "bianche_matrimoniali": 0.90,
    "bianche_singole": 0.80,
    "bambu_matrimoniali": 1.20,
    "bambu_singole": 1.00,
    "federe": 0.60,
    "viso": 0.60,
    "bidet": 0.40,
    "doccia": 1.20,
    "tappeto": 0.70,
    "cialde": 0.22,
    "snack_s": 0.31,
    "dolci": 0.06,
    "bevande": 0.45,
}

def carica_dati():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"carichi": [], "consumi": []}

def salva_dati(dati):
    with open(DATA_FILE, "w") as f:
        json.dump(dati, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/carichi", methods=["GET", "POST"])
def carichi():
    if request.method == "POST":
        sede = request.form["sede"]
        data = datetime.now().strftime("%Y-%m-%d")
        voci = {k: int(request.form.get(k, 0)) for k in PREZZI}
        costo = sum(voci[k] * PREZZI[k] for k in PREZZI)
        record = {"sede": sede, "data": data, "voci": voci, "costo": round(costo, 2)}
        dati = carica_dati()
        dati["carichi"].append(record)
        salva_dati(dati)
        return redirect("/carichi")
    return render_template("carichi.html", prezzi=PREZZI)

@app.route("/inserisci", methods=["GET", "POST"])
def inserisci():
    if request.method == "POST":
        sede = request.form["sede"]
        data = datetime.now().strftime("%Y-%m-%d")
        voci = {k: int(request.form.get(k, 0)) for k in PREZZI}
        record = {"sede": sede, "data": data, "voci": voci}
        dati = carica_dati()
        dati["consumi"].append(record)
        salva_dati(dati)
        return redirect("/inserisci")
    return render_template("inserisci.html", prezzi=PREZZI)

@app.route("/magazzino")
def magazzino():
    sede = request.args.get("sede", "Prati")
    dati = carica_dati()
    giacenze = {k: 0 for k in PREZZI}
    for carico in dati["carichi"]:
        if carico["sede"] == sede:
            for k in carico["voci"]:
                giacenze[k] += carico["voci"][k]
    for consumo in dati["consumi"]:
        if consumo["sede"] == sede:
            for k in consumo["voci"]:
                giacenze[k] -= consumo["voci"][k]
    return render_template("magazzino.html", sede=sede, giacenze=giacenze)

@app.route("/report", methods=["GET"])
def report():
    dati = carica_dati()
    mese = request.args.get("mese")
    sede = request.args.get("sede")
    totale = 0

    if mese and sede:
        for carico in dati["carichi"]:
            try:
                data = datetime.strptime(carico["data"][:7], "%Y-%m")
                mese_dt = datetime.strptime(mese, "%Y-%m")
                if carico["sede"] == sede and data.year == mese_dt.year and data.month == mese_dt.month:
                    totale += carico["costo"]
            except Exception as e:
                print("Errore data:", e)

    return render_template("report.html", mese=mese, sede=sede, totale=round(totale, 2))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)