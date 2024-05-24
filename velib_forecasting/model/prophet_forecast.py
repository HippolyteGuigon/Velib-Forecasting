import logging
import pandas as pd
import numpy as np
import warnings
import json

from prophet import Prophet
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from tqdm import tqdm
from typing import Union, Dict
from itertools import product

from velib_forecasting.utils import get_full_merged_data
from prophet.diagnostics import cross_validation, performance_metrics

logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").disabled = True

warnings.filterwarnings("ignore")

with open("configs/grid_search.json", "r") as f:
    grid_search_params = json.load(f)


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
        self.data = None
        self.model_dict = {}

    def load_data(self, path: str = None, data: pd.DataFrame = None) -> None:
        """
        The goal of this function is to load
        the full dataset containing both velib
        and meteo data

        Arguments:
            -path: If data should be loaded from
            an external data source, path of this
            data source
        Returns:
            -None
        """

        if path:
            self.data = pd.read_csv(path)
        elif data:
            self.data = data
        else:
            self.data = get_full_merged_data()

        self.unique_stations = self.data["station_name"].unique()

    def fit_single_station(
        self, station_name: str, test_size: float = 0.1
    ) -> Union[Prophet, pd.DataFrame, int]:
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
            -test_df: pd.DataFrame: The DataFrame with
            test data
            -total_capacity: int: The total capacity of
            the velib station
        """

        df_station = self.data[self.data["station_name"] == station_name]
        total_capacity = df_station.iloc[0]["total_capacity"]
        df_station.rename({"time": "ds"}, axis=1, inplace=True)
        df_station.sort_values(by="ds", inplace=True)
        df_station = df_station[["ds", "temperature", "number_bikes_available"]]
        df_station["ds"] = df_station["ds"].dt.tz_localize(None)

        df_station.columns = ["ds", "temperature", "y"]

        train_df, test_df = train_test_split(
            df_station, test_size=test_size, shuffle=False
        )

        all_params = [
            dict(zip(grid_search_params.keys(), v))
            for v in product(*grid_search_params.values())
        ]

        maes = []

        for params in all_params:
            m = Prophet(**params)
            m.add_regressor("temperature")
            m.fit(train_df)
            df_cv = cross_validation(m, horizon="1 day")
            df_p = performance_metrics(df_cv, rolling_window=1)
            maes.append(df_p["mae"].values[0])

        best_params = all_params[np.argmin(maes)]

        model_tuned = Prophet(**best_params)
        model_tuned.add_regressor("temperature")

        model_tuned.fit(train_df)

        return model_tuned, test_df, total_capacity

    def full_station_training(self) -> None:
        """
        The goal of this function is to train
        a Prophet model for every station composing
        the velib park

        Arguments:
            -None
        Returns:
            -None
        """

        for station in tqdm(self.unique_stations):
            model, test_df, total_capacity = self.fit_single_station(station)

            future = test_df[["ds", "temperature"]]
            forecast = model.predict(future)

            predictions = forecast[["ds", "yhat"]]

            predictions["yhat"] = predictions["yhat"].apply(
                lambda pred: min(pred, total_capacity)
            )
            predictions["yhat"] = predictions["yhat"].apply(lambda pred: max(pred, 0))

            merged_df = pd.merge(test_df, predictions, on="ds")

            rmse = mean_squared_error(merged_df["y"], merged_df["yhat"], squared=False)

            self.model_dict[station] = {
                "model": model,
                "total_capacity": total_capacity,
                "rmse": rmse,
                "test_df": test_df,
                "predictions": predictions,
            }

    def get_average_rmse(self, model_dict: Dict[str, Dict] = None) -> float:
        """
        The goal of this function is to
        get the average RMSE for all the
        station once the model was trained

        Arguments:
            -model_dict: Dict[List]: Pre-trained
            model, loaded if provided
        Returns:
            -global_rmse: float: The global
            rmse once the model was trained
        """

        if model_dict:
            self.model_dict = model_dict

        if not hasattr(self, "model_dict"):
            raise AssertionError(
                "Model should be trained on\
                                 all stations before evaluation"
            )

        global_rmse = np.mean(
            [
                np.round(v["rmse"] / v["total_capacity"], 2)
                for _, v in self.model_dict.items()
            ]
        )

        return global_rmse
