import unittest
import os

from velib_forecasting.ETL.dags.airflow_dag import (
    velib_station_info_pipeline,
    meteo_info_pipeline,
)
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"
client = bigquery.Client()


class Test(unittest.TestCase):
    """
    The goal of this class is to implement unnitest
    and check everything commited makes sense
    """

    def test_velib_info_pipeline(self) -> None:
        """
        The goal of this function is to check
        that the information about velib station
        are well extracted and loaded on the BigQuery
        table

        Arguments:
            -None
        Returns:
            -None
        """

        table_id = "velib-forecasting.velib_info.hourly_velib_places"
        query = f"SELECT COUNT(*) AS total_rows FROM `{table_id}`"
        query_job = client.query(query)

        total_rows = list(query_job.result())[0]["total_rows"]

        result_insertion = velib_station_info_pipeline()

        query_check = f"SELECT COUNT(*) AS total_rows FROM `{table_id}`"
        query_job_check = client.query(query_check)

        total_rows_check = list(query_job_check.result())[0]["total_rows"]

        existing_timestamp_condition = "Timestamp already exists" == result_insertion
        rows_increased = total_rows_check > total_rows

        self.assertTrue(rows_increased or existing_timestamp_condition)

    def test_meteo_info_pipeline(self) -> None:
        """
        The goal of this function is to check
        that the information about meteo
        are well extracted and loaded on the BigQuery
        table

        Arguments:
            -None
        Returns:
            -None
        """

        table_id = "velib-forecasting.meteo_info.meteo_description"
        query = f"SELECT COUNT(*) AS total_rows FROM `{table_id}`"
        query_job = client.query(query)

        total_rows = list(query_job.result())[0]["total_rows"]

        result_insertion = meteo_info_pipeline()

        query_check = f"SELECT COUNT(*) AS total_rows FROM `{table_id}`"
        query_job_check = client.query(query_check)

        total_rows_check = list(query_job_check.result())[0]["total_rows"]

        existing_timestamp_condition = "Timestamp already exists" == result_insertion

        rows_increased = total_rows_check > total_rows

        self.assertTrue(rows_increased or existing_timestamp_condition)


if __name__ == "__main__":
    unittest.main()
