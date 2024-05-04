import pandas as pd
import pandera as pa
import os

from pandas_gbq import to_gbq
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"


def meteo_dataframe_to_bigquery(
    meteo_json,
    project_id="velib-forecasting",
    dataset_id="meteo_info",
    table_id="meteo_description",
    if_exists="append",
):
    """
    The goal of this function is to add the meteo json to the
    bigquery table

    Arguments:
        -meteo_json: json: The json with meteo data
        -project_id: str: The id of the gcp project
        -dataset_id: str: The id of the gcp project
        -table_id: str: The id of the bigquery table
    Returns:
        -None
    """

    dataframe = pd.json_normalize(meteo_json)

    schema_meteo_processed = pa.DataFrameSchema(
        {
            "time": pa.Column(pa.Timestamp, nullable=False),
            "main_weather": pa.Column(pa.String, nullable=True),
            "main_weather_description": pa.Column(pa.String, nullable=True),
            "temperature": pa.Column(pa.Float, nullable=True),
            "temp_min": pa.Column(pa.Float, nullable=True),
            "temp_max": pa.Column(pa.Float, nullable=True),
            "pressure": pa.Column(pa.Int, nullable=True),
            "humidity": pa.Column(pa.Int, nullable=True),
            "visibility": pa.Column(pa.Int, nullable=True),
            "wind_speed": pa.Column(pa.Float, nullable=True),
            "wind_degree": pa.Column(pa.Int, nullable=True),
            "clouds": pa.Column(pa.Int, nullable=True),
        }
    )

    schema_meteo_processed.validate(dataframe)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)
    datasets = list(client.list_datasets())  # Liste tous les datasets du projet
    dataset_names = [dataset.dataset_id for dataset in datasets]
    if dataset_id not in dataset_names:
        dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
        client.create_dataset(dataset_ref)

    to_gbq(dataframe, full_table_id, project_id=project_id, if_exists=if_exists)
