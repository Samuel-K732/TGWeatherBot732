class WeatherFormatter:
    def __init__(self, todays_weather: dict, three_days_weather: list):
        self.today = todays_weather
        self.three_days = three_days_weather
        self.weather = todays_weather.get("weather")

    def _format_part_of_the_day(self, part_of_the_day: str) -> str:
        data = self.weather.get(part_of_the_day)
        if data:
            return f"{data['temp']}°C, {data['status']}, 💨 {data['wind']} м/с"
        else:
            return "⏰ Время уже прошло"

    def _format_right_now(self) -> str:
        data = self.weather.get("right_now")
        if data:
            return f"Сейчас ({data['time']}): {data['temp']}°C, {data['status']}, 💨 {data['wind']} м/с"
        else:
            return "Данные недоступны"

    def format_today(self) -> str:
        return (
            f"📍 <b>{self.today['city']}, {self.today['country']}:</b>\n\n"
            f"🌅 Утро: {self._format_part_of_the_day('morning')}\n"
            f"🌞 День: {self._format_part_of_the_day('noon')}\n"
            f"🌇 Вечер: {self._format_part_of_the_day('afternoon')}\n"
            f"🌙 Ночь: {self._format_part_of_the_day('night')}\n\n"
            f"🕒 {self._format_right_now()}\n")

    def format_three_days(self) -> str:
        days = []
        for day in self.three_days:
            days.append(
                f"🔹 {day['date']}:\n"
                f"🌙 Ночь: {day['night_temp']}°C\n"
                f"🌞 День: {day['day_temp']}°C\n"
                f"💨 Ветер: {day['wind']} м/с\n")
        return "\n".join(days)
