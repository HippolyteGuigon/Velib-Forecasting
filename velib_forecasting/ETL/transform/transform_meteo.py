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

    pass
