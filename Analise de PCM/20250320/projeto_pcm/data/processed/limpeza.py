import pandas as pd
import os
import pyarrow as pa
from datetime import datetime

# ... (mantenha as configurações de caminho anteriores)

def clean_time_duration(df):
    """Converte durações de tempo para horas decimais com tratamento de erros"""
    if 'TEMPO_TRABALHADO' in df.columns:
        # Remove valores inválidos
        df['TEMPO_TRABALHADO'] = df['TEMPO_TRABALHADO'].replace(r'^#+$', pd.NA, regex=True)
        
        # Converte para horas
        df['TEMPO_TRABALHADO'] = (
            pd.to_timedelta(df['TEMPO_TRABALHADO'], errors='coerce')
            .dt.total_hours()
            .round(2)
        )
    return df

def clean_machine_column(df):
    """Garante que a coluna MAQUINA seja string"""
    if 'MAQUINA' in df.columns:
        df['MAQUINA'] = df['MAQUINA'].astype(str).str.strip()
    return df

def process_files(file_list):
    """Processa e combina todos os arquivos"""
    combined_df = pd.DataFrame()
    
    for file_path in file_list:
        try:
            df = pd.read_csv(
                file_path,
                sep=';',
                encoding='latin-1',
                parse_dates=False,
                dayfirst=True,
                dtype={'MAQUINA': str}  # Força a leitura como string
            )
            
            date_columns = [c for c in df.columns if 'DATA' in c.upper()]
            
            df = (df
                  .pipe(clean_date_columns, date_columns)
                  .pipe(clean_time_duration)
                  .pipe(remove_test_records)
                  .pipe(clean_machine_column)  # Nova etapa
                 )
            
            df.columns = df.columns.str.upper().str.strip()
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
            print(f"✅ Arquivo {os.path.basename(file_path)} processado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro em {os.path.basename(file_path)}: {str(e)}")
            continue
            
    return combined_df

# ... (mantenha o restante do código)

# ==================================================
# 5. Salvamento dos dados (Versão Corrigida)
# ==================================================

# Salva em CSV (mantido igual)
csv_path = os.path.join(processed_dir, 'dados_processados.csv')
df_clean.to_csv(csv_path, index=False, encoding='utf-8')

# Salva em Parquet com schema explícito
parquet_path = os.path.join(processed_dir, 'dados_processados.parquet')

# Define schema manualmente para evitar conflitos
schema = pa.Schema.from_pandas(df_clean, preserve_index=False)
table = pa.Table.from_pandas(df_clean, schema=schema)
pa.parquet.write_table(table, parquet_path)

print(f"\n✅ Processo concluído! Arquivos salvos em:\n{processed_dir}")