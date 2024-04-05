import pandas as pd


def transform_velib(df_velib: pd.DataFrame) -> pd.DataFrame:
    """
    The goal of this function is to transform
    velib data once it was retrieved from the
    API

    Arguments:
        -df_velib: pd.DataFrame: The raw velib
        data
    Returns:
        -cleaned_df_velib: pd.DataFrame: The velib
        DataFrame once it is treated
    """

    cleaned_df_velib = df_velib[df_velib["station_status"] == "OUI"]

    return cleaned_df_velib
