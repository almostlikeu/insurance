import json
import requests
import pandas as pd

def fetch_moradabad_hospitals():
    # List of reliable public Overpass instances to fallback if one throws 406/429
    endpoints = [
        "https://overpass.private.coffee/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass-api.de/api/interpreter"
    ]
    
    # Bounding box around Moradabad city and outer radius
    # [south, west, north, east] -> (28.75, 78.68, 28.92, 78.88)
    overpass_query = """
    [out:json][timeout:60];
    (
      node["amenity"="hospital"](28.75,78.68,28.92,78.88);
      way["amenity"="hospital"](28.75,78.68,28.92,78.88);
      relation["amenity"="hospital"](28.75,78.68,28.92,78.88);
      node["amenity"="clinic"](28.75,78.68,28.92,78.88);
      way["amenity"="clinic"](28.75,78.68,28.92,78.88);
    );
    out center;
    """
    
    # Headers to satisfy Apache / ModSecurity content negotiation
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    data = None
    for url in endpoints:
        print(f"Trying endpoint: {url}...")
        try:
            response = requests.post(url, data={'data': overpass_query}, headers=headers, timeout=40)
            if response.status_code == 200:
                data = response.json()
                print("Query succeeded!")
                break
            else:
                print(f"Server returned status {response.status_code}, trying next mirror...")
        except Exception as err:
            print(f"Connection failed ({err}), trying next mirror...")

    if not data:
        print("Could not retrieve data from any Overpass mirror.")
        return
    
    hospitals = []
    for element in data.get('elements', []):
        tags = element.get('tags', {})
        name = tags.get('name') or tags.get('name:en')
        if not name:
            continue
            
        lat = element.get('lat') or element.get('center', {}).get('lat')
        lon = element.get('lon') or element.get('center', {}).get('lon')
        
        hospitals.append({
            "name": name,
            "type": tags.get('amenity', 'hospital'),
            "phone": tags.get('phone') or tags.get('contact:phone', 'N/A'),
            "emergency": tags.get('emergency', 'N/A'),
            "street": tags.get('addr:street', ''),
            "suburb": tags.get('addr:suburb', ''),
            "latitude": lat,
            "longitude": lon,
            "source": "OpenStreetMap"
        })
        
    df = pd.DataFrame(hospitals)
    
    if df.empty:
        print("No facilities found within the bounding box coordinates.")
    else:
        df.to_csv("moradabad_osm_hospitals.csv", index=False)
        print(f"Success! Extracted {len(df)} healthcare facilities to moradabad_osm_hospitals.csv")

if __name__ == "__main__":
    fetch_moradabad_hospitals()