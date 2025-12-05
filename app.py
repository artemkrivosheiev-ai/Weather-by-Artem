from flask import Flask, render_template, request, redirect, url_for, session
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/"

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Инициализация сессий
@app.before_request
def init_session():
    if "history" not in session:
        session["history"] = []
    if "lang" not in session:
        session["lang"] = "ru"
    if "last_city" not in session:
        session["last_city"] = None

# Переключение языка
@app.route("/change_lang")
def change_lang():
    session["lang"] = "en" if session.get("lang")=="ru" else "ru"
    session.modified = True
    return redirect(request.referrer or url_for("index"))

# Советы по погоде
def get_weather_tips(weather):
    tips = []
    if weather["temp"] >= 30:
        tips.append({"ru": "Наденьте лёгкую одежду", "en": "Take light clothing"})
    elif weather["temp"] <= 10:
        tips.append({"ru": "Оденьтесь тепло", "en": "Dress warmly"})
    else:
        tips.append({"ru": "Одевайтесь по погоде", "en": "Dress appropriately"})
    if "rain" in weather["desc"].lower():
        tips.append({"ru": "Возьмите зонт", "en": "Take an umbrella"})
    if "sun" in weather["desc"].lower() or "clear" in weather["desc"].lower():
        tips.append({"ru": "Можно взять солнцезащитные очки", "en": "Take sunglasses"})
    if weather["wind"] > 8:
        tips.append({"ru": "На улице ветрено", "en": "It's windy outside"})
    return tips

# Главная страница
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    main_weather = "Clear"
    tips = []
    lang = session.get("lang", "ru")

    texts = {
        "error_city": {"ru": "Введите название города!", "en": "Please enter a city name!"},
        "city_not_found": {"ru": "Город не найден 😔", "en": "City not found 😔"},
        "server_error": {"ru": "Ошибка сервера", "en": "Server error"},
    }

    # Определяем город для запроса
    city = request.form.get("city", "").strip()
    if not city and session.get("last_city"):
        city = session["last_city"]  # используем последний введённый город

    if city:
        try:
            url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric&lang={lang}"
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if data.get("cod") != "200":
                weather_data = {"error": texts["city_not_found"][lang]}
            else:
                city_name = data["city"]["name"]

                # Сохраняем город в истории и как последний
                if city_name not in session["history"]:
                    session["history"].append(city_name)
                session["last_city"] = city_name
                session.modified = True

                current = data["list"][0]
                weather_data = {
                    "city": data["city"]["name"],
                    "country": data["city"]["country"],
                    "temp": round(current["main"]["temp"]),
                    "feels_like": round(current["main"]["feels_like"]),
                    "humidity": current["main"]["humidity"],
                    "wind": current["wind"]["speed"],
                    "desc": current["weather"][0]["description"].capitalize(),
                    "icon": current["weather"][0]["icon"]
                }
                main_weather = current["weather"][0]["main"]
                tips = get_weather_tips(weather_data)

                # Прогноз
                forecast_data = []
                for i in range(0,len(data["list"]),8):
                    item = data["list"][i]
                    date_obj = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    forecast_data.append({
                        "date": date_obj.strftime("%a %d.%m"),
                        "temp": round(item["main"]["temp"]),
                        "desc": item["weather"][0]["description"].capitalize(),
                        "icon": item["weather"][0]["icon"]
                    })

        except requests.exceptions.RequestException as e:
            weather_data = {"error": f"{texts['server_error'][lang]}: {e}"}

    return render_template(
        "index.html",
        weather=weather_data,
        forecast=forecast_data,
        mainWeather=main_weather,
        tips=tips,
        lang=lang
    )

# История
@app.route("/history", methods=["GET","POST"])
def history():
    lang = session.get("lang","ru")
    texts = {
        "title": {"ru":"История поиска","en":"Search History"},
        "empty": {"ru":"История пуста 😔","en":"History is empty 😔"},
        "clear_btn": {"ru":"Очистить историю","en":"Clear history"},
    }

    if request.method=="POST":
        session["history"] = []
        session.modified = True
        return redirect(url_for("history"))

    return render_template(
        "history.html",
        history=session.get("history",[]),
        lang=lang,
        texts=texts
    )

# Сравнение городов
@app.route("/compare", methods=["GET", "POST"])
def compare():
    lang = session.get("lang", "ru")
    city1_data = None
    city2_data = None
    forecast1 = []
    forecast2 = []
    error = None

    if request.method == "POST":
        city1 = request.form.get("city1","").strip()
        city2 = request.form.get("city2","").strip()

        if not city1 or not city2:
            error = "Введите оба города!" if lang=="ru" else "Please enter both cities!"
        else:
            try:
                def fetch_weather(city):
                    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric&lang={lang}"
                    resp = requests.get(url, timeout=8)
                    data = resp.json()
                    if data.get("cod") != "200":
                        return None
                    current = data["list"][0]
                    weather = {
                        "city": data["city"]["name"],
                        "country": data["city"]["country"],
                        "temp": round(current["main"]["temp"]),
                        "feels_like": round(current["main"]["feels_like"]),
                        "humidity": current["main"]["humidity"],
                        "wind": current["wind"]["speed"],
                        "desc": current["weather"][0]["description"].capitalize(),
                        "icon": current["weather"][0]["icon"]
                    }
                    forecast_data = []
                    for i in range(0,len(data["list"]),8):
                        item = data["list"][i]
                        date_obj = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                        forecast_data.append({
                            "date": date_obj.strftime("%a %d.%m"),
                            "temp": round(item["main"]["temp"]),
                            "desc": item["weather"][0]["description"].capitalize(),
                            "icon": item["weather"][0]["icon"]
                        })
                    return weather, forecast_data

                city1_data, forecast1 = fetch_weather(city1)
                city2_data, forecast2 = fetch_weather(city2)

                if not city1_data or not city2_data:
                    error = "Город не найден 😔" if lang=="ru" else "City not found 😔"

            except requests.exceptions.RequestException as e:
                error = f"Ошибка сервера: {e}" if lang=="ru" else f"Server error: {e}"

    return render_template(
        "compare.html",
        lang=lang,
        city1=city1_data,
        city2=city2_data,
        forecast1=forecast1,
        forecast2=forecast2,
        error=error
    )

# Страница карты
@app.route("/map")
def map_page():
    city = request.args.get("city", "")
    country = request.args.get("country", "")
    return render_template("map.html", city=city, country=country, lang=session.get("lang", "ru"))

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)








\







