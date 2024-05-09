import os
from google.cloud import bigquery
from pydantic import BaseModel
from datetime import datetime

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"
client = bigquery.Client()


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


def meteo_dataframe_to_bigquery(
    meteo_json,
    project_id="velib-forecasting",
    dataset_id="meteo_info",
    table_id="meteo_description",
):
    WeatherData(**meteo_json)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    query = f"SELECT DISTINCT time AS unique_timestamp FROM `{full_table_id}`"
    query_job = client.query(query)

    unique_timestamps = [
        row["unique_timestamp"].isoformat() for row in query_job.result()
    ]

    datasets = list(client.list_datasets())
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
        ]

        dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
        client.create_dataset(dataset_ref)

        table_ref = bigquery.Table(full_table_id, schema=schema)
        client.create_table(table_ref)

    if str(meteo_json["time"]) not in unique_timestamps:
        client.insert_rows_json(full_table_id, [meteo_json])
    else:
        return "Timestamp already exists"
