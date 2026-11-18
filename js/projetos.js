// Edite aqui: cada objeto vira um card e uma página (projeto.html?id=...)
const R=p=>CONFIG.REPO+"/tree/main/projetos/"+p;
const PROJETOS=[
{id:"futebol",icone:"⚽",titulo:"Classificações do Futebol",tag:"Dados via API",
 resumo:"Classificação de 7 ligas com atualização diária automática e botão de atualização sob demanda.",
 detalhes:"Pipeline em Python que consome a API football-data.org, trata os dados e os publica aqui. A atualização acontece todo dia de forma automática, e você pode forçar uma nova consulta pelo botão abaixo, que busca os dados na API em tempo real por meio de um proxy seguro.",
 stack:["Python","Pandas","API REST","GitHub Actions","Dash"],
 destaques:["134 times em 7 campeonatos (Brasil, Inglaterra, Espanha, Alemanha, Itália, França e Portugal)","Atualização diária automática e sob demanda","Token da API protegido: nunca fica exposto no navegador"],
 links:[["Ver código",R("futebol")]]},
{id:"atlas",icone:"🌍",titulo:"Atlas Estatístico das Nações",tag:"Análise de Dados",
 resumo:"Dashboard com indicadores demográficos e territoriais de 195 países.",
 detalhes:"Aplicação web que processa indicadores como área, população, densidade demográfica, IDH e taxa de fertilidade, calculando KPIs e rankings em Python e entregando tudo a um dashboard interativo.",
 stack:["Python","Pandas","Flask","Plotly","JavaScript"],
 destaques:["195 países e 10 indicadores","Cálculos estatísticos feitos no back-end e expostos por API JSON","Visualizações interativas no navegador"],
 links:[["Ver código",R("atlas-estatistico")]]},
{id:"amazon",icone:"🛒",titulo:"Dashboard de Vendas Amazon",tag:"Dashboard",
 resumo:"Painel interativo para analisar mais de 100 mil pedidos de e-commerce.",
 detalhes:"Dashboard construído em Python para explorar vendas por período, categoria e demais dimensões de uma base com 100 mil pedidos, com alternância entre tema claro e escuro.",
 stack:["Python","Pandas","Plotly","Dash"],
 destaques:["100.000 pedidos analisados","Evolução mensal de vendas e visões por categoria","Interface com tema claro/escuro"],
 links:[["Ver código",R("dashboard-amazon")]]},
{id:"fraude",icone:"🛡️",titulo:"Detecção de Fraude Bancária",tag:"Machine Learning",status:"Em desenvolvimento",
 resumo:"Projeto em andamento: da compreensão do problema à validação de um modelo antifraude.",
 detalhes:"Projeto ainda em desenvolvimento. Segue uma linha do tempo completa: entendimento do problema, impacto financeiro, análise estatística, solução com regras e machine learning e validação por métricas e custo de negócio. Utiliza dados simulados.",
 stack:["Python","Streamlit","scikit-learn","SciPy","Plotly"],
 destaques:["Testes estatísticos: t de Welch, Mann-Whitney, qui-quadrado e IC de Wilson","Random Forest com escolha de threshold pelo custo de negócio","Em construção: novas páginas e métricas serão adicionadas"],
 links:[["Ver código",R("fraude-bancaria")]]}
];
