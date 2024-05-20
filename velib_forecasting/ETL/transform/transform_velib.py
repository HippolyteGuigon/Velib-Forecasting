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

    cleaned_df_velib = cleaned_df_velib[cleaned_df_velib["station_code"].isdigit()]
    cleaned_df_velib["station_code"] = cleaned_df_velib["station_code"].astype(int)
    cleaned_df_velib["time"] = pd.to_datetime(cleaned_df_velib["time"]).dt.tz_localize(
        None
    )

    cleaned_df_velib.drop_duplicates(inplace=True, subset=["time", "station_code"])

    return cleaned_df_velib
