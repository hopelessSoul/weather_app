import json
import os

from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from geopy.geocoders import Nominatim
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_app.utils.weather_requests.weather_requests import get_weather

geolocator = Nominatim(user_agent="my-weather-app")  # Get geolocator from geopy
cities = {}
cities_local = {}
with open("session_history.json", "w") as f:
    f.write("")


def write_to_file(city: str) -> None:
    """
    Func to write local and total search history
    :param city: str city got from post request
    :return: None
    """

    city = city.capitalize()
    if city in cities:
        if city in cities_local:
            cities_local[city] += 1
        cities[city] += 1
    else:
        cities_local[city] = 1
        cities[city] = 1

    with open("total_history.json", "w", encoding="utf-8") as file1, open(
            "session_history.json", "w", encoding="utf-8"
    ) as file2:
        json.dump(cities, file1, sort_keys=False, indent=4, ensure_ascii=False)
        json.dump(cities, file2, sort_keys=False, indent=4, ensure_ascii=False)


class GetCityView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Get template to give ability to search cities
        :param request:
        :return: HttpResponse
        """
        context = {}
        with open("session_history.json", "r", encoding="utf-8") as file:
            if os.stat("session_history.json").st_size == 0:
                context["errors"] = "История поиска пуста"
            else:
                context["history"] = json.load(file)
        return render(request, template_name="weather/city_input.html", context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Get city, that user enters in form and redirect user to page with weather
        :param request:
        :return:HttpResponse
        """
        request.session["session"] = True
        write_to_file(request.POST.get("city"))
        success_url = reverse_lazy(
            "weather_app:get_weather_in_city", kwargs={"city": request.POST.get("city")}
        )
        return HttpResponseRedirect(success_url)


class GetWeatherView(View):
    def get(self, request: HttpRequest, city: str) -> HttpResponse:
        """
        Get weather in requested city via func get_weather, from weather_app/utils/weather_requests
        :param request:
        :param city: City from user's input
        :return: HttpResponse
        """
        location = geolocator.geocode(city)
        weather = get_weather(location.latitude, location.longitude)
        context = {"city": city.capitalize(), "weather": weather}
        return render(request, "weather/weather_in_city.html", context=context)


class GetAllSearchHistory(APIView):
    def get(self, request: HttpRequest) -> Response:
        """
        API view to get all cities that has been searched and how many times they have been searched
        :param request:
        :return: Response
        """
        with open("total_history.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        return Response(data, status=status.HTTP_200_OK)
