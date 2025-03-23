import pandas as pd
import os

# Caminho da pasta processada
processed_dir = "/workspaces/ANALISES-DE-DADOS/AnalisedePCM/data/processed"

# Listar os arquivos na pasta processada
files = os.listdir(processed_dir)
print(f"📂 Arquivos processados encontrados: {files}\n")

# Validar cada arquivo
for file in files:
    file_path = os.path.join(processed_dir, file)
    print(f"📌 Validando: {file}")

    try:
        df = pd.read_csv(file_path, sep=";")  # Define o separador correto
        print(df.head())  # Mostrar as primeiras linhas
        print(df.info())  # Informações sobre colunas e tipos de dados
        print(f"✔ {file} validado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao validar {file}: {e}\n")
