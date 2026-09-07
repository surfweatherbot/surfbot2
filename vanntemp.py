import json
import requests

# Koordinatene for Saltstein
LAT = "58.962"
LON = "9.863"

url = f"https://api.met.no/weatherapi/oceanforecast/2.0/complete?lat={LAT}&lon={LON}"

headers = {
    'User-Agent': 'hjemmeside lokal jogranv@hotmail.com'
}

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        current_details = data['properties']['timeseries'][0]['data']['instant']['details']
        water_temp = current_details.get('sea_water_temperature')

        # Lagrer dataene i en JS-fil
        js_content = f"window.WATER_TEMP_DATA = {{ temp: {water_temp} }};\n"
        
        with open("water_temp.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        print(f"Suksess! Genererte water_temp.js med temperatur: {water_temp} °C")
    else:
        print(f"Feil ved henting av data: statuskode {response.status_code}")

except Exception as e:
    print(f"Det oppstod en feil: {e}")
