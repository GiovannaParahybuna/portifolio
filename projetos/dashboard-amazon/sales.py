import pandas as pd

df = pd.read_csv("Amazon.csv")

print(df)

import plotly.express as px


fig1 = px.bar(
    df,
    x="Category",
    y="Quantity"
)

fig1.update_traces(marker_color="red")

fig1.show()