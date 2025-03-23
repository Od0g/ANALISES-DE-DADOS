import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import io

# Carregando os dados
# Substitua 'seu_arquivo.csv' pelo nome correto do arquivo contendo as OS.
df = pd.read_csv("/workspaces/ANALISES-DE-DADOS/Analise de PCM/2025/02/Dados/dados.xlsx", parse_dates=['Data Início', 'Data Final'])
df['Duração'] = (df['Data Final'] - df['Data Início']).dt.total_seconds() / 3600

# Inicializando o app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Análise de O.S.", style={'textAlign': 'center'}),
    
    # Filtros
    html.Div([
        dcc.Dropdown(id='filtro-setor', options=[{'label': s, 'value': s} for s in df['SETOR'].unique()],
                     placeholder="Selecione um SETOR"),
        dcc.Input(id='filtro-pesquisa', type='text', placeholder='Pesquisar na Descrição...'),
        dcc.DatePickerRange(id='filtro-data',
                            start_date=df['Data Início'].min(),
                            end_date=df['Data Final'].max())
    ], style={'display': 'flex', 'gap': '15px', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
    
    # KPIs
    html.Div([
        html.Div([html.H4("Total de O.S."), html.P(id='kpi-total-os')], className='card'),
        html.Div([html.H4("Duração Média"), html.P(id='kpi-duracao-media')], className='card'),
        html.Div([html.H4("Máquina Mais Frequente"), html.P(id='kpi-maquina-mais-os')], className='card')
    ], style={'display': 'flex', 'gap': '20px', 'padding': '20px', 'justifyContent': 'center'}),
    
    # Tabela de dados
    dash_table.DataTable(id='tabela-dados', columns=[{"name": col, "id": col} for col in df.columns], page_size=10),
    
    # Gráficos
    html.Div([
        dcc.Graph(id='grafico-os-por-setor'),
        dcc.Graph(id='grafico-duracao-media'),
        dcc.Graph(id='grafico-heatmap'),
        dcc.Graph(id='grafico-tendencia'),
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px'}),
    
    html.Button("Download Dados", id="btn-download", className='download-button'),
    dcc.Download(id="download-data")
])

# Callback para atualizar o dashboard
@app.callback(
    [
        Output('kpi-total-os', 'children'),
        Output('kpi-duracao-media', 'children'),
        Output('kpi-maquina-mais-os', 'children'),
        Output('tabela-dados', 'data'),
        Output('grafico-os-por-setor', 'figure'),
        Output('grafico-duracao-media', 'figure'),
        Output('grafico-heatmap', 'figure'),
        Output('grafico-tendencia', 'figure')
    ],
    [
        Input('filtro-setor', 'value'),
        Input('filtro-pesquisa', 'value'),
        Input('filtro-data', 'start_date'),
        Input('filtro-data', 'end_date')
    ]
)
def atualizar_dashboard(setor, pesquisa, start_date, end_date):
    filtered_df = df.copy()
    if setor:
        filtered_df = filtered_df[filtered_df['SETOR'] == setor]
    if pesquisa:
        filtered_df = filtered_df[filtered_df['DESCRIÇÃO'].str.contains(pesquisa, case=False, na=False)]
    if start_date and end_date:
        start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
        filtered_df = filtered_df[(filtered_df['Data Início'] >= start_date) & (filtered_df['Data Final'] <= end_date)]
    
    total_os = len(filtered_df)
    duracao_media = filtered_df['Duração'].mean() if not filtered_df.empty else 0
    maquina_mais_os = filtered_df['EQUIPAMENTO'].mode()[0] if not filtered_df.empty else "N/A"
    
    fig1 = px.bar(filtered_df, x='SETOR', title='O.S. por Setor') if not filtered_df.empty else px.bar(title="Sem dados")
    fig2 = px.histogram(filtered_df, x='Duração', title='Duração Média das O.S.') if not filtered_df.empty else px.histogram(title="Sem dados")
    
    if not filtered_df.empty:
        heatmap_data = filtered_df.groupby(['Hora do Dia', 'Dia da Semana']).size().reset_index(name='Contagem')
        fig3 = px.density_heatmap(heatmap_data, x='Hora do Dia', y='Dia da Semana', z='Contagem', title='Atividade por Hora/Dia')
    else:
        fig3 = px.density_heatmap(title="Sem dados disponíveis")
    
    fig4 = px.line(filtered_df, x='Data Início', y='Duração', title='Tendência da Duração das O.S.') if not filtered_df.empty else px.line(title="Sem dados")
    
    return total_os, f"{duracao_media:.2f} horas", maquina_mais_os, filtered_df.to_dict('records'), fig1, fig2, fig3, fig4

# Callback para download dos dados
@app.callback(
    Output("download-data", "data"),
    Input("btn-download", "n_clicks"),
    State('tabela-dados', 'data'),
    prevent_initial_call=True
)
def download_data(n_clicks, dados_tabela):
    if not dados_tabela:
        return None
    df_download = pd.DataFrame(dados_tabela)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_download.to_excel(writer, index=False, sheet_name="Dados Filtrados")
    buffer.seek(0)
    return dcc.send_bytes(buffer.read(), filename="dados_filtrados.xlsx")

# Executando o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
