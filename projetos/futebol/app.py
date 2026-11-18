from dash import Dash, html, dcc, dash_table, Input, Output
import pandas as pd

# ---------------------------------------------------------------------------
# Carregamento e preparação dos dados
# ---------------------------------------------------------------------------

df = pd.read_csv("dados_api.csv")

COL_CAMPEONATO = "competicao"

if COL_CAMPEONATO not in df.columns:
    df[COL_CAMPEONATO] = "Geral"

if "forma" not in df.columns:
    df["forma"] = ""

if "pais" not in df.columns:
    df["pais"] = ""

# ---------------------------------------------------------------------------
# Preparação das logos
# ---------------------------------------------------------------------------

df["logo"] = df["logo"].fillna("").apply(
    lambda url: (
        f'<img src="{url}" class="team-logo">'
        if url
        else ""
    )
)

# ---------------------------------------------------------------------------
# Ordenação da classificação
# ---------------------------------------------------------------------------

df = df.sort_values(
    by=[
        COL_CAMPEONATO,
        "pontos",
        "saldo_de_gols",
        "gols_marcados"
    ],
    ascending=[True, False, False, False]
).reset_index(drop=True)

df["posicao"] = (
    df.groupby(COL_CAMPEONATO)
    .cumcount()
    + 1
)

# ---------------------------------------------------------------------------
# Forma recente
# ---------------------------------------------------------------------------

CORES_FORMA = {
    "W": "#22c55e",
    "D": "#94a3b8",
    "L": "#ef4444"
}


def formatar_forma(sequencia):
    if not isinstance(sequencia, str) or not sequencia:
        return ""

    return "".join(
        f'<span class="form-dot" '
        f'style="background:{CORES_FORMA.get(letra, "#cbd5e1")}" '
        f'title="{letra}"></span>'
        for letra in sequencia
    )


df["forma"] = df["forma"].apply(formatar_forma)

# ---------------------------------------------------------------------------
# Colunas
# ---------------------------------------------------------------------------

COLUNAS = [
    {"name": "#", "id": "posicao"},
    {"name": "", "id": "logo", "presentation": "markdown"},
    {"name": "Time", "id": "time"},
    {"name": "PTS", "id": "pontos"},
    {"name": "PJ", "id": "partidas"},
    {"name": "V", "id": "vitorias"},
    {"name": "E", "id": "empates"},
    {"name": "D", "id": "derrotas"},
    {"name": "GP", "id": "gols_marcados"},
    {"name": "GC", "id": "gols_sofridos"},
    {"name": "SG", "id": "saldo_de_gols"},
    {"name": "Forma", "id": "forma", "presentation": "markdown"},
]


# ---------------------------------------------------------------------------
# Tabela
# ---------------------------------------------------------------------------

def montar_tabela(dados_campeonato):

    total_times = len(dados_campeonato)

    return dash_table.DataTable(
        data=dados_campeonato.to_dict("records"),
        columns=COLUNAS,

        markdown_options={
            "html": True
        },

        page_size=20,

        sort_action="native",

        style_table={
            "overflowX": "auto",
            "minWidth": "100%"
        },

        style_as_list_view=True,

        style_header={
            "backgroundColor": "#f8fafc",
            "color": "#64748b",
            "fontWeight": "700",
            "textAlign": "center",
            "border": "none",
            "borderBottom": "1px solid #e2e8f0",
            "height": "46px",
            "fontSize": "11px",
            "letterSpacing": "0.08em"
        },

        style_cell={
            "textAlign": "center",
            "padding": "12px 10px",
            "fontFamily": "'Inter', 'Segoe UI', sans-serif",
            "fontSize": "13px",
            "color": "#334155",
            "border": "none",
            "borderBottom": "1px solid #f1f5f9",
            "height": "52px",
            "minWidth": "42px"
        },

        style_cell_conditional=[
            {
                "if": {"column_id": "time"},
                "textAlign": "left",
                "minWidth": "180px",
                "fontWeight": "600",
                "color": "#0f172a"
            },
            {
                "if": {"column_id": "logo"},
                "width": "45px",
                "minWidth": "45px"
            },
            {
                "if": {"column_id": "posicao"},
                "width": "42px",
                "fontWeight": "700"
            },
            {
                "if": {"column_id": "pontos"},
                "fontWeight": "800",
                "color": "#0f172a"
            },
            {
                "if": {"column_id": "forma"},
                "width": "105px",
                "minWidth": "105px",
                "whiteSpace": "nowrap"
            }
        ],

        style_data_conditional=[

            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#fafbfc"
            },

            {
                "if": {
                    "filter_query": "{posicao} = 1"
                },
                "backgroundColor": "#fffbeb",
                "fontWeight": "600",
                "borderLeft": "4px solid #f59e0b"
            },

            {
                "if": {
                    "filter_query": "{posicao} >= 2 && {posicao} <= 4"
                },
                "backgroundColor": "#f0fdf4",
                "borderLeft": "4px solid #22c55e"
            },

            {
                "if": {
                    "filter_query": f"{{posicao}} > {total_times - 4}"
                },
                "backgroundColor": "#fef2f2",
                "borderLeft": "4px solid #ef4444"
            },

            {
                "if": {
                    "filter_query": "{saldo_de_gols} > 0",
                    "column_id": "saldo_de_gols"
                },
                "color": "#16a34a",
                "fontWeight": "700"
            },

            {
                "if": {
                    "filter_query": "{saldo_de_gols} < 0",
                    "column_id": "saldo_de_gols"
                },
                "color": "#dc2626",
                "fontWeight": "700"
            }
        ]
    )


# ---------------------------------------------------------------------------
# Campeonatos
# ---------------------------------------------------------------------------

campeonatos = sorted(
    df[COL_CAMPEONATO].dropna().unique()
)

if "pais" in df.columns:

    pais_por_competicao = (
        df.drop_duplicates(COL_CAMPEONATO)
        .set_index(COL_CAMPEONATO)["pais"]
        .to_dict()
    )

    rotulo_aba = {
        campeonato: (
            f"{campeonato} • {pais_por_competicao.get(campeonato, '')}"
            if pais_por_competicao.get(campeonato)
            else campeonato
        )
        for campeonato in campeonatos
    }

else:

    rotulo_aba = {
        campeonato: campeonato
        for campeonato in campeonatos
    }


# ---------------------------------------------------------------------------
# Informações gerais
# ---------------------------------------------------------------------------

total_campeonatos = len(campeonatos)
total_times = df["time"].nunique()

data_atualizacao = pd.Timestamp.now().strftime(
    "%d/%m/%Y às %H:%M"
)


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------

app = Dash(__name__)

app.title = "Football Analytics"

app.layout = html.Div(

    id="app-container",
    className="app-container light-theme",

    children=[

        # ================================================================
        # HEADER
        # ================================================================

        html.Header(

            className="main-header",

            children=[

                html.Div(

                    className="header-content",

                    children=[

                        html.Div(

                            className="brand",

                            children=[

                                html.Div(
                                    "⚽",
                                    className="brand-icon"
                                ),

                                html.Div(
                                    children=[
                                        html.H1(
                                            "Football Analytics"
                                        ),
                                        html.P(
                                            "Classificação dos principais campeonatos"
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.Div(

                            className="header-actions",

                            children=[

                                html.Div(
                                    className="source-badge",
                                    children=[
                                        html.Span(
                                            "●",
                                            className="source-dot"
                                        ),
                                        html.Span(
                                            "Dados atualizados via API"
                                        )
                                    ]
                                ),

                                html.Button(
                                    "🌙",
                                    id="theme-button",
                                    className="theme-button",
                                    title="Alternar tema"
                                )
                            ]
                        )
                    ]
                )
            ]
        ),

        # ================================================================
        # CONTEÚDO
        # ================================================================

        html.Main(

            className="main-content",

            children=[

                # --------------------------------------------------------
                # INTRO
                # --------------------------------------------------------

                html.Div(

                    className="page-intro",

                    children=[

                        html.Div(

                            children=[

                                html.Div(
                                    "CAMPEONATOS",
                                    className="section-label"
                                ),

                                html.H2(
                                    "Classificação"
                                ),

                                html.P(
                                    "Acompanhe a classificação, desempenho "
                                    "e forma recente dos clubes."
                                )
                            ]
                        ),

                        html.Div(

                            className="update-info",

                            children=[

                                html.Span(
                                    "Última atualização"
                                ),

                                html.Strong(
                                    data_atualizacao
                                )
                            ]
                        )
                    ]
                ),

                # --------------------------------------------------------
                # CARDS
                # --------------------------------------------------------

                html.Div(

                    className="stats-grid",

                    children=[

                        html.Div(
                            className="stat-card",
                            children=[
                                html.Div(
                                    "🏆",
                                    className="stat-icon"
                                ),
                                html.Div(
                                    children=[
                                        html.Span(
                                            "CAMPEONATOS"
                                        ),
                                        html.Strong(
                                            str(total_campeonatos)
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            className="stat-card",
                            children=[
                                html.Div(
                                    "👥",
                                    className="stat-icon"
                                ),
                                html.Div(
                                    children=[
                                        html.Span(
                                            "CLUBES"
                                        ),
                                        html.Strong(
                                            str(total_times)
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.Div(
                            className="stat-card",
                            children=[
                                html.Div(
                                    "📡",
                                    className="stat-icon"
                                ),
                                html.Div(
                                    children=[
                                        html.Span(
                                            "FONTE"
                                        ),
                                        html.Strong(
                                            "football-data.org"
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                # --------------------------------------------------------
                # RANKING
                # --------------------------------------------------------

                html.Div(

                    className="ranking-card",

                    children=[

                        dcc.Tabs(

                            id="tabs-campeonatos",

                            value=campeonatos[0],

                            className="championship-tabs",

                            children=[

                                dcc.Tab(

                                    label=rotulo_aba[camp],

                                    value=camp,

                                    className="championship-tab",

                                    selected_className="championship-tab-selected",

                                    children=[

                                        html.Div(

                                            className="table-container",

                                            children=[

                                                html.Div(

                                                    className="table-title",

                                                    children=[

                                                        html.Div(
                                                            children=[
                                                                html.Span(
                                                                    "CLASSIFICAÇÃO",
                                                                    className="table-label"
                                                                ),
                                                                html.H3(
                                                                    rotulo_aba[camp]
                                                                )
                                                            ]
                                                        ),

                                                        html.Div(
                                                            f"{len(df[df[COL_CAMPEONATO] == camp])} clubes",
                                                            className="club-count"
                                                        )
                                                    ]
                                                ),

                                                montar_tabela(
                                                    df[
                                                        df[COL_CAMPEONATO] == camp
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                )

                                for camp in campeonatos
                            ]
                        )
                    ]
                ),

                # --------------------------------------------------------
                # LEGENDA
                # --------------------------------------------------------

                html.Div(

                    className="legend-card",

                    children=[

                        html.Div(
                            "LEGENDA",
                            className="legend-title"
                        ),

                        html.Div(

                            className="legend-items",

                            children=[

                                html.Div(
                                    [
                                        html.Span(
                                            className="legend-dot leader"
                                        ),
                                        "Líder"
                                    ],
                                    className="legend-item"
                                ),

                                html.Div(
                                    [
                                        html.Span(
                                            className="legend-dot classification"
                                        ),
                                        "Zona de classificação"
                                    ],
                                    className="legend-item"
                                ),

                                html.Div(
                                    [
                                        html.Span(
                                            className="legend-dot relegation"
                                        ),
                                        "Zona de rebaixamento"
                                    ],
                                    className="legend-item"
                                ),

                                html.Div(
                                    [
                                        html.Span(
                                            className="form-example win"
                                        ),
                                        "Vitória"
                                    ],
                                    className="legend-item"
                                ),

                                html.Div(
                                    [
                                        html.Span(
                                            className="form-example draw"
                                        ),
                                        "Empate"
                                    ],
                                    className="legend-item"
                                ),

                                html.Div(
                                    [
                                        html.Span(
                                            className="form-example loss"
                                        ),
                                        "Derrota"
                                    ],
                                    className="legend-item"
                                )
                            ]
                        )
                    ]
                ),

                # --------------------------------------------------------
                # FONTE
                # --------------------------------------------------------

                html.Footer(

                    className="data-source",

                    children=[

                        html.Div(

                            className="source-main",

                            children=[

                                html.Div(
                                    "DATA SOURCE",
                                    className="source-label"
                                ),

                                html.Div(

                                    className="source-content",

                                    children=[

                                        html.Strong(
                                            "football-data.org"
                                        ),

                                        html.Span(
                                            " — Dados de competições e "
                                            "classificações obtidos através "
                                            "da API utilizada pelo projeto."
                                        )
                                    ]
                                )
                            ]
                        ),

                        html.Div(

                            className="source-tech",

                            children=[
                                html.Span("API"),
                                html.Span("•"),
                                html.Span("CSV"),
                                html.Span("•"),
                                html.Span("Python")
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)


# ---------------------------------------------------------------------------
# Alternância de tema
# ---------------------------------------------------------------------------

@app.callback(
    Output("app-container", "className"),
    Output("theme-button", "children"),
    Input("theme-button", "n_clicks"),
    prevent_initial_call=True
)
def alternar_tema(n_clicks):

    if n_clicks and n_clicks % 2 == 1:
        return "app-container dark-theme", "☀️"

    return "app-container light-theme", "🌙"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
