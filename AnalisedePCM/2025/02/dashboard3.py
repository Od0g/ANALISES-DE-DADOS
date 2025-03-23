import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State
from dash import dash_table

# Carregar os dados do Excel
df = pd.read_excel("AnalisedePCM/2025/02/dados.xlsx", engine='openpyxl')

# Converter datas para formato datetime
df['Data Início'] = pd.to_datetime(df['Data Início'], format='%d/%m/%Y %H:%M')
df['Data Final'] = pd.to_datetime(df['Data Final'], format='%d/%m/%Y %H:%M')

# Calcular duração em horas
df['Duração (Horas)'] = (df['Data Final'] - df['Data Início']).dt.total_seconds() / 3600

# Criar colunas auxiliares
df['Dia da Semana'] = df['Data Início'].dt.dayofweek.map({
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
})

df['Hora do Dia'] = df['Data Início'].dt.hour

# Função auxiliar para criação de períodos
def criar_periodo(row, periodo):
    data = row['Data Início']
    try:
        if periodo == 'day':
            return data.strftime('%d/%m/%Y')
        elif periodo == 'week':
            return f"Semana {data.isocalendar().week} - {data.year}"
        elif periodo == 'month':
            return data.strftime('%m/%Y')
        elif periodo == 'quarter':
            quarter = (data.month - 1) // 3 + 1
            return f"T{quarter} {data.year}"
        elif periodo == 'semester':
            semester = '1' if data.month <= 6 else '2'
            return f"S{semester} {data.year}"
        elif periodo == 'year':
            return str(data.year)
    except:
        return 'Outro'

# Iniciar o app Dash
app = Dash(__name__, suppress_callback_exceptions=True)

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Dashboard de Análise de O.S.", style={'textAlign': 'center'}),
    
    # Filtros
    html.Div([
        dcc.Dropdown(
            id='filtro-periodo',
            options=[
                {'label': 'Dia', 'value': 'day'},
                {'label': 'Semana', 'value': 'week'},
                {'label': 'Mês', 'value': 'month'},
                {'label': 'Trimestre', 'value': 'quarter'},
                {'label': 'Semestre', 'value': 'semester'},
                {'label': 'Ano', 'value': 'year'}
            ],
            value='month',
            placeholder="Selecione o período",
            style={'width': '200px'}
        ),
        dcc.Dropdown(
            id='filtro-setor',
            options=[{'label': setor, 'value': setor} for setor in df['SETOR'].unique()],
            placeholder="Selecione um SETOR",
            style={'width': '200px'}
        ),
        dcc.Input(
            id='filtro-pesquisa',
            type='text',
            placeholder='Pesquisar na Descrição...',
            style={'width': '300px'}
        ),
        dcc.DatePickerRange(
            id='filtro-data',
            start_date=df['Data Início'].min(),
            end_date=df['Data Final'].max()
        ),
        html.Button("Download Dados", id="btn-download", className='download-button')
    ], style={'padding': '20px', 'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'}),
    
    # KPIs
    html.Div([
        html.Div([
            html.H4("Total de O.S.", className='card-title'),
            html.P(id='kpi-total-os', className='card-value')
        ], className='card'),
        html.Div([
            html.H4("Duração Média", className='card-title'),
            html.P(id='kpi-duracao-media', className='card-value')
        ], className='card'),
        html.Div([
            html.H4("Máquina Mais Frequente", className='card-title'),
            html.P(id='kpi-maquina-mais-os', className='card-value')
        ], className='card')
    ], style={'display': 'flex', 'gap': '20px', 'padding': '20px'}),
    
    # Tabela
    dash_table.DataTable(
        id='tabela-dados',
        columns=[{"name": col, "id": col} for col in df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '8px'}
    ),
    
    # Gráficos
    html.Div([
        dcc.Graph(id='grafico-os-por-setor'),
        dcc.Graph(id='grafico-duracao-media'),
        dcc.Graph(id='grafico-heatmap'),
        dcc.Graph(id='grafico-tendencia'),
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),
    
    # Componente de download
    dcc.Download(id="download-data")
])

# Callback principal
@app.callback(
    [Output('grafico-os-por-setor', 'figure'),
     Output('grafico-duracao-media', 'figure'),
     Output('grafico-heatmap', 'figure'),
     Output('grafico-tendencia', 'figure'),
     Output('kpi-total-os', 'children'),
     Output('kpi-duracao-media', 'children'),
     Output('kpi-maquina-mais-os', 'children'),
     Output('tabela-dados', 'data')],
    [Input('filtro-setor', 'value'),
     Input('filtro-pesquisa', 'value'),
     Input('filtro-data', 'start_date'),
     Input('filtro-data', 'end_date'),
     Input('filtro-periodo', 'value')]
)
def update_dashboard(setor, pesquisa, start_date, end_date, periodo):
    filtered_df = df.copy()
    
    # Aplicar filtros
    if setor:
        filtered_df = filtered_df[filtered_df['SETOR'] == setor]
    if pesquisa:
        filtered_df = filtered_df[filtered_df['Descrição'].str.contains(pesquisa, case=False, na=False)]
    
    # Filtrar por data
    filtered_df = filtered_df[
        (filtered_df['Data Início'] >= pd.to_datetime(start_date)) &
        (filtered_df['Data Final'] <= pd.to_datetime(end_date))
    ]
    
    # Criar coluna de período
    filtered_df['Período'] = filtered_df.apply(lambda x: criar_periodo(x, periodo), axis=1)
    
    # Calcular KPIs
    total_os = filtered_df.shape[0]
    duracao_media = filtered_df['Duração (Horas)'].mean().round(2) if not filtered_df.empty else 0
    maquina_mais_os = filtered_df['Máquina'].mode()[0] if not filtered_df.empty else 'N/A'

    # Criar gráficos com tratamento para dados vazios
    if not filtered_df.empty:
        # Gráfico 1: O.S. por SETOR
        fig1 = px.bar(
            filtered_df.groupby('SETOR', as_index=False).size(),
            x='SETOR', y='size',
            title='OS por Setor',
            labels={'size': 'Quantidade'}
        ).update_layout(hovermode='x unified')

        # Gráfico 2: Duração média por máquina
        fig2 = px.bar(
            filtered_df.groupby('Máquina', as_index=False)['Duração (Horas)'].mean(),
            x='Máquina', y='Duração (Horas)',
            title='Duração Média por Máquina'
        ).update_traces(marker_color='#3498db')

        # Gráfico 3: Heatmap
        heatmap_data = filtered_df.groupby(['Hora do Dia', 'Dia da Semana']).size().reset_index(name='Contagem')
        fig3 = px.density_heatmap(
            heatmap_data,
            x='Hora do Dia',
            y='Dia da Semana',
            z='Contagem',
            title='Atividade por Hora/Dia',
            nbinsx=24
        )

        # Gráfico 4: Tendência
        trend_data = filtered_df.groupby('Período', as_index=False).size()
        fig4 = px.line(
            trend_data,
            x='Período', y='size',
            title=f'Tendência por {periodo.capitalize()}',
            labels={'size': 'Quantidade'}
        ).update_traces(line=dict(width=2))
    else:
        # Gráficos vazios se não houver dados
        fig1 = px.bar(title='Sem dados')
        fig2 = px.bar(title='Sem dados')
        fig3 = px.density_heatmap(title='Sem dados')
        fig4 = px.line(title='Sem dados')

    return fig1, fig2, fig3, fig4, total_os, f'{duracao_media} h', maquina_mais_os, filtered_df.to_dict('records')


@app.callback(
    Output("download-data", "data"),
    Input("btn-download", "n_clicks"),
    State('tabela-dados', 'data'),
    prevent_initial_call=True
)
def download_data(n_clicks, dados_tabela):
    df_download = pd.DataFrame(dados_tabela)
    return dcc.send_data_frame(df_download.to_excel, "dados_filtrados.xlsx")

# Executar o dashboard
if __name__ == '__main__':
    app.run_server(debug=True)