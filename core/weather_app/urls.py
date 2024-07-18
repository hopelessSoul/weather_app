from django.urls import path
from . import views

app_name = "weather_app"

urlpatterns = [
    path("", views.GetCityView.as_view(), name="get_city"),
    path("<str:city>", views.GetWeatherView.as_view(), name="get_weather_in_city"),
    path(
        "api/search_history",
        views.GetAllSearchHistory.as_view(),
        name="get_all_history",
    ),
]
