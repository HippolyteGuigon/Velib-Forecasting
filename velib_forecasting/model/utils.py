import pandas as pd
import matplotlib.pyplot as plt

from io import BytesIO


def plot_forecast(
    test_df: pd.DataFrame, predictions: pd.DataFrame, station_name: str
) -> BytesIO:
    """
    The goal of this function is to get
    a visual graph of the predictions
    made for a given station

    Arguments:
        -test_df: pd.DataFrame: The part of the dataset
        kept for testing
        -predictions: pd.DataFrame: The predictions made
        by the forecasting model
        -station_name: str: The station name for which
        the forecasting is made
    Returns:
        -buf: Bytes.IO: The graph converted in appropriate
        format
    """

    plt.figure(figsize=(12, 6))

    plt.plot(test_df["ds"], test_df["y"], "b-", label="Vraies Données")

    plt.plot(predictions["ds"], predictions["yhat"], "r-", label="Prédictions")

    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Valeur")
    plt.title(f"Forecasting predictions for station {station_name}")

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    return buf
