import pandas as pd, streamlit as st, plotly.express as px
from utils import config_pagina, gerar_dados, treinar
config_pagina("Solução")
df = gerar_dados()
st.title("4️⃣ Solução proposta")
st.markdown("Abordagem em camadas: **regras determinísticas** (rápidas, explicáveis) + **modelo de ML** (captura padrões complexos).")

st.subheader("Camada 1 · Regras de negócio")
r = ((df.dispositivo_novo == 1) & (df.internacional == 1)) | (df.tentativas_24h >= 5) | ((df.hora < 6) & (df.valor > df.valor.quantile(.95)))
c = st.columns(3)
c[0].metric("Transações sinalizadas", f"{r.mean():.2%}")
c[1].metric("Precisão das regras", f"{df.loc[r,'fraude'].mean():.2%}")
c[2].metric("Recall das regras", f"{r[df.fraude==1].mean():.2%}")

st.subheader("Camada 2 · Machine learning")
nome = st.radio("Modelo", ["Random Forest", "Regressão Logística"], horizontal=True)
res = treinar(nome)
m = res["model"]
imp = m.feature_importances_ if hasattr(m, "feature_importances_") else abs(m.coef_[0])
imp = pd.Series(imp, index=res["cols"]).sort_values().tail(12).reset_index()
imp.columns = ["variável", "importância"]
st.plotly_chart(px.bar(imp, x="importância", y="variável", orientation="h", title="Variáveis mais relevantes"), use_container_width=True)
st.session_state["modelo"] = nome
st.success("Modelo treinado com split estratificado 70/30 e `class_weight='balanced'`. Valide na próxima página.")
