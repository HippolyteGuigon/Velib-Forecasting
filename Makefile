activate_environment:
	conda activate velib_forecasting_project

setup:
	python3 setup.py install

connect_gcp:
	gcloud auth login

load_google_creditentials:
	export GOOGLE_APPLICATION_CREDENTIALS=velib-forecasting-auth.json
