import streamlit as st, plotly.express as px
from utils import config_pagina, gerar_dados
config_pagina("Impacto")
df = gerar_dados()
st.title("2️⃣ O que o problema causa")
f = df[df.fraude == 1]
mensal = f.groupby(f.data.dt.to_period("M").astype(str))["valor"].agg(["sum", "count"]).reset_index()
c1, c2 = st.columns(2)
c1.plotly_chart(px.bar(mensal, x="data", y="sum", title="Perda mensal por fraude (R$)"), use_container_width=True)
c2.plotly_chart(px.line(mensal, x="data", y="count", markers=True, title="Nº de fraudes por mês"), use_container_width=True)
c3, c4 = st.columns(2)
canal = df.groupby("canal")["fraude"].mean().reset_index()
c3.plotly_chart(px.bar(canal, x="canal", y="fraude", title="Taxa de fraude por canal", text_auto=".2%"), use_container_width=True)
hora = df.groupby("hora")["fraude"].mean().reset_index()
c4.plotly_chart(px.line(hora, x="hora", y="fraude", title="Taxa de fraude por hora do dia"), use_container_width=True)
st.markdown("**Consequências:** prejuízo direto, chargebacks, perda de confiança, custo operacional de investigação e riscos regulatórios.")
