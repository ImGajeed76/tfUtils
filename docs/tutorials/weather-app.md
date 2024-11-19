# Building a Weather App Interface: From Basics to Advanced

## Introduction

Now that you understand the basics of TF Utils interfaces, let's build something more exciting - a weather app! We'll
start simple and gradually add features, explaining each new concept as we go.

## Prerequisites

- [Installation Guide](../development/getting-started.md) completed
- [Creating Your First Interface](../tutorials/first-interface.md) completed
- PyCharm installed (completed in the installation guide)
- Project opened in PyCharm (completed in the installation guide)
- Poetry environment set up (completed in the installation guide)
- Basic Python knowledge
- Internet connection (for API calls)

## Part 1: Starting Simple

Let's begin with a basic version that just prints weather data for a hardcoded city:

```python
from textual.containers import Container
from src.lib.interface import interface
from src.lib.utils import console


@interface("Basic Weather")
async def check_weather(container: Container):
    """Display weather for London (hardcoded version)"""
    await console.print(container, "[blue]Weather in London:[/blue]")
    await console.print(container, "Temperature: 20°C")
    await console.print(container, "Conditions: Sunny")
```

Run this first to make sure everything works. You should see:

- A "Basic Weather" option in the menu
- Static weather information when selected

## Part 2: Adding User Input

Now let's allow users to choose the city:

```python
from textual.containers import Container
from src.lib.interface import interface
from src.lib.console import ask_input
from src.lib.utils import console


@interface("Weather Checker")
async def check_weather(container: Container):
    """Get weather information for any city."""

    # Get city name from user
    city = await ask_input(
        container,
        "Enter city name",
        "e.g. London, Paris, Tokyo"
    )

    await console.print(container, f"[blue]Weather in {city}:[/blue]")
    await console.print(container, "Temperature: 20°C")  # Still hardcoded!
    await console.print(container, "Conditions: Sunny")
```

This version:

- Asks for a city name
- Still uses hardcoded weather data (we'll fix that next!)

## Part 3: Adding API Integration

Now comes the exciting part - getting real weather data! First, we need to add the required imports:

```python
from textual.containers import Container
import aiohttp  # For making API calls
from src.lib.interface import interface
from src.lib.console import ask_input
from src.lib.utils import console
```

### Step 1: Create the Weather API Function

Let's create a function to fetch weather data:

```python
async def async_get_weather(city_name: str) -> dict:
    """Fetch weather data for a given city."""
    try:
        async with aiohttp.ClientSession() as session:
            # First, get city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }

            async with session.get(geo_url, params=geo_params) as geo_response:
                geo_data = await geo_response.json()

                if not geo_data.get("results"):
                    return {"error": "City not found"}

                location = geo_data["results"][0]
                lat = location["latitude"]
                lon = location["longitude"]

            # Then, get weather data using coordinates
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m"],
                "timezone": "auto"
            }

            async with session.get(weather_url, params=weather_params) as weather_response:
                weather_data = await weather_response.json()

                return {
                    "city": location["name"],
                    "country": location.get("country", "Unknown"),
                    "temperature": weather_data["current"]["temperature_2m"],
                    "humidity": weather_data["current"]["relative_humidity_2m"]
                }

    except Exception as e:
        return {"error": str(e)}
```

### Step 2: Update the Interface to Use Real Data

Now let's use our new function:

```python
@interface("Live Weather")
async def check_weather(container: Container):
    """Get real-time weather information for any city."""

    # Get city name from user
    city = await ask_input(
        container,
        "Enter city name",
        "e.g. London, Paris, Tokyo"
    )

    # Show loading message
    await console.print(container, "[blue]Fetching weather data...[/blue]")

    # Get real weather data
    weather = await async_get_weather(city)

    if "error" in weather:
        await console.print(container, f"[red]Error: {weather['error']}[/red]")
        return

    # Display weather information
    await console.print(container, "\n" + "─" * 40)
    await console.print(container, f"""
Weather for {weather['city']}, {weather['country']}
────────────────────────
Temperature: {weather['temperature']}°C
Humidity: {weather['humidity']}%
    """.strip())
    await console.print(container, "─" * 40)
```

## Part 4: Adding Weather Conditions and Emojis

Let's make it more visually appealing by adding weather conditions and emojis:

```python
# In async_get_weather, update weather_params to include weather_code:
weather_params = {
    "latitude": lat,
    "longitude": lon,
    "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
    "timezone": "auto"
}

# Add weather code mapping
weather_codes = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    61: ("Slight rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    95: ("Thunderstorm", "⛈️")
}

# Get weather info in the function
weather_info = weather_codes.get(
    weather_data["current"]["weather_code"],
    ("Unknown", "❓")
)
```

Then update the return value to include the new information:

```python
return {
    "city": location["name"],
    "country": location.get("country", "Unknown"),
    "temperature": weather_data["current"]["temperature_2m"],
    "humidity": weather_data["current"]["relative_humidity_2m"],
    "conditions": weather_info[0],
    "emoji": weather_info[1]
}
```

It should now look something like this:

```python
async def async_get_weather(city_name: str) -> dict:
    """Fetch weather data for a given city."""
    try:
        async with aiohttp.ClientSession() as session:
            # First, get city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }

            async with session.get(geo_url, params=geo_params) as geo_response:
                geo_data = await geo_response.json()

                if not geo_data.get("results"):
                    return {"error": "City not found"}

                location = geo_data["results"][0]
                lat = location["latitude"]
                lon = location["longitude"]

            # Then, get weather data using coordinates
            weather_url = "https://api.open-meteo.com/v1/forecast"

            # In async_get_weather, update weather_params to include weather_code:
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
                "timezone": "auto"
            }

            # Add weather code mapping
            weather_codes = {
                0: ("Clear sky", "☀️"),
                1: ("Mainly clear", "🌤️"),
                2: ("Partly cloudy", "⛅"),
                3: ("Overcast", "☁️"),
                45: ("Foggy", "🌫️"),
                51: ("Light drizzle", "🌦️"),
                61: ("Slight rain", "🌧️"),
                71: ("Slight snow", "🌨️"),
                95: ("Thunderstorm", "⛈️")
            }

            async with session.get(weather_url, params=weather_params) as weather_response:
                weather_data = await weather_response.json()

                weather_info = weather_codes.get(
                    weather_data["current"]["weather_code"],
                    ("Unknown", "❓")
                )

                return {
                    "city": location["name"],
                    "country": location.get("country", "Unknown"),
                    "temperature": weather_data["current"]["temperature_2m"],
                    "humidity": weather_data["current"]["relative_humidity_2m"],
                    "conditions": weather_info[0],
                    "emoji": weather_info[1]
                }

    except Exception as e:
        return {"error": str(e)}
```

Finally, update the display:

```python
await console.print(container, f"""
{weather['emoji']} Weather for {weather['city']}, {weather['country']}
────────────────────────
Temperature: {weather['temperature']}°C
Conditions: {weather['conditions']}
Humidity: {weather['humidity']}%
    """.strip())
```

## The Final Weather App

You now have a fully functional weather app that fetches real-time weather data for any city! Here's the complete code:

```python
import aiohttp  # For making API calls
from textual.containers import Container

from src.lib.console import ask_input
from src.lib.interface import interface
from src.lib.utils import console


async def async_get_weather(city_name: str) -> dict:
    """Fetch weather data for a given city."""
    try:
        async with aiohttp.ClientSession() as session:
            # First, get city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": city_name,
                "count": 1,
                "language": "en",
                "format": "json",
            }

            async with session.get(geo_url, params=geo_params) as geo_response:
                geo_data = await geo_response.json()

                if not geo_data.get("results"):
                    return {"error": "City not found"}

                location = geo_data["results"][0]
                lat = location["latitude"]
                lon = location["longitude"]

            # Then, get weather data using coordinates
            weather_url = "https://api.open-meteo.com/v1/forecast"

            # In async_get_weather, update weather_params to include weather_code:
            weather_params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
                "timezone": "auto",
            }

            # Add weather code mapping
            weather_codes = {
                0: ("Clear sky", "☀️"),
                1: ("Mainly clear", "🌤️"),
                2: ("Partly cloudy", "⛅"),
                3: ("Overcast", "☁️"),
                45: ("Foggy", "🌫️"),
                51: ("Light drizzle", "🌦️"),
                61: ("Slight rain", "🌧️"),
                71: ("Slight snow", "🌨️"),
                95: ("Thunderstorm", "⛈️"),
            }

            async with session.get(
                weather_url, params=weather_params
            ) as weather_response:
                weather_data = await weather_response.json()

                weather_info = weather_codes.get(
                    weather_data["current"]["weather_code"], ("Unknown", "❓")
                )

                return {
                    "city": location["name"],
                    "country": location.get("country", "Unknown"),
                    "temperature": weather_data["current"]["temperature_2m"],
                    "humidity": weather_data["current"]["relative_humidity_2m"],
                    "conditions": weather_info[0],
                    "emoji": weather_info[1],
                }

    except Exception as e:
        return {"error": str(e)}


@interface("Live Weather")
async def check_weather(container: Container):
    """Get real-time weather information for any city."""

    # Get city name from user
    city = await ask_input(container, "Enter city name", "e.g. London, Paris, Tokyo")

    # Show loading message
    await console.print(container, "[blue]Fetching weather data...[/blue]")

    # Get real weather data
    weather = await async_get_weather(city)

    if "error" in weather:
        await console.print(container, f"[red]Error: {weather['error']}[/red]")
        return

    # Display weather information
    await console.print(container, "\n" + "─" * 40)
    await console.print(
        container,
        f"""
    {weather['emoji']} Weather for {weather['city']}, {weather['country']}
    ────────────────────────
    Temperature: {weather['temperature']}°C
    Conditions: {weather['conditions']}
    Humidity: {weather['humidity']}%
        """.strip(),
    )
    await console.print(container, "─" * 40)

```

## Understanding the Code

### Key Concepts Used:

1. **Async/Await**: For non-blocking API calls
    - `async with` for managing connections
    - `await` for waiting on responses

2. **Error Handling**:
    - Try/except blocks
    - Error message returns
    - User input validation

3. **API Integration**:
    - Multiple API endpoints
    - Parameter handling
    - Response processing

4. **UI Enhancements**:
    - Loading messages
    - Error formatting
    - Pretty printing with borders
    - Emoji support

## Practice Exercises

Try these enhancements:

1. **Add Wind Speed**:
    - Update `weather_params` to include "wind_speed_10m"
    - Add it to the display

2. **Temperature Units**:
    - Add a second input for preferred unit (C/F)
    - Convert temperatures accordingly

3. **Location Memory**:
    - Store the last searched city
    - Add an option to quickly check it again

## Troubleshooting Tips

1. **API Issues**:
    - Check internet connection
    - Verify city spelling
    - Handle API rate limits

2. **Display Issues**:
    - Run in PowerShell for emoji support
    - Check for proper string formatting
    - Verify border characters display correctly

## Next Steps

Now that you have a working weather app, try:

1. Adding extended forecasts
2. Saving favorite cities
3. Adding weather alerts
4. Including sunrise/sunset times
5. Adding historical weather data

Remember: The Open-Meteo API has many more features you can explore. Check
their [documentation](https://open-meteo.com/en/docs) for more possibilities!
