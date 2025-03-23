import os
import pandas as pd
from datetime import datetime

def padronizar_colunas(df):
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("[^a-z0-9_]", "", regex=True)
    return df

def tratar_valores_ausentes(df):
    df.fillna("N/A", inplace=True)
    return df

def converter_tipos(df):
    for col in df.columns:
        if "data" in col or "date" in col:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass
    return df

def consolidar_csv(pasta_entrada, arquivo_saida):
    arquivos = [f for f in os.listdir(pasta_entrada) if f.endswith(".csv")]
    df_lista = []
    
    for arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta_entrada, arquivo)
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        df = padronizar_colunas(df)
        df = tratar_valores_ausentes(df)
        df = converter_tipos(df)
        df_lista.append(df)
    
    df_final = pd.concat(df_lista, ignore_index=True)
    df_final.to_csv(arquivo_saida, index=False, encoding='utf-8')
    print(f"Arquivo consolidado salvo em: {arquivo_saida}")

# Exemplo de uso
consolidar_csv("/workspaces/ANALISES-DE-DADOS/AnalisedePCM/data/processed", "consolidado.csv")
