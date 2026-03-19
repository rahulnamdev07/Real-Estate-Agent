#from mcp.server.fastmcp import FastMCP

# Create MCP server
#mcp = FastMCP("DemoServer", log_level="ERROR")

# Define a tool
#@mcp.tool()
#def add(a: int, b: int) -> int:
#    """Add two numbers"""
#    return a + b

#if __name__ == "__main__":
#    mcp.run()
import os
import asyncio
import httpx
from geopy.geocoders import Nominatim
from mcp.server.fastmcp import FastMCP
import googlemaps
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import ee
ee.Authenticate()
ee.Initialize(project='real-estate-agent-489610')
print(ee.String('Hello from Earth Engine!').getInfo())

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
#gmaps = googlemaps.Client(key=api_key)

mcp = FastMCP("real-estate-agent", log_level="ERROR")

geolocator = Nominatim(user_agent="real_estate_mcp")

# -----------------------------
# TOOL 1: Get Latitude Longitude
# -----------------------------
@mcp.tool()
async def get_coordinates(place: str, city: str):
    """
    Takes place name and city and returns latitude and longitude.
    """
    query = f"{place}, {city}, India"
    location = geolocator.geocode(query)

    if not location:
        return "Location not found"

    return f"{location.latitude},{location.longitude}"


# -----------------------------
# TOOL 2: Area Statistics
# -----------------------------
@mcp.tool()
async def get_area_stats(lat: float, lon: float, radius_km: int = 5):
    """
    Returns stats about shops, malls, hospitals and famous place names
    """

    try:
        import httpx

        radius_m = radius_km * 1000

        query = f"""
        [out:json];
        (
          node["shop"](around:{radius_m},{lat},{lon});
          node["shop"="mall"](around:{radius_m},{lat},{lon});
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
        );
        out;
        """

        url = "https://overpass.kumi.systems/api/interpreter"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, data=query)

        data = response.json()

        shops = 0
        malls = 0
        hospitals = 0

        famous_malls = set()
        famous_shops = set()
        famous_hospitals = set()

        for el in data.get("elements", []):
            tags = el.get("tags", {})

            # Shops
            if "shop" in tags:
                shops += 1

                if tags.get("brand"):
                    famous_shops.add(tags["brand"])
                elif tags.get("name"):
                    famous_shops.add(tags["name"])

            # Malls
            if tags.get("shop") == "mall":
                malls += 1
                if tags.get("name"):
                    famous_malls.add(tags["name"])

            # Hospitals
            if tags.get("amenity") == "hospital":
                hospitals += 1
                if tags.get("name"):
                    famous_hospitals.add(tags["name"])

        famous_malls_list = list(famous_malls)[:5]
        famous_shops_list = list(famous_shops)[:5]
        famous_hospitals_list = list(famous_hospitals)[:5]

        result = (
            f"shops:{shops}, "
            f"malls:{malls}, "
            f"hospitals:{hospitals}, "
            f"famous_malls:{', '.join(famous_malls_list)}, "
            f"famous_shops:{', '.join(famous_shops_list)}, "
            f"famous_hospitals:{', '.join(famous_hospitals_list)}"
        )

        return result

    except Exception as e:
        print(f"Error in get_area_stats: {str(e)}")
        return f"Tool Error: {str(e)}"

@mcp.tool()
def get_neighborhood_insights(latitude: float, longitude: float, radius_m: float = 5000) -> str:
    """
    Uses Places API (New) to find insights for a real estate agent.
    """
    # The 'New' API uses a FieldMask to save you money (you only pay for what you ask for)
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.rating,places.types"
    }
    
    # We'll search for multiple types in one go (New API capability!)
    payload = {
        "includedTypes": ["school", "shopping_mall", "hospital", "supermarket"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_m
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if "places" not in data:
        return f"No significant landmarks found or API error: {data.get('error', {}).get('message', 'Unknown')}"

    # Sort results into categories for the agent
    categories = {"Schools": [], "Malls": [], "Hospitals": [], "Shops": []}
    
    for place in data["places"]:
        name = place.get("displayName", {}).get("text", "Unknown")
        p_types = place.get("types", [])
        rating = place.get("rating", "N/A")
        
        entry = f"{name} ({rating}⭐)"
        
        if "school" in p_types: categories["Schools"].append(entry)
        elif "shopping_mall" in p_types: categories["Malls"].append(entry)
        elif "hospital" in p_types: categories["Hospitals"].append(entry)
        elif "supermarket" in p_types: categories["Shops"].append(entry)

    report = [
        f"### Neighborhood Report ({radius_m/1000}km Radius)",
        f"**Schools:** {', '.join(categories['Schools'][:3]) or 'None found'}",
        f"**Malls:** {', '.join(categories['Malls'][:3]) or 'None found'}",
        f"**Hospitals:** {', '.join(categories['Hospitals'][:3]) or 'None found'}",
        f"**Shops:** {len(categories['Shops'])} found in vicinity"
    ]
    
    return "\n".join(report)

@mcp.tool()
def get_solar_potential(latitude: float, longitude: float) -> str:
    """Returns solar potential and rooftop insights for a specific coordinate."""
    url = f"https://solar.googleapis.com/v1/buildingInsights:findClosest?location.latitude={latitude}&location.longitude={longitude}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if "solarPotential" not in data:
        return "No solar data available for this specific roof."
        
    sp = data["solarPotential"]
    return (f"Solar Insight: This roof has {sp.get('maxSunshineHoursPerYear', 0)} max sunshine hours/year "
            f"and space for {sp.get('maxArrayPanels', 0)} solar panels.")


@mcp.tool()
def get_area_density(latitude: float, longitude: float, radius_m: int = 3000) -> str:
    """Returns counts of specific amenities to show commercial maturity."""
    url = "https://areainsights.googleapis.com/v1:computeInsights"
    headers = {"X-Goog-Api-Key": API_KEY, "Content-Type": "application/json"}
    
    # Looking for 'lifestyle' indicators
    payload = {
        "insights": ["INSIGHT_COUNT"],
        "filter": {
            "location_filter": {"circle": {"lat_lng": {"latitude": latitude, "longitude": longitude}, "radius": radius_m}},
            "type_filter": {"included_types": ["cafe", "fitness_center", "boutique_store"]}
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    count = response.json().get("count", 0)
    return f"Commercial Density: There are {count} premium lifestyle venues within {radius_m}m."


@mcp.tool()
def get_historical_development_images(latitude: float, longitude: float) -> str:
    """
    Returns thumbnail URLs for satellite imagery from 2023, 2024, and 2025
    to show physical development of a plot.
    """
    point = ee.Geometry.Point([longitude, latitude])
    region = point.buffer(500).bounds() # 500 meter area
    
    years = [2023, 2024, 2025]
    image_links = []

    for year in years:
        # Fetch Sentinel-2 Cloud-Free Composite for the year
        collection = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                      .filterBounds(region)
                      .filterDate(f'{year}-01-01', f'{year}-12-31')
                      .sort('CLOUDY_PIXEL_PERCENTAGE')
                      .first())
        
        # Define visualization parameters (True Color)
        vis_params = {
            'min': 0, 'max': 3000, 
            'bands': ['B4', 'B3', 'B2'], # Red, Green, Blue
            'dimensions': 512,
            'format': 'jpg'
        }
        
        try:
            url = collection.getThumbURL(vis_params)
            image_links.append(f"**{year} Snapshot:** {url}")
        except Exception:
            image_links.append(f"**{year} Snapshot:** Imagery unavailable for this period.")

    return "### Area Evolution (3-Year Satellite History)\n\n" + "\n\n".join(image_links)

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    mcp.run()


# 23.2335177,77.4325731