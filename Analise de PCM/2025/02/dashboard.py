import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Carregar os dados do Excel
df = pd.read_excel("/workspaces/ANALISES-DE-DADOS/Analise de PCM/2025/02/dados.xlsx", engine='openpyxl')

# Converter datas para formato datetime
df['Data Início'] = pd.to_datetime(df['Data Início'], format='%d/%m/%Y %H:%M')
df['Data Final'] = pd.to_datetime(df['Data Final'], format='%d/%m/%Y %H:%M')

# Calcular duração em horas
df['Duração (Horas)'] = (df['Data Final'] - df['Data Início']).dt.total_seconds() / 3600

# Criar colunas auxiliares
# Mapeamento manual dos dias da semana
df['Dia da Semana'] = df['Data Início'].dt.dayofweek.map({
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
})
df['Mês/Ano'] = df['Data Início'].dt.to_period('M').astype(str)
df['Hora do Dia'] = df['Data Início'].dt.hour

# Iniciar o app Dash
app = Dash(__name__)

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Análise de O.S.", style={'textAlign': 'center'}),
    
    # Filtros
    html.Div([
        dcc.Dropdown(
            id='filtro-setor',
            options=[{'label': setor, 'value': setor} for setor in df['SETOR'].unique()],
            placeholder="Selecione um SETOR"
        ),
        dcc.DatePickerRange(
            id='filtro-data',
            start_date=df['Data Início'].min(),
            end_date=df['Data Final'].max()
        )
    ], style={'padding': '20px', 'display': 'flex', 'gap': '20px'}),
    
    # Gráficos
    html.Div([
        dcc.Graph(id='grafico-os-por-setor'),
        dcc.Graph(id='grafico-duracao-media'),
        dcc.Graph(id='grafico-heatmap'),
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px'})
])

# Callbacks para interatividade
@app.callback(
    [Output('grafico-os-por-setor', 'figure'),
     Output('grafico-duracao-media', 'figure'),
     Output('grafico-heatmap', 'figure')],
    [Input('filtro-setor', 'value'),
     Input('filtro-data', 'start_date'),
     Input('filtro-data', 'end_date')]
)
def update_graphs(setor_selecionado, start_date, end_date):
    filtered_df = df.copy()
    # Aplicar filtros
    if setor_selecionado:
        filtered_df = filtered_df[filtered_df['SETOR'] == setor_selecionado]
    filtered_df = filtered_df[(filtered_df['Data Início'] >= start_date) & 
                              (filtered_df['Data Final'] <= end_date)]
    
    # Gráfico 1: O.S. por SETOR
    fig1 = px.bar(
        filtered_df.groupby('SETOR', as_index=False).size(),
        x='SETOR', y='size',
        title='Total de O.S. por SETOR',
        labels={'size': 'Total de O.S.'}
    )
    
    # Gráfico 2: Duração média por máquina
    fig2 = px.bar(
        filtered_df.groupby('Máquina', as_index=False)['Duração (Horas)'].mean(),
        x='Máquina', y='Duração (Horas)',
        title='Duração Média por Máquina'
    )
    
    # Gráfico 3: Heatmap (Hora x Dia da Semana)
    heatmap_data = filtered_df.groupby(['Hora do Dia', 'Dia da Semana']).size().reset_index(name='Contagem')
    fig3 = px.density_heatmap(
        heatmap_data,
        x='Hora do Dia',
        y='Dia da Semana',
        z='Contagem',
        title='Atividade por Hora e Dia da Semana',
        nbinsx=24
    )
    
    return fig1, fig2, fig3


# Executar o dashboard
if __name__ == '__main__':
    app.run_server(debug=True)