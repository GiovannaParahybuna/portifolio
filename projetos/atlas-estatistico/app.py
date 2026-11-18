"""
app.py
------
Aplicacao Flask do Atlas Estatistico das Nacoes.

- GET /            -> renderiza o dashboard (templates/index.html)
- GET /api/data    -> retorna JSON com registros, KPIs e rankings
                      (calculados por data_processing.load_dashboard_data)

Uso:
    pip install -r requirements.txt
    python3 app.py
    # abra http://127.0.0.1:5000
"""
import json

from flask import Flask, Response, render_template

from data_processing import load_dashboard_data

app = Flask(__name__)

# Os dados sao calculados uma vez, na subida do servidor, e ficam em cache
# em memoria. Para recarregar (ex.: apos trocar o CSV), reinicie o app.
_CACHE = None


def get_data():
    global _CACHE
    if _CACHE is None:
        _CACHE = load_dashboard_data()
    return _CACHE


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    data = get_data()
    # json.dumps manual (em vez de jsonify) para preservar acentos em pt-BR
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False)
    return Response(payload, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
