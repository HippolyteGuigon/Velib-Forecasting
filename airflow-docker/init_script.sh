#!/bin/bash

# Exécuter la commande airflow scheduler
airflow scheduler &

# Démarrer le serveur Web Airflow
airflow webserver
