import json
import os

from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"
client = bigquery.Client()


def transform_meteo(meteo_json: json) -> json:
    """
    The goal of this function is to transform
    meteo data once it was retrieved from the
    API

    Arguments:
        -meteo_json: json: The raw meteo
        data
    Returns:
        -cleaned_json_meteo: json: The meteo
        json once it is treated
    """

    table_id = "velib-forecasting.velib_info.hourly_velib_places"
    query = f"SELECT MAX(time) AS last_timestamp FROM `{table_id}`"
    query_job = client.query(query)

    last_timestamp = list(query_job.result())[0]["last_timestamp"]
    meteo_json["velib_matching_timestamp"] = last_timestamp

    return meteo_json
