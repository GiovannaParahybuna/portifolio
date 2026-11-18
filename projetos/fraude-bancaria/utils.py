import numpy as np, pandas as pd, streamlit as st
from scipy.special import expit
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

CUSTO_FP = 15.0  # custo (R$) de bloquear/atritar uma transação legítima

def config_pagina(titulo):
    st.set_page_config(page_title=titulo, page_icon="🛡️", layout="wide")

@st.cache_data
def gerar_dados(n=30000, taxa=0.03, seed=42):
    """Dados simulados. Para usar o Kaggle (Credit Card Fraud), troque por pd.read_csv('creditcard.csv')."""
    r = np.random.default_rng(seed)
    df = pd.DataFrame({
        "data": pd.Timestamp("2026-01-01") + pd.to_timedelta(r.integers(0, 180*86400, n), unit="s"),
        "valor": r.lognormal(4.0, 1.1, n).round(2),
        "canal": r.choice(["App", "Web", "POS", "ATM"], n, p=[.40, .25, .30, .05]),
        "categoria": r.choice(["Varejo", "Alimentação", "Viagens", "Eletrônicos", "Serviços"], n),
        "idade_conta_dias": r.exponential(900, n).astype(int),
        "tentativas_24h": r.poisson(1.2, n),
        "distancia_km": r.exponential(30, n).round(1),
        "dispositivo_novo": (r.random(n) < .12).astype(int),
        "internacional": (r.random(n) < .06).astype(int),
    })
    df["hora"] = df["data"].dt.hour
    z = (0.35*np.log1p(df.valor) + 0.35*df.tentativas_24h + 0.012*df.distancia_km
         + 1.6*df.dispositivo_novo + 1.5*df.internacional + 1.2*(df.hora < 6)
         - 0.0004*df.idade_conta_dias + 0.5*(df.canal == "Web") + 0.4*(df.categoria == "Eletrônicos"))
    lo, hi = -30, 10
    for _ in range(60):  # calibra o intercepto p/ atingir a taxa de fraude desejada
        mid = (lo+hi)/2
        lo, hi = (mid, hi) if expit(z+mid).mean() < taxa else (lo, mid)
    df["fraude"] = (r.random(n) < expit(z+mid)).astype(int)
    return df.sort_values("data").reset_index(drop=True)

FEATS = ["valor", "idade_conta_dias", "tentativas_24h", "distancia_km", "dispositivo_novo",
         "internacional", "hora", "canal", "categoria"]

@st.cache_resource
def treinar(modelo="Random Forest"):
    df = gerar_dados()
    X = pd.get_dummies(df[FEATS], columns=["canal", "categoria"], drop_first=True).astype(float)
    y = df["fraude"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.3, stratify=y, random_state=7)
    if modelo == "Random Forest":
        m = RandomForestClassifier(300, min_samples_leaf=5, class_weight="balanced", n_jobs=-1, random_state=7)
    else:
        m = LogisticRegression(max_iter=2000, class_weight="balanced")
        mu, sd = Xtr.mean(), Xtr.std()
        Xtr, Xte = (Xtr-mu)/sd, (Xte-mu)/sd
    m.fit(Xtr, ytr)
    valores = df.loc[yte.index, "valor"].values
    return dict(model=m, cols=list(X.columns), y=yte.values, p=m.predict_proba(Xte)[:, 1], valor=valores)
