import json
import re

def clean_moradabad_geojson(input_file="export.geojson", output_file="hospitals_clean.json"):
    with open(input_file, "r", encoding="utf-8") as f:
        geo_data = json.load(f)

    cleaned_records = []
    
    # Optional seed dictionary for critical emergency numbers
    emergency_contacts = {
        "Cosmos Hospital": "0591-2555500",
        "Sri Sai Super Speciality Hospital": "0591-2479800",
        "Teerthankar Mahaveer Hospital and Research Centre": "0591-2360500",
        "District Hospital, Moradabad": "0591-2410670",
    }

    for feature in geo_data.get("features", []):
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [None, None])
        
        raw_name = props.get("name", "").strip()
        if not raw_name:
            continue
            
        # Clean typos and trailing commas
        clean_name = raw_name.replace("Morabad", "Moradabad").rstrip(",- ")
        
        # Determine locality from addr:full
        full_address = props.get("addr:full", "Moradabad")
        locality_match = re.search(r"(Civil Lines|Lajpat Nagar|Gandhi Nagar|Kanth Road|Delhi Road|Ashiyana|Ram Ganga Vihar|Prem Nagar)", full_address, re.IGNORECASE)
        locality = locality_match.group(0) if locality_match else "Moradabad"

        record = {
            "id": props.get("@id", "").replace("/", "_"),
            "name": clean_name,
            "category": props.get("amenity", "hospital"),
            "address": full_address,
            "locality": locality,
            "pincode": props.get("addr:postcode", "244001"),
            "latitude": coords[1],
            "longitude": coords[0],
            "phone": emergency_contacts.get(clean_name, props.get("phone", "N/A")),
            # Default schema for your UI matrix
            "facilities": {
                "emergency_24x7": True if "hospital" in props.get("amenity", "") else False,
                "icu": True if any(k in clean_name.lower() for k in ["superspeciality", "research", "heart", "trauma"]) else False,
                "blood_bank": False,
                "ayushman_bharat": True if "District" in clean_name else False
            }
        }
        cleaned_records.append(record)

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(cleaned_records, out, indent=2, ensure_ascii=False)

    print(f"Processed {len(cleaned_records)} records saved to {output_file}")

if __name__ == "__main__":
    clean_moradabad_geojson()