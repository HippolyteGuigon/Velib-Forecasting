SELECT
  time,
  station_code,
  CONCAT(CAST(time AS STRING), ' ', CAST(station_code AS STRING)) AS time_station_code
FROM
  `velib-forecasting.velib_info.hourly_velib_places`
