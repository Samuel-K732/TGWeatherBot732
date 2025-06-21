import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN
from weather_api import WeatherForecast
from weather_formatter import WeatherFormatter
from user_data_manager import UserDataManager

data = UserDataManager("user_data.json")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(storage=storage)


class Form(StatesGroup):
    waiting_for_coords = State()


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="☁️ Узнать погоду")],
    [KeyboardButton(text="📍 Передать геопозицию", request_location=True)],
    [KeyboardButton(text="📌 Ввести координаты вручную")],
    [KeyboardButton(text="ℹ️ Информация")]],
    resize_keyboard=True)


@dispatcher.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привет! Я — бот прогноза погоды 🌤️\n\n"
        "Если вы используете меня впервые, пожалуйста, передайте свою геопозицию. "
        "Вы можете сделать это либо с помощью автоматической передачи местоположения, "
        "либо ввести координаты вручную.\n\n"
        "Я запоминаю вашу геопозицию, поэтому вам не нужно отправлять её каждый раз при запросе погоды. "
        "Если вы смените местоположение — например, уедете в отпуск или к бабушке в деревню — "
        "не забудьте обновить геопозицию через соответствующие кнопки.\n\n"
        "Желаю приятного пользования и не забывайте одеваться по погоде! ☁️",
        reply_markup=main_menu)


@dispatcher.message(F.location)
async def get_location(message: types.Message):
    user_id = str(message.from_user.id)
    lat = message.location.latitude
    lon = message.location.longitude

    data.set(user_id, {"lat": lat, "lon": lon})
    await message.answer("✅ Геопозиция сохранена")


@dispatcher.message(F.text == "📌 Ввести координаты вручную")
async def ask_for_coords(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите координаты в формате:\nширота, долгота\n"
                         "Пример: 10.1010, 10.1010\nИли напишите <b>отмена</b> чтобы выйти.",
                         parse_mode="HTML")
    await state.set_state(Form.waiting_for_coords)


@dispatcher.message(Form.waiting_for_coords, F.text.lower() == "отмена")
async def cancel_coords_input(message: types.Message, state: FSMContext):
    await message.answer("Ввод координат отменён.", reply_markup=main_menu)
    await state.clear()


@dispatcher.message(Form.waiting_for_coords)
async def get_coords(message: types.Message, state: FSMContext):
    try:
        lat_str, lon_str = message.text.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except Exception:
        await message.answer("Кооррдинаты введены неправильно. Введите их в формате: 10.1010, 10.1010")
        return

    user_id = str(message.from_user.id)
    data.set(user_id, {"lat": lat, "lon": lon})

    await message.answer("✅ Геопозиция сохранена")
    await state.clear()


@dispatcher.message(F.text == "☁️ Узнать погоду")
async def get_weather_menu(message: types.Message):
    user_id = str(message.from_user.id)
    location = data.get(user_id)

    if not data.exist(user_id):
        await message.answer("Данные геопозиции отсутствуют. Пожалуйста, отправьте свою геопозицию 📍")
        return

    weather = WeatherForecast(lat=location["lat"], lon=location["lon"])
    forecast = weather.get_forecast()
    formatter = WeatherFormatter(todays_weather=forecast[0], three_days_weather=forecast[1])

    await message.answer(formatter.format_today() + "\n\n" +
                         "<b>Погода на следующие три дня:</b>\n\n" +
                         formatter.format_three_days(),
                         parse_mode="HTML",
                         reply_markup=main_menu)


@dispatcher.message(F.text == "ℹ️ Информация")
async def info_cmd(message: types.Message):
    await start_cmd(message)


async def main():
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
