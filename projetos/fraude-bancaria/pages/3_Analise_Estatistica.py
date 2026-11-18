import numpy as np, pandas as pd, streamlit as st, plotly.express as px
from scipy import stats
from utils import config_pagina, gerar_dados
config_pagina("Análise Estatística")
df = gerar_dados()
st.title("3️⃣ Análise estatística")
t1, t2, t3, t4 = st.tabs(["Variáveis numéricas", "Variáveis categóricas", "Correlações", "IC da taxa de fraude"])

with t1:
    v = st.selectbox("Variável", ["valor", "idade_conta_dias", "tentativas_24h", "distancia_km"])
    a, b = df.loc[df.fraude == 1, v], df.loc[df.fraude == 0, v]
    tt = stats.ttest_ind(a, b, equal_var=False)
    mw = stats.mannwhitneyu(a, b)
    ks = stats.ks_2samp(a, b)
    sp = np.sqrt((a.var()*(len(a)-1)+b.var()*(len(b)-1))/(len(a)+len(b)-2))
    d = (a.mean()-b.mean())/sp
    st.plotly_chart(px.box(df, x="fraude", y=v, log_y=(v == "valor"), color="fraude"), use_container_width=True)
    st.dataframe(pd.DataFrame({
        "Teste": ["t de Welch", "Mann-Whitney U", "Kolmogorov-Smirnov", "d de Cohen"],
        "Estatística": [tt.statistic, mw.statistic, ks.statistic, d],
        "p-valor": [tt.pvalue, mw.pvalue, ks.pvalue, np.nan]}), use_container_width=True)
    st.caption("p < 0,05 → rejeita H0 (distribuições iguais). |d|: 0,2 pequeno · 0,5 médio · 0,8 grande.")

with t2:
    v = st.selectbox("Variável categórica", ["canal", "categoria", "dispositivo_novo", "internacional"])
    ct = pd.crosstab(df[v], df.fraude)
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    cramer = np.sqrt(chi2/(len(df)*(min(ct.shape)-1)))
    st.dataframe(ct, use_container_width=True)
    st.write(f"**χ² = {chi2:.2f}** · gl = {dof} · **p = {p:.4g}** · V de Cramér = {cramer:.3f}")

with t3:
    num = df[["valor", "idade_conta_dias", "tentativas_24h", "distancia_km", "dispositivo_novo", "internacional", "hora", "fraude"]]
    st.plotly_chart(px.imshow(num.corr(method="spearman"), text_auto=".2f", color_continuous_scale="RdBu_r",
                              zmin=-1, zmax=1, title="Correlação de Spearman"), use_container_width=True)

with t4:
    n, k = len(df), df.fraude.sum()
    conf = st.slider("Confiança", .80, .99, .95)
    z = stats.norm.ppf((1+conf)/2); ph = k/n
    centro = (ph + z**2/(2*n))/(1+z**2/n)
    marg = z*np.sqrt(ph*(1-ph)/n + z**2/(4*n**2))/(1+z**2/n)
    st.metric("Taxa de fraude (Wilson)", f"{ph:.2%}", f"IC: [{centro-marg:.2%}, {centro+marg:.2%}]", delta_color="off")
