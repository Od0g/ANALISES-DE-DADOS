from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Carregar os dados
df = pd.read_csv('Analise de PCM/2025/02/Dados/Geral/DadoPcMbeta.csv', delimiter=';', encoding='utf-8')

# Converter datas corretamente
df['DATA_ABERTURA'] = pd.to_datetime(df['DATA_ABERTURA'], format='%d/%m/%Y %H:%M', dayfirst=True, errors='coerce')
df['DATA_FECHAMENTO'] = pd.to_datetime(df['DATA_FECHAMENTO'], format='%d/%m/%Y %H:%M', dayfirst=True, errors='coerce')

# Calcular tempo médio de fechamento
df['TEMPO_FECHAMENTO'] = (df['DATA_FECHAMENTO'] - df['DATA_ABERTURA']).dt.total_seconds() / 3600  # em horas

@app.route("/")
def index():
    return render_template("index.html")  # Página HTML principal

@app.route("/dados")
def dados():
    # Resumo dos setores
    setores = df.groupby("SETOR").size().to_dict()
    tempo_medio = df["TEMPO_FECHAMENTO"].mean()

    # Manutenção corretiva vs preventiva
    tipos_manutencao = df.groupby("TIPO_ACAO").size().to_dict()

    return jsonify({
        "setores": setores,
        "tempo_medio": tempo_medio,
        "tipos_manutencao": tipos_manutencao
    })

if __name__ == "__main__":
    app.run(debug=True)
