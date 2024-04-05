from setuptools import setup, find_packages

setup(
    name="velib_forecasting",
    version="0.1.0",
    packages=find_packages(include=["velib_forecasting", "velib_forecasting.*"]),
    description="Python programm for creating a forecasting\
        program for velib consumption in Pparis",
    author="Hippolyte Guigon",
    author_email="Hippolyte.guigon@hec.edu",
    url="https://github.com/HippolyteGuigon/Velib-Forecasting",
)
