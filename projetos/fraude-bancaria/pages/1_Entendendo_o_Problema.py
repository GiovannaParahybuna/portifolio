import streamlit as st, plotly.express as px
from utils import config_pagina, gerar_dados
config_pagina("O Problema")
df = gerar_dados()
st.title("1️⃣ Entendendo o problema")
st.markdown("""
**Fraude** é qualquer transação feita sem autorização legítima do titular: clonagem de cartão,
account takeover, engenharia social, fraude de identidade.

**Desafios**
- **Desbalanceamento extremo**: poucos casos de fraude entre milhares de transações. Acurácia engana.
- **Adaptação do fraudador**: padrões mudam (concept drift).
- **Custo assimétrico**: deixar passar uma fraude custa o valor da transação; bloquear um cliente legítimo custa atrito e reputação.
""")
c1, c2 = st.columns(2)
cont = df.fraude.map({0: "Legítima", 1: "Fraude"}).value_counts().reset_index()
c1.plotly_chart(px.pie(cont, names="fraude", values="count", hole=.5, title="Distribuição das classes"), use_container_width=True)
c2.dataframe(df.head(15), use_container_width=True)
st.warning(f"Um modelo que prevê 'nunca é fraude' teria **{1-df.fraude.mean():.1%} de acurácia** e zero utilidade.")
