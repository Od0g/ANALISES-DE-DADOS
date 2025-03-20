import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

# Carregar os dados (substituir pelo caminho correto do arquivo CSV)
df = pd.read_csv('Analise de PCM/2025/02/Dados/Geral/DadoPcMbeta.csv', delimiter=';', encoding='utf-8')

# Converter datas
df['DATA_ABERTURA'] = pd.to_datetime(df['DATA_ABERTURA'], format='%d/%m/%Y %H:%M', dayfirst=True, errors='coerce')
df['DATA_FECHAMENTO'] = pd.to_datetime(df['DATA_FECHAMENTO'], format='%d/%m/%Y %H:%M', dayfirst=True, errors='coerce')


# Calcular tempo de resolução (em dias)
df['TEMPO_RESOLUCAO'] = (df['DATA_FECHAMENTO'] - df['DATA_ABERTURA']).dt.days

# Tempo médio de resolução
tempo_medio = df['TEMPO_RESOLUCAO'].mean()

# Setores mais afetados
setores_contagem = df['SETOR'].value_counts().reset_index()
setores_contagem.columns = ['Setor', 'Quantidade']

# Histórico das OS
df_hist = df.groupby(df['DATA_ABERTURA'].dt.to_period('M')).size().reset_index()
df_hist.columns = ['Mês', 'Total_OS']
df_hist['Mês'] = df_hist['Mês'].astype(str)

# Manutenção corretiva
tipo_manutencao = df['TIPO_ACAO'].value_counts().reset_index()
tipo_manutencao.columns = ['Tipo', 'Quantidade']

# Equipamentos com mais OS
equip_contagem = df['EQUIPAMENTO'].value_counts().reset_index().head(10)
equip_contagem.columns = ['Equipamento', 'Quantidade']

# Criar app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Dashboard de Manutenção', style={'textAlign': 'center'}),
    
    html.H3(f'Tempo médio de resolução: {tempo_medio:.2f} dias'),
    
    dcc.Graph(
        figure=px.bar(setores_contagem, x='Setor', y='Quantidade', title='Setores com mais OS')
    ),
    
    dcc.Graph(
        figure=px.line(df_hist, x='Mês', y='Total_OS', title='Histórico de Abertura de OS')
    ),
    
    dcc.Graph(
        figure=px.pie(tipo_manutencao, names='Tipo', values='Quantidade', title='Distribuição dos Tipos de Manutenção')
    ),
    
    dcc.Graph(
        figure=px.bar(equip_contagem, x='Equipamento', y='Quantidade', title='Equipamentos com mais OS')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
