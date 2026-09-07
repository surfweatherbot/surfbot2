import json
import requests

# Koordinater midt i Skagerrak
lat, lon = 57.9, 9.5

headers = {'User-Agent': 'SurfDashboard/1.0 (din-epost@eksempel.no)'}
url = f"https://api.met.no/weatherapi/oceanforecast/2.0/complete?lat={lat}&lon={lon}"

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Hent bølgehøyde for nåværende time
    wave_height = data['properties']['timeseries'][0]['data']['instant']['details']['sea_surface_wave_height']
except Exception as e:
    print(f"Feil ved henting av bølgehøyde: {e}")
    wave_height = None

# Skriv ut som en JavaScript-fil
with open("wave_height.js", "w", encoding="utf-8") as f:
    f.write(f"window.WAVE_HEIGHT_DATA = {{ height: {json.dumps(wave_height)} }};\n")

print(f"Lagret wave_height.js med verdi: {wave_height} m")
