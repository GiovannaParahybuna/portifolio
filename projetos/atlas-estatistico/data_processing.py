"""
data_processing.py
--------------------
Modulo com toda a logica de carregamento e calculo estatistico.
Nao roda sozinho: e importado pelo app.py, que expoe o resultado
via API Flask (rota /api/data) para o dashboard no navegador.
"""

import json
import os

import pandas as pd
import pycountry


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "country_stats-selected-columns.csv")


# ---------------------------------------------------------
# Codigos ISO manuais para nomes que podem nao ser
# reconhecidos corretamente pelo pycountry.
# ---------------------------------------------------------

MANUAL_ISO3 = {
    "Ivory Coast": "CIV",
    "Czech Republic": "CZE",
    "South Korea": "KOR",
    "North Korea": "PRK",
    "Republic of the Congo": "COG",
    "Democratic Republic of the Congo": "COD",
    "Eswatini": "SWZ",
    "Myanmar": "MMR",
    "United States": "USA",
    "Vatican City": "VAT",
    "Palestine": "PSE",
    "Cape Verde": "CPV",
    "Timor-Leste": "TLS",
    "Micronesia": "FSM",
    "Brunei": "BRN",
    "Russia": "RUS",
    "Laos": "LAO",
    "Iran": "IRN",
    "Syria": "SYR",
    "Venezuela": "VEN",
    "Bolivia": "BOL",
    "Tanzania": "TZA",
    "Moldova": "MDA",
    "Vietnam": "VNM",
    "United Kingdom": "GBR",
    "South Sudan": "SSD",
    "Turkey": "TUR",
}


MANUAL_ISO2 = {
    "Ivory Coast": "CI",
    "Czech Republic": "CZ",
    "South Korea": "KR",
    "North Korea": "KP",
    "Republic of the Congo": "CG",
    "Democratic Republic of the Congo": "CD",
    "Eswatini": "SZ",
    "Myanmar": "MM",
    "United States": "US",
    "Vatican City": "VA",
    "Palestine": "PS",
    "Cape Verde": "CV",
    "Timor-Leste": "TL",
    "Micronesia": "FM",
    "Brunei": "BN",
    "Russia": "RU",
    "Laos": "LA",
    "Iran": "IR",
    "Syria": "SY",
    "Venezuela": "VE",
    "Bolivia": "BO",
    "Tanzania": "TZ",
    "Moldova": "MD",
    "Vietnam": "VN",
    "United Kingdom": "GB",
    "South Sudan": "SS",
    "Turkey": "TR",
}


# ---------------------------------------------------------
# Busca de pais
# ---------------------------------------------------------

def _get_country(name: str):
    """
    Tenta encontrar um pais no pycountry.
    Primeiro usa busca exata e depois fuzzy search.
    """

    if not name or pd.isna(name):
        return None

    name = str(name).strip()

    try:
        return pycountry.countries.get(name=name)
    except Exception:
        pass

    try:
        return pycountry.countries.search_fuzzy(name)[0]
    except Exception:
        return None


# ---------------------------------------------------------
# ISO-3
# ---------------------------------------------------------

def _get_iso3(name: str):
    if not name or pd.isna(name):
        return None

    name = str(name).strip()

    if name in MANUAL_ISO3:
        return MANUAL_ISO3[name]

    country = _get_country(name)

    if country:
        return country.alpha_3

    return None


# ---------------------------------------------------------
# ISO-2
# ---------------------------------------------------------

def _get_iso2(name: str):
    if not name or pd.isna(name):
        return None

    name = str(name).strip()

    if name in MANUAL_ISO2:
        return MANUAL_ISO2[name]

    country = _get_country(name)

    if country:
        return country.alpha_2

    return None


# ---------------------------------------------------------
# Bandeira
# ---------------------------------------------------------

def _flag_emoji(iso2: str):
    """
    Converte codigo ISO-2 em emoji de bandeira.

    Exemplo:
        BR -> 🇧🇷
        US -> 🇺🇸
        FR -> 🇫🇷
    """

    if not iso2 or pd.isna(iso2):
        return ""

    iso2 = str(iso2).strip().upper()

    if len(iso2) != 2:
        return ""

    if not all("A" <= char <= "Z" for char in iso2):
        return ""

    return "".join(
        chr(127397 + ord(char))
        for char in iso2
    )


# ---------------------------------------------------------
# Faixa de IDH
# ---------------------------------------------------------

def _hdi_tier(x):
    if pd.isna(x):
        return None

    if x >= 0.8:
        return "Muito Alto"

    if x >= 0.7:
        return "Alto"

    if x >= 0.55:
        return "Medio"

    return "Baixo"


# ---------------------------------------------------------
# Ranking Top 10
# ---------------------------------------------------------

def _top10(df: pd.DataFrame, col: str):

    cols = [
        "country",
        "flag",
        col
    ]

    sub = (
        df
        .dropna(subset=[col])
        .sort_values(col, ascending=False)
        .head(10)
    )

    return (
        sub[cols]
        .rename(columns={col: "value"})
        .to_dict("records")
    )


# ---------------------------------------------------------
# Carregamento principal
# ---------------------------------------------------------

def load_dashboard_data(csv_path: str = INPUT_CSV) -> dict:
    """
    Le o CSV, calcula colunas derivadas, KPIs e rankings,
    e retorna um dicionario pronto para ser serializado
    em JSON pela API Flask.
    """

    # -----------------------------------------------------
    # Carrega CSV
    # -----------------------------------------------------

    df = pd.read_csv(csv_path)

    # -----------------------------------------------------
    # Padronizacao dos nomes das colunas
    # -----------------------------------------------------

    df = df.rename(columns={
        "Country name": "country",
        "Total in km2": "total_km2",
        "Land in km2": "land_km2",
        "Inland water in km2": "water_km2",
        "% water": "pct_water",
        "Population": "population",
        "% of world population": "pct_world_pop",
        "Population density": "density",
        "HDI": "hdi",
        "Fertility rate": "fertility",
    })

    # -----------------------------------------------------
    # Garante que as principais variaveis numericas sejam
    # realmente numericas.
    # -----------------------------------------------------

    numeric_columns = [
        "total_km2",
        "land_km2",
        "water_km2",
        "pct_water",
        "population",
        "pct_world_pop",
        "density",
        "hdi",
        "fertility",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # -----------------------------------------------------
    # Identificacao dos paises
    # -----------------------------------------------------

    df["country"] = (
        df["country"]
        .astype(str)
        .str.strip()
    )

    df["iso3"] = df["country"].apply(_get_iso3)

    df["iso2"] = df["country"].apply(_get_iso2)

    df["flag"] = df["iso2"].apply(_flag_emoji)

    # -----------------------------------------------------
    # Classificacao do IDH
    # -----------------------------------------------------

    df["hdi_tier"] = df["hdi"].apply(_hdi_tier)

    # -----------------------------------------------------
    # Participacao na agua interior mundial
    # -----------------------------------------------------

    total_water = df["water_km2"].sum()

    if total_water > 0:
        df["pct_world_water"] = (
            df["water_km2"] /
            total_water *
            100
        )
    else:
        df["pct_world_water"] = None

    # -----------------------------------------------------
    # KPIs
    # -----------------------------------------------------

    max_hdi_idx = df["hdi"].idxmax()
    min_hdi_idx = df["hdi"].idxmin()
    max_population_idx = df["population"].idxmax()
    max_density_idx = df["density"].idxmax()
    max_area_idx = df["total_km2"].idxmax()
    max_water_idx = df["pct_world_water"].idxmax()

    kpis = {
        "n_countries": int(
            df["country"].nunique()
        ),

        "total_population": float(
            df["population"].sum()
        ),

        "total_land_km2": float(
            df["land_km2"].sum()
        ),

        "avg_density": float(
            df["density"].mean()
        ),

        "median_hdi": float(
            df["hdi"].median()
        ),

        "avg_fertility": float(
            df["fertility"].mean()
        ),

        "corr_hdi_fertility": float(
            df["hdi"].corr(df["fertility"])
        ),

        "max_hdi_country":
            df.loc[max_hdi_idx, "country"],

        "max_hdi_flag":
            df.loc[max_hdi_idx, "flag"],

        "max_hdi_value":
            float(df["hdi"].max()),

        "min_hdi_country":
            df.loc[min_hdi_idx, "country"],

        "min_hdi_flag":
            df.loc[min_hdi_idx, "flag"],

        "min_hdi_value":
            float(df["hdi"].min()),

        "most_populous":
            df.loc[max_population_idx, "country"],

        "most_populous_flag":
            df.loc[max_population_idx, "flag"],

        "most_populous_value":
            float(df["population"].max()),

        "most_dense":
            df.loc[max_density_idx, "country"],

        "most_dense_flag":
            df.loc[max_density_idx, "flag"],

        "most_dense_value":
            float(df["density"].max()),

        "largest_country":
            df.loc[max_area_idx, "country"],

        "largest_country_flag":
            df.loc[max_area_idx, "flag"],

        "largest_country_value":
            float(df["total_km2"].max()),

        "most_world_water":
            df.loc[max_water_idx, "country"],

        "most_world_water_flag":
            df.loc[max_water_idx, "flag"],

        "most_world_water_value":
            float(df["pct_world_water"].max()),
    }

    # -----------------------------------------------------
    # Rankings
    # -----------------------------------------------------

    rankings = {
        "top_area":
            _top10(df, "total_km2"),

        "top_population":
            _top10(df, "population"),

        "top_hdi":
            _top10(df, "hdi"),

        "top_world_water":
            _top10(df, "pct_world_water"),
    }

    # -----------------------------------------------------
    # Conversao final para JSON
    #
    # to_json converte NaN em null corretamente.
    # Isso evita problemas com json.dumps(...,
    # allow_nan=False) no app.py.
    # -----------------------------------------------------

    records = json.loads(
        df.to_json(
            orient="records"
        )
    )

    return {
        "records": records,
        "kpis": kpis,
        "rankings": rankings
    }