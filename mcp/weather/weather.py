from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
# Initiaise FastMCP Server
mcp = FastMCP()

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any]:
    """Helper function to make requests to the NWS API."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            return None
        

def format_alert( feature: dict[str, Any]) -> str:
    """Format a single alert feature into a readable string."""
    alert_properties = feature["properties"]
    return f"""
Event: {alert_properties.get("event", "Unknown")}\n
Area: {alert_properties.get("areaDesc", "Unknown")}\n
Severity: {alert_properties.get("severity", "Unknown")}\n
Description: {alert_properties.get("description", "No description available")}\n
Instructions: {alert_properties.get("instruction", "No specific instructions provided")}\n
"""

def format_forecast( period: dict[str, Any]) -> str:
    """Format a single forecast period into a readable string."""
    # Limit the number of forecast periods to avoid overwhelming the output
    periods = period["properties"]["periods"]
    forecast_properties = periods[:10]
    forecasts = []
    for forecast in forecast_properties:
        forecasts.append(f"""
Name: {forecast.get("name", "Unknown")}\n
Temperature: {forecast.get("temperature", "Unknown")} {forecast.get("temperatureUnit", "")}\n
Wind: {forecast.get("windSpeed", "Unknown")} {forecast.get("windDirection", "Unknown")}\n
    """)
    return "\n===---===\n".join(forecasts)


@mcp.tool()
async def get_alerts(city: str) -> str:
    """ Get Weather alert for a US City

    Arg:
        city (str): The city for which to fetch alerts.
    """
    alert_url = f"{NWS_API_BASE}/alerts/active?area={city}"
    data  = await make_nws_request(alert_url)
    if not data or "features" not in data:
        return f"No alerts found for {city}."
    if not data["features"]:
        return f"No active alerts for {city}."
    city_alert = [format_alert(feature) for feature in data["features"]]
    return "\n===\n".join(city_alert)


@mcp.tool()
async def get_forecast( latitude: float, longitude: float) -> str:
    """Get forecast for a given location with latitude and longitude.
    
    Arg:
        latitude (float): The latitude of the location for which to fetch the forecast.
        longitude (float): The longitude of the location for which to fetch the forecast.
    """
    try:
        location_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
        location_data_forecast_url_response = await make_nws_request(location_url)
        if not location_data_forecast_url_response or "properties" not in location_data_forecast_url_response:
            return "Unable to retrieve location information."
        if not location_data_forecast_url_response["properties"].get("forecast"):
            return "No forecast information available for this location."
        location_data_url = location_data_forecast_url_response["properties"]["forecast"]
        logger.info(f"**** Location data URL: {location_data_url}")
        location_data_response = await make_nws_request(location_data_url)
        logger.info(f"**** Location data response: {location_data_response}")
        if not location_data_response or "properties" not in location_data_response:
            return "Unable to retrieve forecast information."
        if not location_data_response["properties"].get("periods"):
            return "No forecast periods available for this location."   
        forecasts_data = format_forecast(location_data_response)
        return forecasts_data
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        return f"An error occurred while fetching the forecast with error : {str(e)}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()


"""
Add this config in claude_desktop_config.json in "mcpServers" section
to enable the tool in Claude Desktop:

    "local_weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/<path_to_project>/mcp/weather",
        "run",
        "weather.py"
      ]
    }   

Use this follwoing prompt to test the tool in Claude Desktop:

1. What’s the weather forecast in Texas ? Use the local_weather tool. Use TX as 
    code for Texas.  and also provide its lattitude and longitude

2. What’s the weather in Texas ? Use the local_weather tool. Use TX as code for Texas.
"""














































































































