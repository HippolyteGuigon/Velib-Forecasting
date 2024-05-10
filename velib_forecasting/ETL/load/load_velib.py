import pandera as pa
import pandas as pd
import os

from pandas_gbq import to_gbq
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "velib-forecasting-auth.json"


def velib_dataframe_to_bigquery(
    dataframe,
    project_id="velib-forecasting",
    dataset_id="velib_info",
    table_id="hourly_velib_places",
    if_exists="append",
):
    """
    The goal of this function is to add the velib DataFrame to the
    bigquery table

    Arguments:
        -dataframe: pd.DataFrame: The dataframe with velib data
        -project_id: str: The id of the gcp project
        -dataset_id: str: The id of the gcp project
        -table_id: str: The id of the bigquery table
    Returns:
        -None
    """

    schema_velib_processed = pa.DataFrameSchema(
        {
            "time": pa.Column(pa.Timestamp, nullable=True),
            "station_name": pa.Column(pa.String, nullable=True),
            "station_code": pa.Column(pa.Int, nullable=True),
            "station_status": pa.Column(pa.String, nullable=True),
            "number_bikes_available": pa.Column(pa.Int, nullable=True),
            "number_docks_available": pa.Column(pa.Int, nullable=True),
            "total_capacity": pa.Column(pa.Int, nullable=True),
        }
    )

    schema_velib_processed.validate(dataframe)

    full_table_id = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)

    query = f"SELECT DISTINCT time  AS unique_timestamp, \
            station_code AS station_code_reference \
            FROM `{full_table_id}`\
            WHERE time >= CURRENT_TIMESTAMP() - INTERVAL 12 HOUR"

    query_job = client.query(query)

    df_reference = query_job.to_dataframe()

    datasets = list(client.list_datasets())
    dataset_names = [dataset.dataset_id for dataset in datasets]

    if dataset_id not in dataset_names:
        dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
        client.create_dataset(dataset_ref)

    dataframe_columns = dataframe.columns
    dataframe["time"] = pd.to_datetime(dataframe["time"], utc=True)
    merged_dataframe = dataframe.merge(
        df_reference,
        left_on=["time", "station_code"],
        right_on=["unique_timestamp", "station_code_reference"],
        how="outer",
    )

    merged_dataframe = merged_dataframe[
        merged_dataframe["station_code_reference"].isna()
    ]
    merged_dataframe = merged_dataframe[dataframe_columns]

    if merged_dataframe.empty:
        return "Timestamp already exists"
    else:
        to_gbq(
            merged_dataframe, full_table_id, project_id=project_id, if_exists=if_exists
        )
