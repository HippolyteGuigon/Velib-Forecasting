import re
import pandas as pd
import mlflow
import mlflow.sklearn
import logging

from velib_forecasting.model.prophet_forecast import Forecasting_model

mlflow.set_tracking_uri("http://127.0.0.1:5000")


def load_data() -> pd.DataFrame:
    logging.info("Loading data...")
    forecasting_model = Forecasting_model()
    forecasting_model.load_data()
    logging.info("Data succesfully loaded !")

    return forecasting_model


def train_model(model) -> str:
    logging.info("Beginning model training...")
    model.full_station_training()
    logging.info("Model sucessfully trained")

    return model


def evaluate_model(model) -> str:
    return model.get_average_rmse()


with mlflow.start_run(run_name="Velib Pipeline"):
    with mlflow.start_run(run_name="Load Data", nested=True):
        model = load_data()
        mlflow.log_param("train_size", model.data.shape[0])

    # Étape 2: Entraîner le modèle
    with mlflow.start_run(run_name="Train Model", nested=True):
        model = train_model(model=model)
        mlflow.sklearn.log_model(model, "Prophet Forcast model")

    with mlflow.start_run(run_name="Single station evaluation", nested=True):
        for station_name in model.unique_stations:
            cleaned_station_name = re.sub(r"[^a-zA-Z0-9_\-\. /]", "_", station_name)
            mlflow.log_metric(
                f"{cleaned_station_name} station evaluation RMSE",
                model.model_dict[station_name][2],
            )

    # Étape 3: Évaluer le modèle
    with mlflow.start_run(run_name="Evaluate Model", nested=True):
        metrics = evaluate_model(model)
        mlflow.log_metric("Average RMSE", metrics)
