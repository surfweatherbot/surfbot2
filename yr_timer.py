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
        return ""
    base_symbol = symbol_code.split("_")[0]
    return WEATHER_EMOJIS.get(base_symbol, "🌤️")


def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def format_hour_key(dt_obj):
    hour = dt_obj.hour
    ampm = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour} {ampm}"


def fetch_weather():
    today = datetime.datetime.now(LOCAL_TZ).date()
    today_str = today.isoformat()

    # 1. Hent solnedgang først for å sette time-grensen
    sunrise_url = f"https://api.met.no/weatherapi/sunrise/3.0/sun?lat={LAT}&lon={LON}&date={today_str}"
    sun_data = get_json(sunrise_url)

    sun_details = sun_data["properties"]
    sunrise_raw = sun_details.get("sunrise", {}).get("time", "")
    sunset_raw = sun_details.get("sunset", {}).get("time", "")

    sunset_hour = None
    if sunset_raw:
        dt_sunset = datetime.datetime.fromisoformat(sunset_raw).astimezone(LOCAL_TZ)
        sunset_hour = dt_sunset.hour  # Eks: 20:36 gir sunset_hour = 20

    sunrise_time = (
        datetime.datetime.fromisoformat(sunrise_raw).astimezone(LOCAL_TZ).strftime("%H:%M")
        if sunrise_raw
        else "--:--"
    )
    sunset_time = (
        datetime.datetime.fromisoformat(sunset_raw).astimezone(LOCAL_TZ).strftime("%H:%M")
        if sunset_raw
        else "--:--"
    )

    # 2. Hent værvarsel og påfør månelogikk
    forecast_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={LAT}&lon={LON}"
    forecast_data = get_json(forecast_url)

    timeseries = forecast_data["properties"]["timeseries"]
    hourly_dict = {}

    for item in timeseries:
        dt_utc = datetime.datetime.fromisoformat(
            item["time"].replace("Z", "+00:00")
        )
        dt_local = dt_utc.astimezone(LOCAL_TZ)

        if dt_local.date() == today:
            hour_key = format_hour_key(dt_local)

            if hour_key in hourly_dict:
                continue

            instant = item["data"]["instant"]["details"]
            next_1h = item["data"].get("next_1_hours", {})
            symbol = next_1h.get("summary", {}).get("symbol_code", "")

            # Logikk for månesymbol hvis timen er større enn solnedgangstimen
            if sunset_hour is not None and dt_local.hour > sunset_hour:
                emoji = "🌑"
            else:
                emoji = get_emoji(symbol)

            wind_from = round(instant.get("wind_from_direction", 0))
            wind_to = (wind_from + 180) % 360

            hourly_dict[hour_key] = {
                "emoji": emoji,
                "vind": round(instant.get("wind_speed", 0)),
                "vind_retning": wind_to,
            }

    output = {
        "sun": {"sunrise": sunrise_time, "sunset": sunset_time},
        "hourly": hourly_dict,
    }

    js_content = f"window.WEATHER_DATA = {json.dumps(output, indent=2)};"

    with open("weather_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Værdata ble hentet og lagret til weather_data.js!")


if __name__ == "__main__":
    fetch_weather()
