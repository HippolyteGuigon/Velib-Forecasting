import os
import pandas as pd

from kfp import dsl, compiler
from kfp.dsl import component

from velib_forecasting.model.prophet_forecast import Forecasting_model


@component
def load_data_op() -> str:
    forecasting_model = Forecasting_model()
    forecasting_model.load_data()

    data_path = os.path.join(os.getcwd(), "data.csv")
    forecasting_model.data.to_csv(data_path, index=False)

    return data_path


@component
def train_model_op(data_path: str) -> str:
    model = Forecasting_model()
    model.load_data(data_path=data_path)
    model.full_station_training()

    model_dict_path = os.path.join(os.getcwd(), "model_dict.pkl")
    pd.to_pickle(model.model_dict, model_dict_path)

    return model_dict_path


@component
def evaluate_model_op(model_dict_path: str) -> float:
    model = Forecasting_model()
    model_dict = pd.read_pickle(model_dict_path)

    return model.get_average_rmse(model_dict=model_dict)


@dsl.pipeline(
    name="Velib Forecasting Model Training",
    description="A pipeline that trains and evaluates\
        a forecasting model for Velib stations.",
)
def velib_model_pipeline():
    data_path = load_data_op()
    model_dict_path = train_model_op(data_path=data_path.output)
    rmse = evaluate_model_op(model_dict_path=model_dict_path.output)
    return rmse


compiler.Compiler().compile(
    pipeline_func=velib_model_pipeline, package_path="velib_model_pipeline.json"
)
