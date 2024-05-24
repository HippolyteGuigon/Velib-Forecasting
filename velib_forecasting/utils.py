import pandas as pd
import os

from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"


def get_full_merged_data() -> pd.DataFrame:
    """
    The goal of this function is to get the
    velib and meteo data from BigQuery all
    merged in a single DataFrame

    Arguments:
        -None
    Returns:
        -df_merged: pd.DataFrame: The dataframe
        containing all velib and meteo data merged
    """

    client = bigquery.Client(project="velib-forecasting")

    query = "SELECT \
                * \
              FROM \
                `velib-forecasting.velib_info.hourly_velib_places` velib \
              INNER JOIN \
                `velib-forecasting.meteo_info.meteo_description` meteo \
              ON \
                velib.time=meteo.time"

    query_job = client.query(query)

    df_merged = query_job.to_dataframe()

    return df_merged
