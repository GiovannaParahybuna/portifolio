import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, State, callback, ctx, ALL

# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------
df = pd.read_csv("Amazon.csv")
df["OrderDate"] = pd.to_datetime(df["OrderDate"])
df["YearMonth"] = df["OrderDate"].dt.to_period("M").dt.to_timestamp()

COLORS = [
    "#007C83",  # Teal
    "#E58A2B",  # Laranja
    "#3BAA68",  # Verde
    "#8A5BA8",  # Roxo
    "#D04A45",  # Vermelho
    "#159A91",  # Turquesa
]

# ---------------------------------------------------------------------------
# Definição dos temas
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#FFFFFF",
        "panel_bg": "#FAFAFA",
        "card_bg": "#F8F9FA",
        "text": "#1A1A1A",
        "subtext": "#666666",
        "border": "#EEEEEE",
        "plot_template": "plotly_white",
        "toggle_label": "🌙 Modo Escuro",
    },
    "dark": {
        "bg": "#121212",
        "panel_bg": "#1A1A1A",
        "card_bg": "#1E1E1E",
        "text": "#F5F5F5",
        "subtext": "#AAAAAA",
        "border": "#333333",
        "plot_template": "plotly_dark",
        "toggle_label": "☀️ Modo Claro",
    },
}

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Amazon Sales - Dashboard"

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html, body {
                margin: 0;
                min-height: 100%;
                transition: background-color 0.2s ease, color 0.2s ease;
            }

            /* Fundo do html/body acompanha o tema para não sobrar
               nenhuma faixa branca fora do app-container */
            html[data-theme="light"], html[data-theme="light"] body {
                background-color: #FFFFFF;
            }
            html[data-theme="dark"], html[data-theme="dark"] body {
                background-color: #121212;
            }

            .card-grafico {
                width: 32%;
                min-width: 320px;
                border-radius: 10px;
                box-sizing: border-box;
                padding: 10px;
                transition: background-color 0.2s ease, border-color 0.2s ease;
            }

            /* Cor de fundo/borda dos cards de gráfico por tema */
            html[data-theme="light"] .card-grafico {
                background-color: #F8F9FA;
                border: 1px solid #EEEEEE;
            }
            html[data-theme="dark"] .card-grafico {
                background-color: #1E1E1E;
                border: 1px solid #333333;
            }

            /* Deixa os dropdowns do Dash acompanharem o tema escuro */
            [data-theme="dark"] .Select-control,
            [data-theme="dark"] .Select-menu-outer,
            [data-theme="dark"] .Select-value-label,
            [data-theme="dark"] .Select-input > input {
                background-color: #2A2A2A !important;
                color: #F5F5F5 !important;
                border-color: #444 !important;
            }
            [data-theme="dark"] .Select-placeholder {
                color: #AAAAAA !important;
            }
            [data-theme="dark"] .DateInput_input {
                background-color: #2A2A2A !important;
                color: #F5F5F5 !important;
            }

            /* Indica visualmente que os gráficos são clicáveis (cross-filter) */
            .card-grafico .js-plotly-plot .plotly .cursor-pointer {
                cursor: pointer;
            }
            .chip-remover:hover {
                filter: brightness(0.92);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div(
    id="app-container",
    children=[

        dcc.Store(id="theme-store", data="light"),
        dcc.Store(id="cross-filter-store", data={}),
        html.Div(id="theme-sync", style={"display": "none"}),

        # Cabeçalho
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Amazon Sales Dashboard", style={"margin": 0}),
                        html.P(
                            "Visão Geral de vendas, produtos e clientes · clique em um gráfico para filtrar os demais",
                            id="subtitle",
                            style={"marginTop": "4px"},
                        ),
                    ]
                ),
                html.Button(
                    THEMES["light"]["toggle_label"],
                    id="theme-toggle-btn",
                    n_clicks=0,
                    style={
                        "height": "40px",
                        "padding": "0 16px",
                        "borderRadius": "20px",
                        "border": "1px solid #ccc",
                        "cursor": "pointer",
                        "fontSize": "14px",
                        "backgroundColor": "#fff",
                    },
                ),
            ],
            style={
                "padding": "20px 30px",
                "borderBottom": "1px solid #eee",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
            },
            id="header",
        ),

        # Filtros
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Country"),
                        dcc.Dropdown(
                            id="f-country",
                            options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
                            value=[],
                            multi=True,
                            placeholder="Todos os países",
                        ),
                    ],
                    style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"},
                ),
                html.Div(
                    [
                        html.Label("Categoria"),
                        dcc.Dropdown(
                            id="f-category",
                            options=[{"label": c, "value": c} for c in sorted(df["Category"].unique())],
                            value=[],
                            multi=True,
                            placeholder="Todas as categorias",
                        ),
                    ],
                    style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"},
                ),
                html.Div(
                    [
                        html.Label("Status do Pedido"),
                        dcc.Dropdown(
                            id="f-status",
                            options=[{"label": s, "value": s} for s in sorted(df["OrderStatus"].unique())],
                            value=[],
                            multi=True,
                            placeholder="Todos os status",
                        ),
                    ],
                    style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"},
                ),
                html.Div(
                    [
                        html.Label("Período"),
                        dcc.DatePickerRange(
                            id="f-periodo",
                            min_date_allowed=df["OrderDate"].min(),
                            max_date_allowed=df["OrderDate"].max(),
                            start_date=df["OrderDate"].min(),
                            end_date=df["OrderDate"].max(),
                            display_format="DD/MM/YYYY",
                        ),
                    ],
                    style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"},
                ),
            ],
            id="filtros",
            style={"padding": "20px 30px", "borderBottom": "1px solid #eee"},
        ),

        html.Div(
            id="cross-filter-bar",
            children=[
                html.Div(
                    id="cross-filter-chips",
                    children=[],
                    style={"display": "flex", "flexWrap": "wrap", "gap": "8px", "alignItems": "center"},
                ),
                html.Button(
                    "Limpar tudo",
                    id="clear-filters-btn",
                    n_clicks=0,
                    style={
                        "padding": "6px 14px",
                        "borderRadius": "16px",
                        "border": "none",
                        "backgroundColor": "#EF5350",
                        "color": "white",
                        "cursor": "pointer",
                        "fontSize": "12px",
                        "display": "none",
                    },
                ),
            ],
            style={
                "padding": "14px 30px 0 30px",
                "display": "flex", "flexWrap": "wrap",
                "gap": "8px", "alignItems": "center", "minHeight": "20px",
            },
        ),

        html.Div(id="kpis", style={"padding": "20px 30px", "display": "flex", "gap": "20px"}),

        html.Div(
            [
                html.Div([dcc.Graph(id="fig-linha")], className="card-grafico"),
                html.Div([dcc.Graph(id="fig-pais")], className="card-grafico"),
                html.Div([dcc.Graph(id="fig-pizza")], className="card-grafico"),
                html.Div([dcc.Graph(id="fig-produtos")], className="card-grafico"),
                html.Div([dcc.Graph(id="fig-pagamento")], className="card-grafico"),
                html.Div([dcc.Graph(id="fig-status")], className="card-grafico"),
            ],
            style={
                "display": "flex", "flexWrap": "wrap",
                "rowGap": "28px", "columnGap": "1.5%",
                "padding": "10px 30px 40px 30px",
            },
        ),
    ],
    style={"fontFamily": "Arial, sans-serif"},
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def filtrar(pais, categoria, status, data_ini, data_fim):
    dff = df.copy()
    if pais:
        dff = dff[dff["Country"].isin(pais)]
    if categoria:
        dff = dff[dff["Category"].isin(categoria)]
    if status:
        dff = dff[dff["OrderStatus"].isin(status)]
    if data_ini and data_fim:
        data_ini = pd.to_datetime(data_ini)
        data_fim = pd.to_datetime(data_fim)
        dff = dff[(dff["OrderDate"] >= data_ini) & (dff["OrderDate"] <= data_fim)]
    return dff


CROSS_FILTER_LABELS = {
    "country": "País",
    "category": "Categoria",
    "status": "Status",
    "payment": "Pagamento",
    "month": "Mês",
    "product": "Produto",
}


def aplicar_cross_filtros(dff, cross, excluir=None):
    """Aplica os filtros vindos de cliques nos gráficos (cross-filter),
    exceto os campos listados em `excluir` (usado para o próprio gráfico
    de origem continuar mostrando todas as opções)."""
    excluir = excluir or set()
    cross = cross or {}

    if cross.get("country") and "country" not in excluir:
        dff = dff[dff["Country"] == cross["country"]]
    if cross.get("category") and "category" not in excluir:
        dff = dff[dff["Category"] == cross["category"]]
    if cross.get("status") and "status" not in excluir:
        dff = dff[dff["OrderStatus"] == cross["status"]]
    if cross.get("payment") and "payment" not in excluir:
        dff = dff[dff["PaymentMethod"] == cross["payment"]]
    if cross.get("month") and "month" not in excluir:
        dff = dff[dff["YearMonth"].dt.strftime("%Y-%m") == cross["month"]]
    if cross.get("product") and "product" not in excluir:
        dff = dff[dff["ProductName"] == cross["product"]]
    return dff


def opacidades(rotulos, selecionado):
    """Lista de opacidades para destacar o item selecionado num gráfico de barras."""
    if not selecionado:
        return [1.0] * len(rotulos)
    return [1.0 if r == selecionado else 0.30 for r in rotulos]


def puxar_fatias(rotulos, selecionado):
    """Lista de 'pull' para destacar a fatia selecionada num gráfico de pizza."""
    if not selecionado:
        return [0] * len(rotulos)
    return [0.09 if r == selecionado else 0 for r in rotulos]


def cartao_kpi(titulo, valor, cor, theme):
    return html.Div(
        [
            html.P(titulo, style={"margin": "0", "color": theme["subtext"], "fontSize": "13px"}),
            html.H2(valor, style={"margin": "4px 0 0 0", "color": cor}),
        ],
        style={
            "flex": "1",
            "padding": "16px 20px",
            "backgroundColor": theme["card_bg"],
            "border": f"1px solid {theme['border']}",
            "borderRadius": "8px",
            "borderTop": f"4px solid {cor}",
        },
    )


# ---------------------------------------------------------------------------
# Callback: alterna o tema (clique no botão)
# ---------------------------------------------------------------------------
@callback(
    Output("theme-store", "data"),
    Output("theme-toggle-btn", "children"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def alternar_tema(n_clicks, tema_atual):
    novo_tema = "dark" if tema_atual == "light" else "light"
    return novo_tema, THEMES[novo_tema]["toggle_label"]


# Sincroniza o atributo data-theme no <html> via clientside callback,
# permitindo que o CSS acima (dropdowns, inputs de data) reaja ao tema.
app.clientside_callback(
    """
    function(theme) {
        document.documentElement.setAttribute('data-theme', theme || 'light');
        return '';
    }
    """,
    Output("theme-sync", "children"),
    Input("theme-store", "data"),
)


# ---------------------------------------------------------------------------
# Callback: cross-filter (clique nos gráficos filtra os outros)
# ---------------------------------------------------------------------------
@callback(
    Output("cross-filter-store", "data"),
    Input("fig-pais", "clickData"),
    Input("fig-pizza", "clickData"),
    Input("fig-pagamento", "clickData"),
    Input("fig-status", "clickData"),
    Input("fig-linha", "clickData"),
    Input("fig-produtos", "clickData"),
    Input("clear-filters-btn", "n_clicks"),
    Input({"type": "remove-cross-filter", "field": ALL}, "n_clicks"),
    State("cross-filter-store", "data"),
    prevent_initial_call=True,
)
def atualizar_cross_filter(pais_click, cat_click, pag_click, status_click,
                            linha_click, prod_click, limpar_clicks, remove_clicks, store):
    store = dict(store or {})
    disparado = ctx.triggered_id

    if disparado is None:
        return store

    if disparado == "clear-filters-btn":
        return {}

    if isinstance(disparado, dict) and disparado.get("type") == "remove-cross-filter":
        store.pop(disparado.get("field"), None)
        return store

    if disparado == "fig-pais" and pais_click:
        valor = pais_click["points"][0]["x"]
        store["country"] = None if store.get("country") == valor else valor
    elif disparado == "fig-pizza" and cat_click:
        valor = cat_click["points"][0]["label"]
        store["category"] = None if store.get("category") == valor else valor
    elif disparado == "fig-pagamento" and pag_click:
        valor = pag_click["points"][0]["label"]
        store["payment"] = None if store.get("payment") == valor else valor
    elif disparado == "fig-status" and status_click:
        valor = status_click["points"][0]["x"]
        store["status"] = None if store.get("status") == valor else valor
    elif disparado == "fig-linha" and linha_click:
        valor_bruto = linha_click["points"][0]["x"]
        valor_mes = pd.to_datetime(valor_bruto).strftime("%Y-%m")
        store["month"] = None if store.get("month") == valor_mes else valor_mes
    elif disparado == "fig-produtos" and prod_click:
        valor = prod_click["points"][0]["y"]
        store["product"] = None if store.get("product") == valor else valor

    # remove chaves vazias para manter o store limpo
    return {k: v for k, v in store.items() if v}


# ---------------------------------------------------------------------------
# Callback: renderiza os "chips" dos filtros ativos por clique
# ---------------------------------------------------------------------------
@callback(
    Output("cross-filter-chips", "children"),
    Output("clear-filters-btn", "style"),
    Input("cross-filter-store", "data"),
    Input("theme-store", "data"),
)
def renderizar_chips(cross, tema_nome):
    theme = THEMES.get(tema_nome, THEMES["light"])
    cross = {k: v for k, v in (cross or {}).items() if v}

    estilo_botao_limpar = {
        "padding": "6px 14px",
        "borderRadius": "16px",
        "border": "none",
        "backgroundColor": "#EF5350",
        "color": "white",
        "cursor": "pointer",
        "fontSize": "12px",
        "display": "inline-block" if cross else "none",
    }

    if not cross:
        return [], estilo_botao_limpar

    chips = []
    for campo, valor in cross.items():
        chips.append(
            html.Button(
                f"{CROSS_FILTER_LABELS.get(campo, campo)}: {valor}  ✕",
                id={"type": "remove-cross-filter", "field": campo},
                n_clicks=0,
                className="chip-remover",
                style={
                    "padding": "6px 14px",
                    "borderRadius": "16px",
                    "border": f"1px solid {theme['border']}",
                    "backgroundColor": theme["card_bg"],
                    "color": theme["text"],
                    "cursor": "pointer",
                    "fontSize": "12px",
                },
            )
        )

    return chips, estilo_botao_limpar


# ---------------------------------------------------------------------------
# Callback principal: filtros + tema -> KPIs, gráficos e estilos
# ---------------------------------------------------------------------------
@callback(
    Output("kpis", "children"),
    Output("fig-linha", "figure"),
    Output("fig-pais", "figure"),
    Output("fig-pizza", "figure"),
    Output("fig-produtos", "figure"),
    Output("fig-pagamento", "figure"),
    Output("fig-status", "figure"),
    Output("app-container", "style"),
    Output("header", "style"),
    Output("filtros", "style"),
    Output("subtitle", "style"),
    Output("theme-toggle-btn", "style"),
    Input("f-country", "value"),
    Input("f-category", "value"),
    Input("f-status", "value"),
    Input("f-periodo", "start_date"),
    Input("f-periodo", "end_date"),
    Input("theme-store", "data"),
    Input("cross-filter-store", "data"),
)
def atualizar_dashboard(pais, categoria, status, data_ini, data_fim, tema_nome, cross):
    theme = THEMES.get(tema_nome, THEMES["light"])
    template = theme["plot_template"]
    cross = cross or {}

    # Filtro base (dropdowns + período) aplicado a todos os gráficos
    dff_base = filtrar(pais, categoria, status, data_ini, data_fim)

    # KPIs consideram TODOS os filtros, inclusive os de clique (cross-filter)
    dff_kpi = aplicar_cross_filtros(dff_base, cross)

    faturamento = dff_kpi["TotalAmount"].sum()
    pedidos = dff_kpi["OrderID"].nunique()
    pedidos_cancelados = (dff_kpi["OrderStatus"] == "Cancelled").sum()
    ticket_medio = faturamento / pedidos if pedidos else 0
    itens_vendidos = dff_kpi["Quantity"].sum()

    kpis = [
        cartao_kpi("Faturamento Total", f"${faturamento:,.0f}", "#4CAF50", theme),
        cartao_kpi("Pedidos", f"{pedidos:,}", "#00ACC1", theme),
        cartao_kpi("Pedidos Cancelados", f"{pedidos_cancelados:,}", "#EF5350", theme),
        cartao_kpi("Ticket Médio", f"${ticket_medio:,.2f}", "#EF6C00", theme),
        cartao_kpi("Itens Vendidos", f"{itens_vendidos:,}", "#F9A825", theme),
    ]

    # --- Faturamento ao longo do tempo -------------------------------------
    dff_linha = aplicar_cross_filtros(dff_base, cross, excluir={"month"})
    linha = dff_linha.groupby("YearMonth", as_index=False)["TotalAmount"].sum()
    linha["MesStr"] = linha["YearMonth"].dt.strftime("%Y-%m")
    mes_selecionado = cross.get("month")
    tamanhos_marcador = [12 if m == mes_selecionado else 6 for m in linha["MesStr"]]
    fig_linha = go.Figure(
        data=[go.Scatter(
            x=linha["YearMonth"], y=linha["TotalAmount"],
            mode="lines+markers",
            line=dict(color="#0F52BA", width=3),
            marker=dict(size=tamanhos_marcador, color="#0F52BA",
                        line=dict(width=[2 if m == mes_selecionado else 0 for m in linha["MesStr"]], color="#FFD54F")),
        )]
    )
    fig_linha.update_layout(
        title="Faturamento ao Longo do Tempo",
        xaxis_title="Mês", yaxis_title="Faturamento ($)",
        template=template, height=320,
        margin=dict(l=50, r=20, t=55, b=40),
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, zeroline=False),
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Faturamento por país ------------------------------------------------
    dff_pais_chart = aplicar_cross_filtros(dff_base, cross, excluir={"country"})
    por_pais = dff_pais_chart.groupby("Country", as_index=False)["TotalAmount"].sum().sort_values("TotalAmount", ascending=False)
    fig_pais = go.Figure(
        data=[go.Bar(
            x=por_pais["Country"], y=por_pais["TotalAmount"],
            marker=dict(color=COLORS[5], opacity=opacidades(por_pais["Country"], cross.get("country"))),
            text=por_pais["TotalAmount"].round(0), textposition="outside",
        )]
    )
    fig_pais.update_layout(
        title="Faturamento por País",
        xaxis_title="País", yaxis_title="Faturamento ($)",
        xaxis={"categoryorder": "total descending"},
        template=template, height=320,
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Participação por categoria ------------------------------------------
    dff_pizza_chart = aplicar_cross_filtros(dff_base, cross, excluir={"category"})
    por_categoria = dff_pizza_chart.groupby("Category", as_index=False)["TotalAmount"].sum()
    fig_pizza = go.Figure(
        data=[go.Pie(
            labels=por_categoria["Category"], values=por_categoria["TotalAmount"],
            marker=dict(colors=COLORS, line=dict(color=theme["bg"], width=2)),
            hole=0.5, textinfo="percent", textposition="inside",
            domain=dict(y=[0.20, 1]),
            pull=puxar_fatias(por_categoria["Category"], cross.get("category")),
            hovertemplate="<b>%{label}</b><br>Faturamento: $%{value:,.2f}<br>Participação: %{percent}<extra></extra>",
        )]
    )
    fig_pizza.update_layout(
        title="Participação por Categoria",
        template=template, height=320,
        margin=dict(l=20, r=20, t=55, b=10),
        showlegend=True,
        legend=dict(orientation="h", y=0, x=0.5, xanchor="center", yanchor="bottom"),
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Top produtos ----------------------------------------------------------
    dff_produtos_chart = aplicar_cross_filtros(dff_base, cross, excluir={"product"})
    top_produtos = dff_produtos_chart.groupby("ProductName", as_index=False)["Quantity"].sum()
    top_produtos = top_produtos.nlargest(10, "Quantity").sort_values("Quantity")
    produto_selecionado = cross.get("product")
    cores_produtos = [
        "#FFD54F" if p == produto_selecionado else COLORS[0] for p in top_produtos["ProductName"]
    ]
    tamanhos_produtos = [16 if p == produto_selecionado else 12 for p in top_produtos["ProductName"]]
    fig_produtos = go.Figure(
        go.Scatter(
            x=top_produtos["Quantity"], y=top_produtos["ProductName"],
            mode="markers",
            marker=dict(size=tamanhos_produtos, color=cores_produtos, line=dict(width=1, color=theme["bg"])),
            hovertemplate="<b>%{y}</b><br>Itens vendidos: %{x:,}<extra></extra>",
        )
    )
    fig_produtos.update_layout(
        title="Top 10 Produtos Mais Vendidos",
        template=template, height=320,
        margin=dict(l=20, r=25, t=55, b=35),
        xaxis=dict(title="Quantidade Vendida", showgrid=True, zeroline=False),
        yaxis=dict(title="", showgrid=False, automargin=True),
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Forma de pagamento ------------------------------------------------------
    dff_pagamento_chart = aplicar_cross_filtros(dff_base, cross, excluir={"payment"})
    por_pagamento = dff_pagamento_chart.groupby("PaymentMethod", as_index=False)["OrderID"].count()
    por_pagamento.columns = ["PaymentMethod", "Pedidos"]
    por_pagamento = por_pagamento.sort_values("Pedidos", ascending=False)
    fig_pagamento = go.Figure(
        data=[go.Pie(
            labels=por_pagamento["PaymentMethod"], values=por_pagamento["Pedidos"],
            hole=0.5,
            marker=dict(colors=COLORS, line=dict(color=theme["bg"], width=2)),
            textinfo="percent", textposition="inside",
            pull=puxar_fatias(por_pagamento["PaymentMethod"], cross.get("payment")),
            hovertemplate="<b>%{label}</b><br>Pedidos: %{value}<br>%{percent}<extra></extra>",
        )]
    )
    fig_pagamento.update_layout(
        title=dict(text="Pedidos por Forma de Pagamento", x=0.5, xanchor="center"),
        template=template, height=320,
        margin=dict(l=10, r=10, t=50, b=85),
        showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.02, yanchor="top"),
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Status do pedido --------------------------------------------------------
    dff_status_chart = aplicar_cross_filtros(dff_base, cross, excluir={"status"})
    por_status = dff_status_chart.groupby("OrderStatus", as_index=False)["OrderID"].count()
    por_status.columns = ["OrderStatus", "Pedidos"]
    por_status = por_status.sort_values("Pedidos", ascending=False)
    fig_status = go.Figure(
        data=[go.Bar(
            x=por_status["OrderStatus"], y=por_status["Pedidos"],
            marker=dict(color=COLORS[4], opacity=opacidades(por_status["OrderStatus"], cross.get("status"))),
            text=por_status["Pedidos"], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Pedidos: %{y}<extra></extra>",
        )]
    )
    fig_status.update_layout(
        title="Pedidos por Status",
        xaxis_title="Status", yaxis_title="Pedidos",
        xaxis=dict(categoryorder="total descending", showgrid=False),
        yaxis=dict(showgrid=True, zeroline=False, automargin=True),
        template=template, height=360,
        margin=dict(l=50, r=20, t=55, b=60),
        paper_bgcolor=theme["card_bg"], plot_bgcolor=theme["card_bg"],
        font=dict(color=theme["text"]),
    )

    # --- Estilos dependentes do tema --------------------------------------------
    container_style = {"fontFamily": "Arial, sans-serif", "backgroundColor": theme["bg"], "color": theme["text"], "minHeight": "100vh"}
    header_style = {
        "padding": "20px 30px", "borderBottom": f"1px solid {theme['border']}",
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "backgroundColor": theme["bg"],
    }
    filtros_style = {"padding": "20px 30px", "backgroundColor": theme["panel_bg"], "borderBottom": f"1px solid {theme['border']}"}
    subtitle_style = {"marginTop": "4px", "color": theme["subtext"]}
    toggle_btn_style = {
        "height": "40px", "padding": "0 16px", "borderRadius": "20px",
        "border": f"1px solid {theme['border']}", "cursor": "pointer", "fontSize": "14px",
        "backgroundColor": theme["card_bg"], "color": theme["text"],
    }

    return (
        kpis, fig_linha, fig_pais, fig_pizza, fig_produtos, fig_pagamento, fig_status,
        container_style, header_style, filtros_style, subtitle_style, toggle_btn_style,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8051)