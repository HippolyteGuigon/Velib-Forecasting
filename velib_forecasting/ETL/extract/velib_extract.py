import requests
import pandas as pd

from velib_forecasting.configs.confs import load_conf, clean_params

main_params = load_conf("configs/main.yml",include=True)
main_params = clean_params(main_params)

VELIB_ENDPOINT=main_params["VELIB_ENDPOINT"]

def get_velib_data()->pd.DataFrame:
    """
    The goal of this function is to retrieve
    data from the velib API and store them in
    a pandas DataFrame
    
    Arguments:
        -None
    Returns:
        -df_velib: pd.DataFrame: The DataFrame
        containing the retrieved velib data
    """

    resp = requests.get(VELIB_ENDPOINT)
    data = resp.json()

    df_velib = pd.DataFrame(columns =['time', 'station_name', 'station_code', 'station_status',
                             "number_bikes_available", "number_docks_available", "total_capacity", 
                            ])

    for rec in data['records']:
        df_velib.loc[len(df_velib)] = [   rec['record_timestamp'],
                                rec['fields']['name'],
                                rec['fields']['stationcode'],
                                rec['fields']['is_renting'],
                                rec['fields']['numbikesavailable'],
                                rec['fields']['numdocksavailable'], 
                                rec['fields']['capacity']
                                ]
        
    return df_velib