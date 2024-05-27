import re
import pandas as pd
import mlflow
import mlflow.sklearn
import logging

from velib_forecasting.model.prophet_forecast import Forecasting_model
from velib_forecasting.model.utils import plot_forecast

mlflow.set_tracking_uri("http://35.204.218.116:80")


def load_data() -> pd.DataFrame:
    logging.info("Loading data...")
    forecasting_model = Forecasting_model()
    forecasting_model.load_data()
    logging.info("Data successfully loaded!")

    return forecasting_model


def train_model(model) -> str:
    logging.info("Beginning model training...")
    model.full_station_training()
    logging.info("Model successfully trained")

    return model


def evaluate_model(model) -> str:
    return model.get_average_rmse()


with mlflow.start_run(run_name="Velib Pipeline"):
    with mlflow.start_run(run_name="Load Data", nested=True):
        model = load_data()
        mlflow.log_param("train_size", model.data.shape[0])

    with mlflow.start_run(run_name="Train Model", nested=True):
        trained_model = train_model(model=model)
        mlflow.sklearn.log_model(trained_model, "Prophet Forecast model")

    with mlflow.start_run(run_name="Single station evaluation", nested=True):
        for station_name in trained_model.unique_stations:
            cleaned_station_name = re.sub(r"[^a-zA-Z0-9_\-\. /]", "_", station_name)
            mlflow.log_metric(
                f"{cleaned_station_name} station evaluation RMSE",
                trained_model.model_dict[station_name]["rmse"],
            )
            test_df = trained_model.model_dict[station_name]["test_df"]
            predictions = trained_model.model_dict[station_name]["predictions"]
            plot = plot_forecast(test_df, predictions, station_name)
            mlflow.log_figure(plot, f"plot_station{station_name}.png")

    with mlflow.start_run(run_name="Evaluate Model", nested=True):
        metrics = evaluate_model(trained_model)
        mlflow.log_metric("Average RMSE", metrics)
