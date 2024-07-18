import openmeteo_requests

import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def get_weather(latitude: float, longitude: float) -> dict:
    """
    Func to get weather information of location based on latitude and longitude of city
    :param latitude: Latitude of requested city
    :param longitude: Longitude of requested city
    :return: Dict of weather information
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
        "timezone": "Europe/Moscow",
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()[12]
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()[12]
    hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()[12]

    daily = response.Daily()
    daily_temperature_2m_max = max(daily.Variables(0).ValuesAsNumpy())
    daily_temperature_2m_min = min(daily.Variables(1).ValuesAsNumpy())
    daily_rain_sum = max(daily.Variables(2).ValuesAsNumpy())

    data = {
        "temperature": f"{round(hourly_temperature_2m)} C",
        "humidity": f"{hourly_relative_humidity_2m}%",
        "wind_speed": f"{round(hourly_wind_speed_10m)} км/ч",
        "daily_temp_max": f"{round(daily_temperature_2m_max)} C",
        "daily_temp_min": f"{round(daily_temperature_2m_min)} C",
        "daily_rain_sum": f"{round(daily_rain_sum)} мм",
    }
    return data
