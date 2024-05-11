import logging

from prophet import Prophet
from sklearn.model_selection import train_test_split

from velib_forecasting.utils import get_full_merged_data

logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").disabled = True


class Forecasting_model:
    """
    The goal of this class is to
    have a full pipeline from
    raw data to forecasting model

    Arguments:
        -None
    Returns:
        -None
    """

    def __init__(self) -> None:
        self.data = get_full_merged_data()
        self.unique_stations = self.data["station_name"].unique()

    def fit_single_station(self, station_name: str, test_size: float = 0.2) -> Prophet:
        """
        The goal of this function is to fit
        the Prophet model to a single velib
        station

        Arguments:
            -station_name: str: The name of the
            station on which model will be fitted
            -test_size: float: The percentage of the
            data that will be used for testing
        Returns:
            -Prophet: The fitted model
        """

        model = Prophet()
        model.add_regressor("temperature")
        model.add_regressor("humidity")

        df_station = self.data[self.data["station_name"] == station_name]
        df_station.rename({"time": "ds"}, axis=1, inplace=True)
        df_station.sort_values(by="ds", inplace=True)
        df_station = df_station[
            ["ds", "temperature", "humidity", "number_bikes_available"]
        ]
        df_station["ds"] = df_station["ds"].dt.tz_localize(None)

        df_station.columns = ["ds", "temperature", "humidity", "y"]

        train_df, _ = train_test_split(df_station, test_size=test_size, shuffle=False)

        model.fit(train_df)

        return model
