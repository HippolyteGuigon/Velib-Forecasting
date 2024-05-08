from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
from velib_forecasting.ETL.extract.velib_extract import get_velib_data
from velib_forecasting.ETL.load.load_velib import velib_dataframe_to_bigquery
from velib_forecasting.ETL.transform.transform_velib import transform_velib
from velib_forecasting.ETL.extract.meteo_extract import get_meteo_data
from velib_forecasting.ETL.load.load_meteo import meteo_dataframe_to_bigquery
from velib_forecasting.ETL.transform.transform_meteo import transform_meteo

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

dag_velib = DAG(
    "velib_dag_recuperation",
    is_paused_upon_creation=False,
    default_args=default_args,
    description="DAG pour récupérer les données velib",
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 4, 11),
    catchup=False,
)

dag_meteo = DAG(
    "meteo_dag_recuperation",
    is_paused_upon_creation=False,
    default_args=default_args,
    description="DAG pour récupérer les données météo",
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 4, 11),
    catchup=False,
)


def velib_station_info_pipeline():
    df_velib = get_velib_data()
    df_velib = transform_velib(df_velib)
    velib_dataframe_to_bigquery(df_velib)


def meteo_info_pipeline():
    meteo_json = get_meteo_data()
    meteo_json = transform_meteo(meteo_json)
    meteo_dataframe_to_bigquery(meteo_json)


velib_task = PythonOperator(
    task_id="recuperer_et_inserer_donnees_velib",
    python_callable=velib_station_info_pipeline,
    dag=dag_velib,
)

meteo_task = TriggerDagRunOperator(
    task_id="recuperer_et_inserer_donnees_meteo",
    trigger_dag_id="meteo_dag_recuperation",
    python_callable=meteo_info_pipeline,
    dag=dag_meteo,
)

velib_task >> meteo_task
