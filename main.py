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
    will_rain = "Yes" if "rain" in weather_data else "No"

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
    print(f"Rain:{will_rain}")
num_events=int(input("Number of events today"))
events=[]
for i in range(1, num_events + 1):
    print(f"\nEvent {i}:")
    event_name = input("Enter the event name: ")
    event_time = input("Enter the event time (e.g., 2:00 PM): ")
    events.append({"name": event_name, "time": event_time})

prompt = f"""
Should I do the following events today: {events}
with the current weather conditions:
Temperature (Celsius): {temp}
Feels like (Celsius): {feels_like_temp}
Pressure: {pressure} hPa
Humidity: {humidity}%
Wind speed: {wind_speed:.2f} km/hr
Sunrise at: {sunrise_time}
Sunset at: {sunset_time}
Cloud: {cloudy}%
Info: {description}
Rain: {will_rain}
"""
import openai
import requests
import openai
from datetime import datetime

# ========== CONFIG ==========
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"   # Get from https://openweathermap.org/api
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"             # Get from https://platform.openai.com

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ========== WEATHER FETCH ==========
def get_weather(city="Delhi"):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    weather_data = {
        "city": city,
        "temperature": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "wind_speed": response["wind"]["speed"],
        "rain": response.get("rain", {}).get("1h", 0),
        "condition": response["weather"][0]["description"]
    }
    return weather_data

# ========== GPT CHAT ==========
def chat_with_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ========== MAIN ==========
def main():
    # Ask user for schedule
    num_events = int(input("How many events do you have today? "))
    events = []
    for i in range(num_events):
        event = input(f"Enter event {i+1} (e.g., 'Math class at 4 PM'): ")
        events.append(event)

    # Get weather
    city = input("Enter your city: ")
    weather = get_weather(city)

    # Prepare prompt for GPT
    prompt = (
        f"Here is my schedule for today:\n{events}\n\n"
        f"Here is the current weather in {weather['city']}:\n"
        f"Temperature: {weather['temperature']}°C\n"
        f"Humidity: {weather['humidity']}%\n"
        f"Wind Speed: {weather['wind_speed']} m/s\n"
        f"Rain (last hour): {weather['rain']} mm\n"
        f"Condition: {weather['condition']}\n\n"
        f"Suggest the best order of tasks and precautions I should take (like carrying umbrella, hydration, etc.)"
    )

    # Get GPT response
    answer = chat_with_gpt(prompt)
    print("\n===== AI Suggestion =====\n")
    print(answer)
main()
