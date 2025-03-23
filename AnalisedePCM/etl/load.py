import os

def load(dataframes):
    """Salva os DataFrames transformados na pasta data/processed"""
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed'))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for name, df in dataframes.items():
        output_file = os.path.join(output_path, name)
        df.to_csv(output_file, index=False)
        print(f"📁 {name} salvo em {output_path}!")

    print("\n✅ Todos os arquivos foram carregados com sucesso!")
