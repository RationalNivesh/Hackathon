import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox
import google.generativeai as genai

# ===================== CONFIGURATION =====================
weather_api_key = "Your openweather API Key"
gemini_api_key = "Your Gemini API Key"  # Replace with your Gemini API key
geodb_api_key = "Your geodbapi key"    # Get from https://rapidapi.com/wirefreethought/api/geodb-cities/

genai.configure(api_key=gemini_api_key)

# Gemini model config for deterministic answers + reasoning
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    generation_config={
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 256,
    }
)

last_weather = None
last_city_info = None

# ===================== FUNCTIONS =====================
def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={weather_api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()

    description = data["weather"][0]["description"]
    temp = round(data["main"]["temp"], 1)
    feels_like = round(data["main"]["feels_like"], 1)
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = round(data["wind"]["speed"] * 3.6, 2)
    cloud = data["clouds"]["all"]

    return (
        f"Weather in {city_name}: {description}, Temp: {temp}°C (feels like {feels_like}°C), "
        f"Humidity: {humidity}%, Pressure: {pressure} hPa, Wind: {wind_speed} km/h, Clouds: {cloud}%."
    )


def get_city_info(city_name):
    """Fetch city info from GeoDB Cities API."""
    headers = {
        "X-RapidAPI-Key": geodb_api_key,
        "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
    }
    url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={city_name}&limit=1"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    if data["data"]:
        city = data["data"][0]
        info = (
            f"City: {city.get('city')}, Country: {city.get('country')}, "
            f"Region: {city.get('region')}, Population: {city.get('population')}, "
            f"Elevation: {city.get('elevationMeters')}m, Timezone: {city.get('timezone')}"
        )
        return info
    return None


def fetch_weather_and_city():
    global last_weather, last_city_info
    city = city_entry.get().strip()
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    # Fetch weather
    weather_text = get_weather(city)
    if not weather_text:
        messagebox.showerror("Error", "Could not fetch weather data. Check city name or API key.")
        return
    last_weather = weather_text
    output_box.insert(tk.END, weather_text + "\n\n")

    # Fetch city info
    city_info = get_city_info(city)
    if city_info:
        last_city_info = city_info
        output_box.insert(tk.END, f"City Info:\n{city_info}\n\n")
    else:
        last_city_info = None
        output_box.insert(tk.END, "Could not fetch city info.\n\n")

    output_box.see(tk.END)


def ask_gemini():
    question = ai_entry.get().strip()
    if not question:
        messagebox.showwarning("Input Error", "Please enter a question.")
        return

    if not last_weather:
        messagebox.showwarning("No Data", "Please fetch weather first.")
        return

    try:
        prompt = (
            "You are a precise assistant. Always provide a single, definitive answer and explain briefly your reasoning. "
            f"Weather report:\n{last_weather}\n"
        )
        if last_city_info:
            prompt += f"City info:\n{last_city_info}\n"
        prompt += f"\nQuestion: {question}\nAnswer with reasoning:"

        response = model.generate_content(prompt)
        output_box.insert(tk.END, f"Q: {question}\nA: {response.text}\n\n")
        output_box.see(tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Gemini failed: {e}")


def suggest_foods():
    if not last_weather:
        messagebox.showwarning("No Data", "Please fetch weather first.")
        return

    try:
        prompt = (
            "You are a culinary assistant. Based on the following weather (and city info if available), "
            "recommend 3-5 foods or drinks ideal to prepare. Give brief reasoning for each choice.\n\n"
            f"Weather report:\n{last_weather}\n"
        )
        if last_city_info:
            prompt += f"City info:\n{last_city_info}\n"
        prompt += "\nFood suggestions:"

        response = model.generate_content(prompt)
        output_box.insert(tk.END, f"Food suggestions:\n{response.text}\n\n")
        output_box.see(tk.END)
    except Exception as e:
        messagebox.showerror("Error", f"Gemini failed: {e}")


# ===================== GUI =====================
root = tk.Tk()
root.title("Weather + Gemini + Food + City Info Assistant")

# City input
tk.Label(root, text="City:").pack()
city_entry = tk.Entry(root, width=40)
city_entry.pack()
tk.Button(root, text="Get Weather & City Info", command=fetch_weather_and_city).pack(pady=2)

# AI Question input
tk.Label(root, text="Ask Gemini about the weather or city:").pack()
ai_entry = tk.Entry(root, width=40)
ai_entry.pack()
tk.Button(root, text="Ask AI", command=ask_gemini).pack(pady=2)

# Food suggestion button
tk.Button(root, text="Suggest Foods Based on Weather", command=suggest_foods).pack(pady=5)

# Output box
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=30)
output_box.pack(padx=10, pady=10)

root.mainloop()
