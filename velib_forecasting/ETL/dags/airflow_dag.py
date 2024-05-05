from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

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
    description="DAG pour aller récupérer les données velib",
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 4, 11),
    catchup=False,
)

dag_meteo = DAG(
    "meteo_dag_recuperation",
    is_paused_upon_creation=False,
    default_args=default_args,
    description="DAG pour aller récupérer les données météo",
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 4, 11),
    catchup=False,
)


def velib_station_info_pipeline() -> None:
    """
    The goal of this function is to
    use Airflow to put the different
    velib data inside Bigquery tables

    Arguments:
        -None
    Returns:
        -None
    """

    df_velib = get_velib_data()
    df_velib = transform_velib(df_velib)
    velib_dataframe_to_bigquery(df_velib)


def meteo_info_pipeline() -> None:
    """
    The goal of this function is to
    use Airflow to put the different
    meteo data inside Bigquery tables

    Arguments:
        -None
    Returns:
        -None
    """

    meteo_json = get_meteo_data()
    meteo_json = transform_meteo(meteo_json)
    meteo_dataframe_to_bigquery(meteo_json)


velib_task = PythonOperator(
    task_id="recuperer_et_inserer_donnees",
    python_callable=velib_station_info_pipeline,
    dag=dag_velib,
)

meteo_task = PythonOperator(
    task_id="recuperer_et_inserer_donnees",
    python_callable=meteo_info_pipeline,
    dag=dag_meteo,
)

if __name__ == "__main__":
    meteo_info_pipeline()
