from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

import pandas as pd
import requests
import logging
from io import StringIO
from datetime import datetime


# Configuração da DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'start_date': datetime(2024, 10, 1),
    'catchup': False
}

dag = DAG(
    'fin_cotacoes_bcb_classic',
    schedule_interval='@daily',
    default_args=default_args,
    tags=['bcb']
)

# EXTRACT
def extract(**kwargs):
    print("(0) extração")

    # Definindo as datas inicial e final
    data_inicial = "01/10/2024"  # Formato DD/MM/YYYY
    data_final = "10/10/2024"     # Formato DD/MM/YYYY

    # URL para obter os dados da série histórica do dólar em CSV com parâmetros de data
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=csv&dataInicial={data_inicial}&dataFinal={data_final}"

    try:
        # Fazendo a requisição para obter o CSV
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx

        # Lendo o conteúdo CSV diretamente na variável
        csv_data = response.content.decode('utf-8')
        logging.info("CSV data retrieved successfully.")
        return csv_data

    except requests.exceptions.HTTPError as err:
        logging.error(f"Erro ao acessar a API: {err}")
        return None  # Handle this case in the downstream task
    except ValueError as ve:
        logging.error(f"Erro ao converter resposta CSV: {ve}")
        return None
    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")
        return None

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    provide_context=True,
    dag=dag
)

# TRANSFORM
def transform(**kwargs):
    print("(0) antes da transformação")
    cotacoes = kwargs['ti'].xcom_pull(task_ids='extract')
    if not cotacoes:
        logging.error("No data retrieved from extract task. Aborting transform.")
        return None  # This will cause the downstream load task to fail

    csvStringIO = StringIO(cotacoes)
    print("conteudo:\n" + csvStringIO.getvalue())

    # Define apenas as colunas relevantes
    column_names = [
        "DT_FECHAMENTO",
        "VALOR"  # Valor dos dados da série histórica
    ]

    # Mudando os tipos de dados para refletir a nova estrutura
    data_types = {
        "DT_FECHAMENTO": str,  # Mudou para string para facilitar o processamento
        "VALOR": float
    }

    parse_dates = ["DT_FECHAMENTO"]

    # Ajustando a leitura do CSV para incluir apenas as colunas necessárias
    df = pd.read_csv(
        csvStringIO,
        sep=";",
        decimal=",",
        thousands=".",
        encoding="utf-8",
        header=0,  # Mudar para 0 para pegar a primeira linha como cabeçalho
        names=column_names,
        dtype=data_types,
        parse_dates=parse_dates
    )

    # Remove a coluna não necessária
    df['data_processamento'] = datetime.now()

    return df[['DT_FECHAMENTO', 'VALOR']]  # Retornar apenas as colunas relevantes

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    provide_context=True,
    dag=dag
)

# CREATE TABLE
# Define a nova conexão para o PostgreSQL
new_postgres_conn_id = "postgres_new_connection"

# CREATE TABLE com nova estrutura
create_table_ddl = """
CREATE TABLE IF NOT EXISTS cotacoes (
    dt_fechamento DATE PRIMARY KEY,
    valor REAL
)
"""

create_table_postgres = PostgresOperator(
    task_id="create_table_postgres",
    postgres_conn_id=new_postgres_conn_id,  # Use a nova conexão
    sql=create_table_ddl,
    dag=dag
)

# LOAD
def load(**kwargs):
    cotacoes_df = kwargs['ti'].xcom_pull(task_ids='transform')
    table_name = "cotacoes"
    if cotacoes_df is None or cotacoes_df.empty:
        logging.error("No data to load. Aborting load task.")
        return  # This prevents trying to insert empty data

    # Atualize o hook para usar a nova conexão
    postgres_hook = PostgresHook(postgres_conn_id=new_postgres_conn_id, schema="test_database_62yd")
    print("(1) antes da linha rows")
    rows = list(cotacoes_df.itertuples(index=False, name=None))  # Converte para uma lista de tuplas

    # Imprimir as três primeiras linhas, se houver
    print("Primeiras três linhas de rows:")
    for i, row in enumerate(rows[:3], start=1):
        print(f"Linha {i}: {row}")

    # Loop para inserir os dados, lidando com conflitos
    for row in rows:
        insert_query = f"""
        INSERT INTO {table_name} (dt_fechamento, valor)
        VALUES (%s, %s)
        ON CONFLICT (dt_fechamento) DO UPDATE SET valor = EXCLUDED.valor;
        """
        postgres_hook.run(insert_query, parameters=row)

    print("(3) depois da insert")

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    provide_context=True,
    dag=dag
)

extract_task >> transform_task >> create_table_postgres >> load_task
