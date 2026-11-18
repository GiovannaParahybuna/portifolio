import pandas as pd
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback

# =========================================================
# DADOS
# =========================================================
# Lê o CSV uma única vez, quando o servidor sobe (não a cada clique do usuário).
# Isso é importante: os filtros mais na frente sempre partem desse "df" original,
# nunca o sobrescrevem — cada filtro cria uma cópia (dff) separada.
df = pd.read_csv("Amazon.csv")

# A coluna vem como texto (ex: "2023-01-31"). Convertendo para datetime real,
# conseguimos comparar datas (>=, <=) no filtro de período mais abaixo.
df["OrderDate"] = pd.to_datetime(df["OrderDate"])

# Cria uma coluna auxiliar "YearMonth" agrupando cada data no primeiro dia do mês
# (ex: 2023-01-31 e 2023-01-05 viram os dois 2023-01-01).
# Isso é o que permite montar o gráfico de linha "faturamento por mês" mais à frente,
# sem precisar agrupar por cada dia individual (o que deixaria a linha poluída).
df["YearMonth"] = df["OrderDate"].dt.to_period("M").dt.to_timestamp()

# Paleta de cores fixa, reutilizada em vários gráficos (pizza, boxplot, funil...)
# para manter uma identidade visual consistente no dashboard inteiro.
CORES = ["#2E86C1", "#E67E22", "#27AE60", "#8E44AD", "#C0392B", "#16A085"]

# Cria a aplicação Dash. "app.title" é o que aparece na aba do navegador.
app = Dash(__name__)
app.title = "Amazon Sales Dashboard"

# app.index_string substitui o HTML padrão que o Dash gera por baixo dos panos.
# Usamos isso só para injetar um <style> customizado (classe .card-grafico),
# sem precisar criar uma pasta "assets/" separada com um arquivo .css.
# Os blocos {%...%} são "placeholders" que o próprio Dash preenche automaticamente
# (meta tags, título da aba, scripts do React/Plotly etc.) — não mexer neles.
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Cada gráfico recebe essa classe. width: 32% + gap no container pai
               é o que garante 3 gráficos por linha em telas largas. */
            .card-grafico {
                width: 32%;
                min-width: 320px;  /* abaixo disso, quebra para 2 ou 1 por linha (responsivo) */
                background-color: white;
                border: 1px solid #eee;
                border-radius: 8px;
                box-sizing: border-box;
                padding: 5px;
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

# =========================================================
# LAYOUT
# =========================================================
# app.layout descreve a estrutura VISUAL da página inteira, como se fosse HTML.
# html.Div([...]) = uma <div> comum, que pode conter outras divs, textos, gráficos etc.
# Tudo aqui é só "esqueleto" (o que existe na tela) — quem preenche os valores
# de verdade é o callback lá embaixo, toda vez que um filtro muda.
app.layout = html.Div([

    # ---------- CABEÇALHO ----------
    html.Div([
        html.H1("Amazon Sales Dashboard", style={"margin": "0"}),
        html.P("Visão geral de vendas, produtos e clientes", style={"color": "#666", "marginTop": "4px"}),
    ], style={"padding": "20px 30px", "borderBottom": "1px solid #eee"}),

    # ---------- FILTROS ----------
    # 4 filtros lado a lado. Cada um tem um "id" único (ex: "f-pais") — é esse id
    # que o callback usa para saber qual valor o usuário selecionou em cada um.
    html.Div([

        # Filtro de País: multi=True permite selecionar vários países ao mesmo tempo.
        # Se o usuário não selecionar nada, o value fica None (= "sem filtro", mostra tudo).
        html.Div([
            html.Label("País"),
            dcc.Dropdown(
                id="f-pais",
                options=[{"label": c, "value": c} for c in sorted(df["Country"].unique())],
                value=None,
                multi=True,
                placeholder="Todos os países"
            ),
        ], style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"}),

        # Filtro de Categoria: mesma lógica do filtro de país.
        html.Div([
            html.Label("Categoria"),
            dcc.Dropdown(
                id="f-categoria",
                options=[{"label": c, "value": c} for c in sorted(df["Category"].unique())],
                value=None,
                multi=True,
                placeholder="Todas as categorias"
            ),
        ], style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"}),

        # Filtro de Status do Pedido (Delivered, Cancelled, Pending, etc.)
        html.Div([
            html.Label("Status do Pedido"),
            dcc.Dropdown(
                id="f-status",
                options=[{"label": s, "value": s} for s in sorted(df["OrderStatus"].unique())],
                value=None,
                multi=True,
                placeholder="Todos os status"
            ),
        ], style={"width": "23%", "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"}),

        # Filtro de Período: um seletor de intervalo de datas.
        # Os limites (min/max) vêm direto dos dados, então o usuário nunca
        # consegue escolher uma data fora do que existe no CSV.
        html.Div([
            html.Label("Período"),
            dcc.DatePickerRange(
                id="f-periodo",
                min_date_allowed=df["OrderDate"].min(),
                max_date_allowed=df["OrderDate"].max(),
                start_date=df["OrderDate"].min(),
                end_date=df["OrderDate"].max(),
                display_format="DD/MM/YYYY"
            ),
        ], style={"width": "25%", "display": "inline-block", "verticalAlign": "top"}),

    ], style={"padding": "20px 30px", "backgroundColor": "#fafafa", "borderBottom": "1px solid #eee"}),

    # ---------- KPIs ----------
    # Div vazia por enquanto (children não foi definido) — ela só ganha conteúdo
    # quando o callback roda e devolve a lista de cartões pelo Output("kpis", "children").
    # display: flex + gap deixa os 4 cartões lado a lado, distribuindo o espaço igualmente.
    html.Div(id="kpis", style={"padding": "20px 30px", "display": "flex", "gap": "20px"}),

    # ---------- GRÁFICOS: grid de 3 colunas ----------
    # Container pai com display: flex + flexWrap: wrap: os itens ficam em linha,
    # e quando não cabem mais 3 na largura disponível, o próximo "quebra" para a
    # linha de baixo automaticamente — não precisamos calcular isso manualmente.
    # Cada dcc.Graph fica dentro de uma html.Div com className="card-grafico"
    # (o estilo dessa classe está definido lá em cima, no app.index_string).
    # Os ids (fig-linha, fig-pais, etc.) são o "gancho" que o callback usa para
    # saber qual figura vai em qual gráfico.
    html.Div([
        html.Div([dcc.Graph(id="fig-linha")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-pais")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-pizza")], className="card-grafico"),

        html.Div([dcc.Graph(id="fig-produtos")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-pagamento")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-status")], className="card-grafico"),

        html.Div([dcc.Graph(id="fig-marca")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-cidade")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-dispersao")], className="card-grafico"),

        html.Div([dcc.Graph(id="fig-treemap")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-heatmap")], className="card-grafico"),
        html.Div([dcc.Graph(id="fig-boxplot")], className="card-grafico"),

        html.Div([dcc.Graph(id="fig-funil")], className="card-grafico"),  # sobra sozinho na última linha (13 não é múltiplo de 3)
    ], style={
        "display": "flex", "flexWrap": "wrap", "gap": "1.5%",
        "padding": "10px 30px 40px 30px"
    }),

], style={"fontFamily": "Arial, sans-serif"})


# =========================================================
# FUNÇÃO AUXILIAR DE FILTRO
# =========================================================
# Centraliza a lógica de filtro num único lugar. Em vez de repetir esse
# "if" quatro vezes dentro de cada gráfico, chamamos filtrar() uma vez só
# no início do callback, e todos os gráficos usam o resultado (dff).
def filtrar(pais, categoria, status, data_ini, data_fim):
    dff = df.copy()  # nunca alteramos o df original — sempre trabalhamos numa cópia

    # Cada "if" só aplica o filtro se o usuário de fato selecionou algo.
    # Se o dropdown estiver vazio (None ou []), pulamos o filtro e mantemos tudo.
    if pais:
        dff = dff[dff["Country"].isin(pais)]
    if categoria:
        dff = dff[dff["Category"].isin(categoria)]
    if status:
        dff = dff[dff["OrderStatus"].isin(status)]
    if data_ini and data_fim:
        dff = dff[(dff["OrderDate"] >= data_ini) & (dff["OrderDate"] <= data_fim)]

    return dff


# Função que gera o HTML de UM cartão de KPI, para não repetir o mesmo bloco
# de código 4 vezes (Faturamento, Pedidos, Ticket Médio, Itens Vendidos).
def cartao_kpi(titulo, valor, cor):
    return html.Div([
        html.P(titulo, style={"margin": "0", "color": "#888", "fontSize": "13px"}),
        html.H2(valor, style={"margin": "4px 0 0 0", "color": cor}),
    ], style={
        "flex": "1",  # faz os cartões dividirem o espaço disponível igualmente
        "padding": "16px 20px", "backgroundColor": "white",
        "border": "1px solid #eee", "borderRadius": "8px",
        "borderTop": f"4px solid {cor}"  # detalhe colorido no topo do cartão
    })


# =========================================================
# CALLBACK ÚNICO: atualiza tudo a partir dos filtros
# =========================================================
# Um callback conecta "Input"s (o que o usuário mexe) a "Output"s (o que muda na tela).
# Aqui usamos UM callback só com 14 Outputs — cada vez que qualquer um dos 5 Inputs
# muda (usuário troca o país, a categoria, o status ou a data), a função
# atualizar_dashboard roda inteira de novo e recalcula TODOS os gráficos de uma vez.
#
# Vantagem dessa abordagem (um callback grande) em vez de vários pequenos:
# o filtro (dff = filtrar(...)) é aplicado uma única vez e reaproveitado por
# todos os gráficos, em vez de cada gráfico ter seu próprio callback repetindo
# a mesma lógica de filtro.
@callback(
    Output("kpis", "children"),
    Output("fig-linha", "figure"),
    Output("fig-pais", "figure"),
    Output("fig-pizza", "figure"),
    Output("fig-produtos", "figure"),
    Output("fig-pagamento", "figure"),
    Output("fig-status", "figure"),
    Output("fig-marca", "figure"),
    Output("fig-cidade", "figure"),
    Output("fig-dispersao", "figure"),
    Output("fig-treemap", "figure"),
    Output("fig-heatmap", "figure"),
    Output("fig-boxplot", "figure"),
    Output("fig-funil", "figure"),
    Input("f-pais", "value"),
    Input("f-categoria", "value"),
    Input("f-status", "value"),
    Input("f-periodo", "start_date"),
    Input("f-periodo", "end_date"),
)
def atualizar_dashboard(pais, categoria, status, data_ini, data_fim):
    # Primeiro passo, sempre: aplicar os filtros escolhidos pelo usuário.
    # A partir daqui, "dff" é usado em TODOS os gráficos abaixo (nunca o "df" original).
    dff = filtrar(pais, categoria, status, data_ini, data_fim)

    # ---------- KPIs ----------
    # Métricas simples calculadas em cima do dataframe já filtrado.
    faturamento = dff["TotalAmount"].sum()
    pedidos = dff["OrderID"].nunique()  # nunique() em vez de count(): evita contar o mesmo pedido 2x
    ticket_medio = faturamento / pedidos if pedidos else 0  # evita divisão por zero se o filtro não retornar nada
    itens_vendidos = dff["Quantity"].sum()

    kpis = [
        cartao_kpi("Faturamento Total", f"${faturamento:,.0f}", "#2E86C1"),
        cartao_kpi("Pedidos", f"{pedidos:,}", "#E67E22"),
        cartao_kpi("Ticket Médio", f"${ticket_medio:,.2f}", "#27AE60"),
        cartao_kpi("Itens Vendidos", f"{itens_vendidos:,}", "#8E44AD"),
    ]

    # ---------- Gráfico de LINHA: faturamento por mês ----------
    # Agrupa por "YearMonth" (criada lá no início) e soma o faturamento de cada mês.
    linha = dff.groupby("YearMonth", as_index=False)["TotalAmount"].sum()
    fig_linha = go.Figure(
        data=[go.Scatter(
            x=linha["YearMonth"], y=linha["TotalAmount"],
            mode="lines+markers",  # desenha a linha E os pontinhos em cada mês
            line=dict(color="#2E86C1", width=3),
            marker=dict(size=6)
        )]
    )
    fig_linha.update_layout(
        title="Faturamento ao Longo do Tempo",
        xaxis_title="Mês", yaxis_title="Faturamento ($)",
        template="plotly_white", height=320
    )

    # ---------- Gráfico de BARRAS: faturamento por país ----------
    por_pais = dff.groupby("Country", as_index=False)["TotalAmount"].sum().sort_values("TotalAmount", ascending=False)
    fig_pais = go.Figure(
        data=[go.Bar(
            x=por_pais["Country"], y=por_pais["TotalAmount"],
            marker=dict(color="#2E86C1"),
            text=por_pais["TotalAmount"].round(0), textposition="outside"  # mostra o valor em cima de cada barra
        )]
    )
    fig_pais.update_layout(
        title="Faturamento por País",
        xaxis_title="País", yaxis_title="Faturamento ($)",
        # Força o eixo X a respeitar a ordem do maior para o menor valor,
        # em vez de ordenar por ordem alfabética (comportamento padrão do Plotly).
        xaxis={"categoryorder": "total descending"},
        template="plotly_white", height=320
    )

    # ---------- Gráfico de PIZZA (donut): participação por categoria ----------
    por_categoria = dff.groupby("Category", as_index=False)["TotalAmount"].sum()
    fig_pizza = go.Figure(
        data=[go.Pie(
            labels=por_categoria["Category"], values=por_categoria["TotalAmount"],
            marker=dict(colors=CORES),
            hole=0.4  # hole > 0 transforma a pizza num "donut" (buraco no meio)
        )]
    )
    fig_pizza.update_layout(title="Participação por Categoria", template="plotly_white", height=320)

    # ---------- Gráfico de BARRAS: top 10 produtos mais vendidos ----------
    top_produtos = dff.groupby("ProductName", as_index=False)["Quantity"].sum()
    top_produtos = top_produtos.sort_values("Quantity", ascending=False).head(10)  # pega só as 10 primeiras linhas
    fig_produtos = go.Figure(
        data=[go.Bar(
            x=top_produtos["ProductName"], y=top_produtos["Quantity"],
            marker=dict(color="#E67E22"),
            text=top_produtos["Quantity"], textposition="outside"
        )]
    )
    # Quando os 10 produtos têm quantidades parecidas, o gráfico "esmaga" a diferença
    # se o eixo Y começar em 0. Aqui cortamos o eixo perto do menor valor,
    # exagerando visualmente a diferença entre as barras (só usar isso em análise
    # interna/exploratória — pode ser enganoso em apresentações externas).
    if len(top_produtos):
        y_min = top_produtos["Quantity"].min() * 0.9
        y_max = top_produtos["Quantity"].max() * 1.15
        fig_produtos.update_yaxes(range=[y_min, y_max])
    fig_produtos.update_layout(
        title="Top 10 Produtos Mais Vendidos (Quantidade)",
        xaxis_title="Produto", yaxis_title="Quantidade",
        xaxis={"categoryorder": "total descending"},
        template="plotly_white", height=320
    )

    # ---------- Gráfico de PIZZA: forma de pagamento ----------
    por_pagamento = dff.groupby("PaymentMethod", as_index=False)["OrderID"].count()
    por_pagamento.columns = ["PaymentMethod", "Pedidos"]  # renomeia a coluna resultante do count()
    fig_pagamento = go.Figure(
        data=[go.Pie(
            labels=por_pagamento["PaymentMethod"], values=por_pagamento["Pedidos"],
            marker=dict(colors=CORES)
        )]
    )
    fig_pagamento.update_layout(title="Pedidos por Forma de Pagamento", template="plotly_white", height=320)

    # ---------- Gráfico de BARRAS: status do pedido ----------
    por_status = dff.groupby("OrderStatus", as_index=False)["OrderID"].count()
    por_status.columns = ["OrderStatus", "Pedidos"]
    por_status = por_status.sort_values("Pedidos", ascending=False)
    fig_status = go.Figure(
        data=[go.Bar(
            x=por_status["OrderStatus"], y=por_status["Pedidos"],
            marker=dict(color="#C0392B"),
            text=por_status["Pedidos"], textposition="outside"
        )]
    )
    fig_status.update_layout(
        title="Pedidos por Status",
        xaxis_title="Status", yaxis_title="Pedidos",
        xaxis={"categoryorder": "total descending"},
        template="plotly_white", height=320
    )

    # ---------- Gráfico de BARRAS: top 10 marcas por faturamento ----------
    top_marcas = dff.groupby("Brand", as_index=False)["TotalAmount"].sum()
    top_marcas = top_marcas.sort_values("TotalAmount", ascending=False).head(10)
    fig_marca = go.Figure(
        data=[go.Bar(
            x=top_marcas["Brand"], y=top_marcas["TotalAmount"],
            marker=dict(color="#16A085"),
            text=top_marcas["TotalAmount"].round(0), textposition="outside"
        )]
    )
    fig_marca.update_layout(
        title="Top 10 Marcas por Faturamento",
        xaxis_title="Marca", yaxis_title="Faturamento ($)",
        xaxis={"categoryorder": "total descending"},
        template="plotly_white", height=320
    )

    # ---------- Gráfico de BARRAS: top 10 cidades por faturamento ----------
    top_cidades = dff.groupby("City", as_index=False)["TotalAmount"].sum()
    top_cidades = top_cidades.sort_values("TotalAmount", ascending=False).head(10)
    fig_cidade = go.Figure(
        data=[go.Bar(
            x=top_cidades["City"], y=top_cidades["TotalAmount"],
            marker=dict(color="#8E44AD"),
            text=top_cidades["TotalAmount"].round(0), textposition="outside"
        )]
    )
    fig_cidade.update_layout(
        title="Top 10 Cidades por Faturamento",
        xaxis_title="Cidade", yaxis_title="Faturamento ($)",
        xaxis={"categoryorder": "total descending"},
        template="plotly_white", height=320
    )

    # ---------- Gráfico de DISPERSÃO: desconto x faturamento ----------
    # Com 100 mil linhas, plotar todos os pontos deixaria o gráfico lento e ilegível
    # (pontos empilhados uns em cima dos outros). Por isso pegamos uma amostra
    # aleatória de até 2000 pedidos — suficiente para ver o padrão geral,
    # sem travar o navegador. random_state=42 garante que a amostra seja sempre
    # a mesma toda vez que o código rodar (resultado reprodutível).
    amostra = dff.sample(min(2000, len(dff)), random_state=42) if len(dff) else dff
    fig_dispersao = go.Figure(
        data=[go.Scatter(
            x=amostra["Discount"], y=amostra["TotalAmount"],
            mode="markers",  # sem linha conectando os pontos, só os marcadores
            marker=dict(color="#2E86C1", size=6, opacity=0.5)  # opacity baixa ajuda a ver áreas de sobreposição
        )]
    )
    fig_dispersao.update_layout(
        title="Desconto x Faturamento do Pedido",
        xaxis_title="Desconto (%)", yaxis_title="Faturamento ($)",
        template="plotly_white", height=320
    )

    # ---------- TREEMAP: Categoria > Marca (faturamento) ----------
    # Treemap mostra hierarquia: "parents" define quem é "pai" de quem.
    # Aqui, cada Marca (labels) pertence a uma Categoria (parents) — o tamanho
    # de cada retângulo é proporcional ao faturamento (values).
    treemap_dados = dff.groupby(["Category", "Brand"], as_index=False)["TotalAmount"].sum()
    fig_treemap = go.Figure(
        data=[go.Treemap(
            labels=treemap_dados["Brand"],
            parents=treemap_dados["Category"],
            values=treemap_dados["TotalAmount"],
            marker=dict(colorscale="Blues"),
            textinfo="label+value"  # mostra o nome da marca + o valor dentro do retângulo
        )]
    )
    fig_treemap.update_layout(
        title="Faturamento por Categoria e Marca (Treemap)",
        template="plotly_white", height=320
    )

    # ---------- HEATMAP: Categoria x País (faturamento) ----------
    # pivot_table transforma o dataframe numa "matriz": linhas = Categoria,
    # colunas = País, e cada célula = soma do faturamento daquela combinação.
    # fill_value=0 preenche com zero as combinações que não existem nos dados
    # (ex: se não houve nenhuma venda de "Books" na "Austrália").
    heatmap_dados = dff.pivot_table(
        index="Category", columns="Country", values="TotalAmount", aggfunc="sum", fill_value=0
    )
    fig_heatmap = go.Figure(
        data=[go.Heatmap(
            z=heatmap_dados.values,        # os números (intensidade da cor)
            x=heatmap_dados.columns,       # eixo X = países
            y=heatmap_dados.index,         # eixo Y = categorias
            colorscale="Blues",            # quanto mais escuro, maior o faturamento
            text=heatmap_dados.values.round(0),
            texttemplate="%{text}",        # escreve o número dentro de cada célula
            hoverongaps=False
        )]
    )
    fig_heatmap.update_layout(
        title="Faturamento: Categoria x País (Heatmap)",
        template="plotly_white", height=320
    )

    # ---------- BOXPLOT: distribuição do valor do pedido por categoria ----------
    # Diferente dos gráficos de barra (que só mostram a SOMA), o boxplot mostra
    # a distribuição completa: mediana (linha do meio), quartis (caixa),
    # e outliers (pontos fora da "caixa"). Ajuda a ver, por exemplo, se uma
    # categoria tem pedidos muito mais variados em valor do que outra.
    #
    # Usamos um loop + add_trace (em vez de passar tudo de uma vez pro go.Box)
    # porque isso permite colorir cada categoria com uma cor diferente da
    # nossa paleta CORES — o go.Box sozinho não faz essa distinção de cor
    # automaticamente quando os dados vêm todos juntos.
    fig_boxplot = go.Figure()
    for i, cat in enumerate(sorted(dff["Category"].unique())):
        fig_boxplot.add_trace(go.Box(
            y=dff.loc[dff["Category"] == cat, "TotalAmount"],
            name=cat,
            marker=dict(color=CORES[i % len(CORES)])  # % garante que não estoure o índice se houver mais categorias que cores
        ))
    fig_boxplot.update_layout(
        title="Distribuição do Valor do Pedido por Categoria",
        yaxis_title="Faturamento ($)",
        template="plotly_white", height=320,
        showlegend=False  # a legenda seria redundante, já que cada caixa já tem o nome embaixo
    )

    # ---------- FUNIL: status do pedido ----------
    # value_counts() conta quantos pedidos existem em cada status.
    # reindex(ordem_funil) força a ORDEM das barras do funil a seguir o fluxo lógico
    # do pedido (Pending -> Shipped -> Delivered -> Returned -> Cancelled),
    # em vez da ordem que o pandas escolheria sozinho (por frequência).
    # fillna(0): se algum status não existir no filtro atual, mostra 0 em vez de sumir.
    ordem_funil = ["Pending", "Shipped", "Delivered", "Returned", "Cancelled"]
    funil_dados = dff["OrderStatus"].value_counts().reindex(ordem_funil).fillna(0)
    fig_funil = go.Figure(
        data=[go.Funnel(
            y=funil_dados.index,
            x=funil_dados.values,
            marker=dict(color=CORES[:len(funil_dados)])
        )]
    )
    fig_funil.update_layout(
        title="Funil de Status dos Pedidos",
        template="plotly_white", height=320
    )

    # A ORDEM dos itens aqui retornados precisa bater EXATAMENTE com a ordem
    # dos Output(...) declarados no @callback lá em cima — o Dash conecta
    # posição por posição, não por nome.
    return (kpis, fig_linha, fig_pais, fig_pizza, fig_produtos, fig_pagamento,
            fig_status, fig_marca, fig_cidade, fig_dispersao,
            fig_treemap, fig_heatmap, fig_boxplot, fig_funil)


if __name__ == "__main__":
    # debug=True ativa o hot-reload (o servidor reinicia sozinho quando você
    # salva o arquivo) e mostra mensagens de erro mais detalhadas no navegador.
    # Em produção (site publicado de verdade), isso deve ser desligado (debug=False).
    app.run(debug=True)