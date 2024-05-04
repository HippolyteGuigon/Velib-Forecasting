import requests
import time
import json

from velib_forecasting.configs.confs import load_conf, clean_params

main_params = load_conf(include=True)
main_params = clean_params(main_params)

METEO_API_KEY = main_params["METEO_API_KEY"]
METEO_ENDPOINT = main_params["METEO_ENDPOINT"]


def get_velib_data() -> json:
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

    local_time = time.localtime(time.time())
    local_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", local_time)

    city_name = "Paris"

    complete_url = f"{METEO_ENDPOINT}q={city_name}&appid={METEO_API_KEY}&units=metric"

    response = requests.get(complete_url)

    data = response.json()

    meteo_json = {
        "time": local_timestamp,
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
