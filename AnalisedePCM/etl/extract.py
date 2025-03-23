import os
import pandas as pd

def extract():
    """Carrega os arquivos CSV da pasta data/raw"""
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw'))
    dataframes = {}


    print(f"📂 Buscando arquivos em: {data_path}")

    for file in os.listdir(data_path):
        if file.endswith('.csv'):
            file_path = os.path.join(data_path, file)
            df = pd.read_csv(file_path, sep=",", on_bad_lines='skip', encoding="utf-8")
            dataframes[file] = df
            print(f"✔ {file} carregado! ({df.shape[0]} linhas, {df.shape[1]} colunas)")

    return dataframes
