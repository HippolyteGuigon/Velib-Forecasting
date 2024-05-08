import requests
import json
import os

from velib_forecasting.configs.confs import load_conf, clean_params

from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"
client = bigquery.Client()

main_params = load_conf(include=True)
main_params = clean_params(main_params)

METEO_API_KEY = main_params["METEO_API_KEY"]
METEO_ENDPOINT = main_params["METEO_ENDPOINT"]


def get_meteo_data() -> json:
    """
    The goal of this function is to retrieve
    data from the meteo API and store them in
    a jsoon

    Arguments:
        -None
    Returns:
        -meteo_json: json: The json
        containing the json data
    """

    table_id = "velib-forecasting.velib_info.hourly_velib_places"
    query = f"SELECT MAX(time) AS last_timestamp FROM `{table_id}`"
    query_job = client.query(query)

    last_timestamp = list(query_job.result())[0]["last_timestamp"]

    city_name = "Paris"

    complete_url = f"{METEO_ENDPOINT}q={city_name}&appid={METEO_API_KEY}&units=\
        metric&dt={int(last_timestamp.timestamp())}"

    response = requests.get(complete_url)

    data = response.json()

    meteo_json = {
        "time": last_timestamp.isoformat(),
        "main_weather": data["weather"][0]["main"],
        "main_weather_description": data["weather"][0]["description"],
        "temperature": data["main"]["temp"],
        "temp_min": data["main"]["temp_min"],
        "temp_max": data["main"]["temp_max"],
        "pressure": data["main"]["pressure"],
        "humidity": data["main"]["humidity"],
        "visibility": data["visibility"],
        "wind_speed": data["wind"]["speed"],
        "wind_degree": data["wind"]["deg"],
        "clouds": data["clouds"]["all"],
    }

    return meteo_json
