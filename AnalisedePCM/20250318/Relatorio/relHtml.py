import dash
from dash import dcc, html
import plotly.express as px

df = pd.read_csv("/workspaces/ANALISES-DE-DADOS/Analise de PCM/20250318/dash01.py")  # Substitua pelo seu DataFrame real

# Criar gráfico interativo
fig = px.bar(df, x="Setor", y="Tempo_Médio_Manutenção", color="Setor")

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1("Relatório de Manutenção"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)
