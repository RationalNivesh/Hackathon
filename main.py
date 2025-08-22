import requests
from datetime import datetime
from openai import OpenAI

def time_from_utc_with_timezone(utc_with_tz):
    local_time = datetime.utcfromtimestamp(utc_with_tz)
    return local_time.strftime("%H:%M:%S")

# API keys
weather_api_key = "45637c43bd5e0a0173fce1e5c9af15af"   # OpenWeather
openai_api_key = "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"
# Get city name from user
city_name = input("Enter city name : ")

# API url
weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}"

# Get the response from weather url
response = requests.get(weather_url)
weather_data = response.json()

if weather_data['cod'] == 200:
    kelvin = 273.15
    temp = int(weather_data['main']['temp'] - kelvin)
    feels_like_temp = int(weather_data['main']['feels_like'] - kelvin)
    pressure = weather_data['main']['pressure']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed'] * 3.6
    sunrise = weather_data['sys']['sunrise']
    sunset = weather_data['sys']['sunset']
    timezone = weather_data['timezone']
    cloudy = weather_data['clouds']['all']
    description = weather_data['weather'][0]['description']

    sunrise_time = time_from_utc_with_timezone(sunrise + timezone)
    sunset_time = time_from_utc_with_timezone(sunset + timezone)

    print(f"\nWeather Information for City: {city_name}")
    print(f"Temperature (Celsius): {temp}")
    print(f"Feels like in (Celsius): {feels_like_temp}")
    print(f"Pressure: {pressure} hPa")
    print(f"Humidity: {humidity}%")
    print("Wind speed: {0:.2f} km/hr".format(wind_speed))
    print(f"Sunrise at {sunrise_time} and Sunset at {sunset_time}")
    print(f"Cloud: {cloudy}%")
    print(f"Info: {description}")

    # OpenAI part
    #lient = OpenAI(api_key=openai_api_key)

   #ai_prompt = f"The weather in {city_name} is {description} with temperature {temp}°C, humidity {humidity}%, and wind speed {wind_speed:.2f} km/hr. Should the user do outdoor activities in this weather?"
    #response = client.responses.create(
          #model="gpt-5",
          # input=ai_prompt
        #add a bracket
    #print("\nAI Suggestion:", response.output_text)
    from google_auth_oaouthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.ouath2.credentials import Credentials
    from openai import openai
    import os, datetime
    SCOPES= ["https:googleapis.com/auth/calendar.readonly"]
    from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os, datetime

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_events(max_results=5):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"

    events = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])

    return [f"{e.get('summary', '(No title)')} at {e['start'].get('dateTime', e['start'].get('date'))}" for e in events]
