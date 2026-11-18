import numpy as np, pandas as pd, streamlit as st, plotly.express as px, plotly.graph_objects as go
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score, confusion_matrix, brier_score_loss
from utils import config_pagina, treinar, CUSTO_FP
config_pagina("Validação")
st.title("5️⃣ Validação dos resultados")
nome = st.radio("Modelo", ["Random Forest", "Regressão Logística"], horizontal=True)
res = treinar(nome); y, p, val = res["y"], res["p"], res["valor"]

fpr, tpr, _ = roc_curve(y, p); pr, rc, _ = precision_recall_curve(y, p)
c1, c2 = st.columns(2)
fig = go.Figure(go.Scatter(x=fpr, y=tpr, name="ROC")); fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line_dash="dash")
fig.update_layout(title=f"ROC · AUC = {auc(fpr, tpr):.3f}", xaxis_title="FPR", yaxis_title="TPR")
c1.plotly_chart(fig, use_container_width=True)
c2.plotly_chart(px.line(x=rc, y=pr, labels={"x": "Recall", "y": "Precisão"}, title=f"Precision-Recall · AP = {average_precision_score(y, p):.3f}"), use_container_width=True)
st.caption(f"Brier score: {brier_score_loss(y, p):.4f} · linha de base de AP = taxa de fraude ({y.mean():.2%})")

st.subheader("Threshold e custo de negócio")
ths = np.linspace(.01, .99, 99)
def custo(t):
    pred = p >= t
    return val[(y == 1) & ~pred].sum() + CUSTO_FP*((y == 0) & pred).sum()
custos = [custo(t) for t in ths]
t_otimo = ths[int(np.argmin(custos))]
t = st.slider("Threshold", .01, .99, float(round(t_otimo, 2)), .01)
pred = p >= t
tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
m = st.columns(5)
m[0].metric("Precisão", f"{tp/max(tp+fp,1):.1%}"); m[1].metric("Recall", f"{tp/max(tp+fn,1):.1%}")
m[2].metric("F1", f"{2*tp/max(2*tp+fp+fn,1):.1%}"); m[3].metric("Custo total", f"R$ {custo(t):,.0f}")
m[4].metric("Sem modelo", f"R$ {val[y==1].sum():,.0f}")
c3, c4 = st.columns(2)
c3.plotly_chart(px.imshow([[tn, fp], [fn, tp]], text_auto=True, x=["Prev. legítima", "Prev. fraude"], y=["Real legítima", "Real fraude"],
                          color_continuous_scale="Blues", title="Matriz de confusão"), use_container_width=True)
f2 = px.line(x=ths, y=custos, labels={"x": "Threshold", "y": "Custo (R$)"}, title=f"Curva de custo · ótimo ≈ {t_otimo:.2f}")
f2.add_vline(x=t, line_dash="dash"); c4.plotly_chart(f2, use_container_width=True)
st.info(f"Custo de falso positivo assumido: R$ {CUSTO_FP:.0f} (ajuste em `utils.py`).")
