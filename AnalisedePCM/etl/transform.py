import pandas as pd

def transform(dataframes):
    """Limpa e estrutura os dados extraídos"""
    processed_data = {}

    for name, df in dataframes.items():
        print(f"🔄 Transformando {name}...")

        # Remover linhas com valores nulos
        df.dropna(inplace=True)

        # Padronizar nomes das colunas (minúsculas e sem espaços)
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Remover duplicatas
        df.drop_duplicates(inplace=True)

        processed_data[name] = df

        print(f"✔ {name} transformado! ({df.shape[0]} linhas, {df.shape[1]} colunas)")

    return processed_data
