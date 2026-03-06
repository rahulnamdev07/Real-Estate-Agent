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

import asyncio
import httpx
from geopy.geocoders import Nominatim
from mcp.server.fastmcp import FastMCP

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

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    mcp.run()