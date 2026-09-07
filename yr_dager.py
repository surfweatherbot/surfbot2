import datetime
import json
import urllib.request
from zoneinfo import ZoneInfo

LAT = "58.96"
LON = "9.87"
LOCAL_TZ = ZoneInfo("Europe/Oslo")

HEADERS = {"User-Agent": "lokal hjemmeside jogranv@hotmail.com"}

WEATHER_EMOJIS = {
    "clearsky": "☀️",
    "fair": "🌤️",
    "partlycloudy": "⛅",
    "cloudy": "☁️",
    "rainshowers": "🌦️",
    "rainshowersandthunder": "⛈️",
    "heavyrainshowersandthunder": "⛈️",
    "heavyrainshowers": "🌧️",
    "rain": "🌧️",
    "heavyrain": "🌧️",
    "heavyrainandthunder": "⛈️",
    "sleet": "🌧️❄️",
    "snow": "❄️",
    "fog": "🌫️",
}


def get_emoji(symbol_code):
    if not symbol_code:
        return "❓"
    base_symbol = symbol_code.split("_")[0]
    return WEATHER_EMOJIS.get(base_symbol, "🌤️")


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def extract_symbol(item):
    data = item.get("data", {})
    for period in ["next_1_hours", "next_6_hours"]:
        symbol = data.get(period, {}).get("summary", {}).get("symbol_code")
        if symbol:
            return symbol
    return ""


def fetch_weather_longterm():
    today = datetime.datetime.now(LOCAL_TZ).date()
    target_dates = [today + datetime.timedelta(days=i) for i in range(1, 7)]

    # Formatert til DD.MM.YYYY for å matche dato_str i surf_longterm.js
    # Bruker "NATT" i stedet for "Night"
    forecast_by_day = {
        d.strftime("%d.%m.%Y"): {"AM": "❓", "PM": "❓", "NATT": "❓"}
        for d in target_dates
    }

    forecast_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={LAT}&lon={LON}"
    forecast_data = get_json(forecast_url)
    timeseries = forecast_data["properties"]["timeseries"]

    for item in timeseries:
        dt_utc = datetime.datetime.fromisoformat(
            item["time"].replace("Z", "+00:00")
        )
        dt_local = dt_utc.astimezone(LOCAL_TZ)
        date_str = dt_local.date().strftime("%d.%m.%Y")

        if date_str in forecast_by_day:
            hour = dt_local.hour
            symbol = extract_symbol(item)
            if not symbol:
                continue

            slot = None
            if hour in [6, 7, 8, 9]:
                slot = "AM"
            elif hour in [12, 13, 14, 15]:
                slot = "PM"
            elif hour in [18, 19, 20, 21]:
                slot = "NATT"

            if slot and forecast_by_day[date_str][slot] == "❓":
                forecast_by_day[date_str][slot] = get_emoji(symbol)

    js_content = f"window.WEATHER_LONGTERM_DATA = {json.dumps(forecast_by_day, indent=2, ensure_ascii=False)};"

    with open("weather_longterm.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Langtidsvarsel lagret til weather_longterm.js!"
    )


if __name__ == "__main__":
    fetch_weather_longterm()
