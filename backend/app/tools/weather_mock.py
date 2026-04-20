"""Mock weather app """

import re

from app.agent.tool_definitions import ToolDefinition, ToolScore, build_tool_score


WEATHER_FIXTURES = {
    "calgary": {"temperature_c": 10, "condition": "Sunny"},
    "london": {"temperature_c": 14, "condition": "Cloudy"},
    "new york": {"temperature_c": 19, "condition": "Sunny"},
    "tokyo": {"temperature_c": 22, "condition": "Rain showers"},
    "edmonton": {"temperature_c": 8, "condition": "Windy"},
}


def get_weather(task: str) -> dict:
    city = _extract_city(task)
    weather = WEATHER_FIXTURES.get(city.lower(), {"temperature_c": 20, "condition": "Clear"})
    output = f"{city}: {weather['temperature_c']}°C, {weather['condition']}"

    return {
        "final_output": output,
        "metadata": {
            "city": city,
            "weather": weather,
        },
    }


def _extract_city(task: str) -> str:
    lower_task = task.lower()

    direction_match = re.search(
        r"(?:north|south|east|west)\s+of\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
        lower_task,
    )
    if direction_match:
        return direction_match.group(1).strip(" ?.!").title()

    match = re.search(
        r"(?i)(?:weather|forecast|temperature)(?:\s+(?:in|for))?\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)",
        task,
    )
    if match:
        city_text = match.group(1).strip(" ?.!").lower()
        city_text = re.split(r"\b(?:and|then|plus)\b", city_text, maxsplit=1)[0].strip()
        filler_words = {"the", "its", "it", "location", "if"}
        filtered_words = [word for word in city_text.split() if word not in filler_words]
        if filtered_words:
            return " ".join(filtered_words).title()

    return "Unknown"


def score_weather_tool(task: str, clean_task: str) -> ToolScore:
    confidence = 0.0
    matches: list[str] = []
    intent_detected = False

    weather_keywords = ["weather", "forecast", "temperature"]
    if any(keyword in clean_task for keyword in weather_keywords):
        confidence += 0.7
        matches.append("matched weather keyword")
        intent_detected = True

    location_match = re.search(r"(?i)(?:weather|forecast|temperature)(?:\s+(?:in|for))?\s+[a-zA-Z\s]+", task)
    if location_match:
        confidence += 0.2
        matches.append("matched location-style weather phrase")
        intent_detected = True

    return build_tool_score("weather_mock", confidence, matches, intent_detected)


WEATHER_TOOL = ToolDefinition(
    name="weather_mock",
    handler=get_weather,
    score=score_weather_tool,
)
