from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from velib_forecasting.ETL.extract.velib_extract import get_velib_data
from velib_forecasting.ETL.load.load_velib import velib_dataframe_to_bigquery
from velib_forecasting.ETL.transform.transform_velib import transform_velib

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "velib_dag_recuperation",
    default_args=default_args,
    description="DAG pour aller récupérer les données velib",
    schedule_interval=timedelta(hours=1),
)


def ma_fonction_api() -> None:
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


velib_task = PythonOperator(
    task_id="recuperer_et_inserer_donnees",
    python_callable=ma_fonction_api,
    dag=dag,
)
