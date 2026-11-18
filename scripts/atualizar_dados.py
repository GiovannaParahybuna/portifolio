"""Busca as classificações na API e grava data/classificacao.json. Token via variável de ambiente."""
import os, json, time, datetime as dt, requests
LIGAS = {"Brasil": ("Brasileirão", "BSA"), "Inglaterra": ("Premier League", "PL"), "Espanha": ("La Liga", "PD"),
         "Alemanha": ("Bundesliga", "BL1"), "Itália": ("Serie A", "SA"), "França": ("Ligue 1", "FL1"), "Portugal": ("Primeira Liga", "PPL")}
H = {"X-Auth-Token": os.environ["FOOTBALL_TOKEN"]}
dados = []
for pais, (nome, cod) in LIGAS.items():
    r = requests.get(f"https://api.football-data.org/v4/competitions/{cod}/standings", headers=H, timeout=30)
    r.raise_for_status()
    for s in r.json()["standings"]:
        if s.get("type", "TOTAL") != "TOTAL": continue
        for t in s["table"]:
            dados.append(dict(pais=pais, competicao=nome, time=t["team"]["name"], logo=t["team"]["crest"], pontos=t["points"],
                partidas=t["playedGames"], forma=t.get("form") or "", vitorias=t["won"], empates=t["draw"], derrotas=t["lost"],
                gols_marcados=t["goalsFor"], gols_sofridos=t["goalsAgainst"], saldo_de_gols=t["goalDifference"]))
    time.sleep(7)  # plano gratuito: 10 requisições/min
json.dump({"atualizado_em": dt.datetime.now().isoformat(timespec="minutes"), "dados": dados},
          open("data/classificacao.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(dados), "linhas gravadas")
