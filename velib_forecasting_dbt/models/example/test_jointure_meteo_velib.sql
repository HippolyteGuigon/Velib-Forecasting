WITH velib_meteo_outer_merged AS (
    SELECT meteo.time AS meteo_time,
           velib.time AS velib_time
    FROM `velib-forecasting.dbt_dataset.meteo_description` AS meteo
    FULL OUTER JOIN `velib-forecasting.velib_info.hourly_velib_places` AS velib
    ON meteo.time = velib.time
)

SELECT
    *
FROM velib_meteo_outer_merged
