import os

from google.cloud import bigquery
from pydantic import BaseModel
from datetime import datetime


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"


class WeatherData(BaseModel):
    time: datetime
    main_weather: str
    main_weather_description: str
    temperature: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    visibility: int
    wind_speed: float
    wind_degree: int
    clouds: int
    velib_matching_timestamp: datetime


def meteo_dataframe_to_bigquery(
    meteo_json,
    project_id="velib-forecasting",
    dataset_id="meteo_info",
    table_id="meteo_description",
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

    WeatherData(**meteo_json)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)
    datasets = list(client.list_datasets())  # Liste tous les datasets du projet
    dataset_names = [dataset.dataset_id for dataset in datasets]
    if dataset_id not in dataset_names:
        schema = [
            bigquery.SchemaField("time", "TIMESTAMP"),
            bigquery.SchemaField("main_weather", "STRING"),
            bigquery.SchemaField("main_weather_description", "STRING"),
            bigquery.SchemaField("temperature", "FLOAT"),
            bigquery.SchemaField("temp_min", "FLOAT"),
            bigquery.SchemaField("temp_max", "FLOAT"),
            bigquery.SchemaField("pressure", "INTEGER"),
            bigquery.SchemaField("humidity", "INTEGER"),
            bigquery.SchemaField("visibility", "INTEGER"),
            bigquery.SchemaField("wind_speed", "FLOAT"),
            bigquery.SchemaField("wind_degree", "INTEGER"),
            bigquery.SchemaField("clouds", "INTEGER"),
            bigquery.SchemaField("velib_matching_timestamp", "TIMESTAMP"),
        ]

        dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
        client.create_dataset(dataset_ref)

        table_ref = bigquery.Table(full_table_id, schema=schema)
        client.create_table(table_ref)

    client.insert_rows_json(full_table_id, [meteo_json])
