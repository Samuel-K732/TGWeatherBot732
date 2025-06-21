import requests
import datetime
from config import WEATHER_API_KEY


class WeatherForecast:
    def __init__(self, lat: float, lon: float, api_key: str = WEATHER_API_KEY, units: str = "metric",
                 lang: str = "ru"):
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.units = units
        self.lang = lang
        self.endpoint = "https://api.openweathermap.org/data/2.5/forecast"
        self.three_days_forecast = []
        self.todays_weather = {}
        self.today = datetime.datetime.today().strftime("%d.%m.%Y")
        self.time_now = datetime.datetime.today().strftime("%H:%M")

        self.forecast_params = {"lat": self.lat,
                                "lon": self.lon,
                                "appid": self.api_key,
                                "units": self.units,
                                "lang": self.lang
                                }

    def _load_three_days_forecast(self) -> list:
        self.forecast_params["cnt"] = 32

        forecast_response = requests.get(self.endpoint, params=self.forecast_params)

        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()["list"]
            day_data = None

            for forecast in forecast_data:
                if len(self.three_days_forecast) == 3:
                    break

                dt = datetime.datetime.fromtimestamp(forecast["dt"])
                formatted_dt = dt.strftime("%d.%m.%Y")
                formatted_time = dt.strftime("%H:%M")
                temp = forecast["main"]["temp"]

                if self.today not in forecast and formatted_time == "00:00" and day_data is None:
                    day_data = {"date": formatted_dt,
                                "night_temp": temp,
                                "day_temp": 0,
                                "wind": 0
                                }

                elif formatted_time == "12:00" and day_data is not None:
                    day_data["day_temp"] = temp
                    day_data["wind"] = forecast["wind"]["speed"]
                    self.three_days_forecast.append(day_data)
                    day_data = None
        else:
            print(f"Ошибка: {forecast_response.status_code}, {forecast_response.json()['message']}")

        return self.three_days_forecast

    def _get_part_of_day(self, hour: int) -> str | None:
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour <= 15:
            return "noon"
        elif 15 < hour < 21:
            return "afternoon"
        elif hour == 21:
            return "night"
        else:
            return None

    def _load_todays_forecast(self) -> dict:
        self.forecast_params["cnt"] = 8
        self.todays_weather = {
            "date": self.today,
            "country": "",
            "city": "",
            "weather": {
                "morning": None,
                "noon": None,
                "afternoon": None,
                "night": None
            }
        }

        todays_forecast_response = requests.get(self.endpoint, params=self.forecast_params)
        if todays_forecast_response.status_code == 200:
            todays_forecast_data = todays_forecast_response.json()
            self.todays_weather["country"] = todays_forecast_data["city"]["country"]
            self.todays_weather["city"] = todays_forecast_data["city"]["name"]

            recieved_forecasts = set()
            for forecast in todays_forecast_data["list"]:
                dt = datetime.datetime.fromtimestamp(forecast["dt"])
                formatted_dt = dt.strftime("%d.%m.%Y")
                formatted_time = dt.strftime("%H:%M")
                hour = dt.strftime("%H")
                if self.today == formatted_dt:
                    part_of_day = self._get_part_of_day(int(hour))
                    if part_of_day and part_of_day not in recieved_forecasts:
                        self.todays_weather["weather"][part_of_day] = {
                            "time": formatted_time,
                            "status": forecast["weather"][0]["description"],
                            "temp": forecast["main"]["temp"],
                            "feels_like_temp": forecast["main"]["feels_like"],
                            "wind": forecast["wind"]["speed"]
                        }
                        recieved_forecasts.add(part_of_day)
        else:
            print(f"Ошибка: {todays_forecast_response.status_code}, {todays_forecast_response.json()['message']}")

        right_now_weather_endpoint = "https://api.openweathermap.org/data/2.5/weather"
        right_now_weather_response = requests.get(right_now_weather_endpoint, params=self.forecast_params)
        if right_now_weather_response.status_code == 200:
            right_now_weather_data = right_now_weather_response.json()
            self.todays_weather["weather"]["right_now"] = {
                "time": self.time_now,
                "status": right_now_weather_data["weather"][0]["description"],
                "temp": right_now_weather_data["main"]["temp"],
                "feels_like_temp": right_now_weather_data["main"]["feels_like"],
                "wind": right_now_weather_data["wind"]["speed"]
            }
        else:
            print(f"Ошибка: {right_now_weather_response.status_code}, {right_now_weather_response.json()['message']}")

        return self.todays_weather

    def get_forecast(self) -> list:
        full_forecast = [self._load_todays_forecast(), self._load_three_days_forecast()]
        return full_forecast
