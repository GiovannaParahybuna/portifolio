import streamlit as st
from utils import config_pagina, gerar_dados
config_pagina("Antifraude | Home")
df = gerar_dados()

st.title("🛡️ Projeto Antifraude Bancária")
st.caption("Do problema à validação do modelo · dados simulados (substituíveis por dataset do Kaggle)")

c = st.columns(4)
c[0].metric("Transações", f"{len(df):,}".replace(",", "."))
c[1].metric("Taxa de fraude", f"{df.fraude.mean():.2%}")
c[2].metric("Perda por fraude", f"R$ {df.loc[df.fraude==1,'valor'].sum():,.0f}".replace(",", "."))
c[3].metric("Ticket médio fraude", f"R$ {df.loc[df.fraude==1,'valor'].mean():,.0f}")

st.subheader("Linha do tempo do projeto")
etapas = [
 ("1️⃣ Entendendo o problema", "O que é fraude, tipos e por que é difícil detectar (classes desbalanceadas)."),
 ("2️⃣ Impacto", "Perdas financeiras, evolução temporal, canais e horários mais afetados."),
 ("3️⃣ Análise estatística", "Testes de hipótese, tamanho de efeito, correlações e intervalos de confiança."),
 ("4️⃣ Solução", "Regras de negócio vs. modelo de machine learning, importância das variáveis."),
 ("5️⃣ Validação", "ROC, Precision-Recall, matriz de confusão e threshold ótimo por custo."),
]
for t, d in etapas:
    with st.container(border=True):
        st.markdown(f"**{t}**  \n{d}")
st.info("Use o menu lateral para navegar. Rode com: `streamlit run app.py`")
