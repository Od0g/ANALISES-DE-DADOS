import os
import sys

# Adiciona a pasta raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.extract import extract
from etl.transform import transform
from etl.load import load

def main():
    print("🚀 Iniciando o Pipeline ETL...")

    # Extração
    print("\n📂 Extraindo dados...")
    raw_data = extract()

    # Transformação
    print("\n🔄 Transformando dados...")
    transformed_data = transform(raw_data)

    # Carga
    print("\n📡 Carregando dados...")
    load(transformed_data)

    print("\n✅ Pipeline ETL finalizado com sucesso!")

if __name__ == "__main__":
    main()
