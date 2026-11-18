import requests
import json
import pandas as pd
from openpyxl import Workbook

campeonatos = {
    "Brasil": {
        "competicao": "Brasileirão",
        "codigo": "BSA"
    },
    "Inglaterra": {
        "competicao": "Premier League",
        "codigo": "PL"
    },
    "Espanha": {
        "competicao": "La Liga",
        "codigo": "PD"
    },
    "Alemanha": {
        "competicao": "Bundesliga",
        "codigo": "BL1"
    },
    "Itália": {
        "competicao": "Serie A",
        "codigo": "SA"
    },
    "França": {
        "competicao": "Ligue 1",
        "codigo": "FL1"
    },
    "Portugal": {
        "competicao": "Primeira Liga",
        "codigo": "PPL"
    }
    #"Europe": {
     #   "competicao" : "UEFA Champions League",
      #  "codigo": "CL"
    #},
    #"South America": {
     #   "competicao" : "Copa Libertadores",
      #   "codigo": "CLI"
    #}
}

import os
token = os.environ.get("FOOTBALL_TOKEN", "")  # nunca escreva o token no código

# o cabeçalho que a api exige para conexão
header = {"X-Auth-Token": token}

def buscar_classificacao(cod):
    url = f"https://api.football-data.org/v4/competitions/{cod}/standings"

    response = requests.get(url, headers=header)

    response.raise_for_status()

    return response.json()

def carregar_dados():

    classificacao_final = []

    for pais, info in campeonatos.items():

        cod = info["codigo"]
        name = info["competicao"]

        dados = buscar_classificacao(cod)

        print(dados["season"])

        print(f"{pais} - {name}")

        for classificacao in dados["standings"]:
            for time in classificacao["table"]:
                classificacao_final.append({
                    "pais": pais,
                    "competicao": name,
                    "time": time["team"]["name"],
                    "logo": time["team"]["crest"],
                    "pontos": time["points"],
                    "partidas": time["playedGames"],
                    "forma": time["form"],
                    "vitorias": time["won"],
                    "empates": time["draw"],
                    "derrotas": time["lost"],
                    "gols_marcados": time["goalsFor"],
                    "gols_sofridos": time["goalsAgainst"],
                    "saldo_de_gols": time["goalDifference"]
                })

    df = pd.DataFrame(classificacao_final)

    df.to_csv("dados_api.csv", index=False)

    return df

# executa a coleta somente quando football.py for executado diretamente
if __name__ == "__main__":
    carregar_dados()

#df.to_excel("dados_api.xlsx", index=False)

#dados = response.json()
#print(json.dumps(dados, indent=4, ensure_ascii=False))
