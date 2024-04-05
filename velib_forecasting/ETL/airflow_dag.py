from velib_forecasting.ETL.extract.velib_extract import get_velib_data
from velib_forecasting.ETL.load.load_velib import velib_dataframe_to_bigquery
from velib_forecasting.ETL.transform.transform_velib import transform_velib

df = get_velib_data()
df = transform_velib(df)
velib_dataframe_to_bigquery(df)
