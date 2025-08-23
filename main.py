import requests
from datetime import datetime
import openai # Ensure this is installed: pip install openai

# ========== CONFIGURATION ==========
# IMPORTANT: Replace these with your actual API keys.
# Get your OpenWeatherMap API key from https://openweathermap.org/api
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"
# Get your OpenAI API key from https://platform.openai.com
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize the OpenAI client
# Ensure the openai library is installed (pip install openai)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ========== WEATHER FETCHING FUNCTION ==========
def get_weather(city="Delhi"):
    """
    Fetches current weather data for a given city using OpenWeatherMap API.
    Returns weather data in metric units (Celsius, m/s for wind speed).
    Includes basic error handling for API calls.
    """
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        print("Error: OpenWeatherMap API key is not set. Please replace 'YOUR_OPENWEATHER_API_KEY' with your actual key.")
        return None

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        weather_data_raw = response.json()

        if weather_data_raw.get('cod') == 200:
            weather = {
                "city": city,
                "temperature": weather_data_raw["main"]["temp"],
                "feels_like": weather_data_raw["main"]["feels_like"],
                "pressure": weather_data_raw["main"]["pressure"],
                "humidity": weather_data_raw["main"]["humidity"],
                "wind_speed": weather_data_raw["wind"]["speed"] * 3.6, # Convert m/s to km/hr
                "cloudiness": weather_data_raw["clouds"]["all"],
                "description": weather_data_raw["weather"][0]["description"],
                # Check if 'rain' key exists, and then check for '1h' (rain in last hour)
                "will_rain": "Yes" if "rain" in weather_data_raw else "No"
            }
            return weather
        else:
            print(f"Error fetching weather for {city}: {weather_data_raw.get('message', 'Unknown error')}")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Could not get weather for {city}. Please check the city name.")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err} - Check your internet connection.")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err} - The request took too long.")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
        return None
    except Exception as e:
        print(f"An error occurred while processing weather data: {e}")
        return None

# ========== GPT CHAT FUNCTION ==========
def chat_with_gpt(prompt):
    """
    Sends a prompt to the OpenAI GPT model and returns the response.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        print("Error: OpenAI API key is not set. Please replace 'YOUR_OPENAI_API_KEY' with your actual key.")
        return "I cannot provide suggestions without a valid OpenAI API key."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using the specified model
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except openai.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
        return "I'm having trouble connecting to the AI. Please check your internet connection and try again."
    except openai.RateLimitError as e:
        print(f"OpenAI API rate limit exceeded: {e}")
        return "I'm experiencing high traffic. Please try again in a moment."
    except openai.APIStatusError as e:
        print(f"OpenAI API error {e.status_code}: {e.response}")
        return "An error occurred with the AI service. Please try again later."
    except Exception as e:
        print(f"An unexpected error occurred with the AI: {e}")
        return "An unexpected error occurred while generating a response."


# ========== MAIN CHATBOT LOGIC ==========
def main():
    """
    Main function to run the chatbot, gather user input, fetch weather,
    and get suggestions from GPT.
    """
    print("🌟 Welcome to your personal daily planner chatbot! 🌟")

    # --- Get User Events ---
    num_events = -1
    while num_events < 0:
        try:
            num_events = int(input("How many events do you have planned for today? "))
            if num_events < 0:
                print("Please enter a non-negative number for events.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    events = []
    for i in range(num_events):
        event_name = input(f"Enter event {i+1} (e.g., 'Team meeting', 'Gym workout'): ")
        event_time = input(f"Enter the time for '{event_name}' (e.g., '10:00 AM', '3 PM'): ")
        events.append({"name": event_name, "time": event_time})

    # --- Get City for Weather ---
    city = input("Which city are you in today for the weather forecast? ")

    print(f"\nFetching weather for {city}...")
    weather = get_weather(city)

    if weather:
        print(f"\n--- Current Weather in {weather['city']} ---")
        print(f"🌡️ Temperature: {weather['temperature']:.1f}°C (Feels like: {weather['feels_like']:.1f}°C)")
        print(f"💧 Humidity: {weather['humidity']}%")
        print(f"💨 Wind Speed: {weather['wind_speed']:.2f} km/hr")
        print(f"☁️ Cloudiness: {weather['cloudiness']}%")
        print(f"📝 Condition: {weather['description'].capitalize()}")
        print(f"☔ Rain Expected: {weather['will_rain']}")
        print("--------------------------------------")

        # --- Prepare Prompt for GPT ---
        events_str = "\n".join([f"- {event['name']} at {event['time']}" for event in events])
        if not events_str:
            events_str = "No specific events planned."

        prompt = f"""
        I have the following events planned for today:
        {events_str}

        The current weather conditions in {weather['city']} are:
        Temperature: {weather['temperature']:.1f}°C (Feels like: {weather['feels_like']:.1f}°C)
        Pressure: {weather['pressure']} hPa
        Humidity: {weather['humidity']}%
        Wind Speed: {weather['wind_speed']:.2f} km/hr
        Cloudiness: {weather['cloudiness']}%
        Overall condition: {weather['description'].capitalize()}
        Rain expected: {weather['will_rain']}

        Please provide suggestions on the best order for these events, any necessary precautions (e.g., carrying an umbrella, staying hydrated, suitable attire), and general advice for my day based on the weather. Be encouraging and helpful!
        """
        
        print("\nSending details to AI for suggestions...")
        ai_suggestion = chat_with_gpt(prompt)
        print("\n===== 🤖 AI's Daily Suggestion =====\n")
        print(ai_suggestion)
        print("\n======================================")
    else:
        print("\nCould not get weather information. Cannot provide AI suggestions without it.")

if __name__ == "__main__":
    main()
