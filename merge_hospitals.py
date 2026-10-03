import json
import re

def normalize_name(name: str) -> str:
    """Standardizes names for consistent matching."""
    if not name:
        return ""
    name = name.lower()
    # Remove city/state noise and special punctuation
    noise = ["moradabad", "uttar pradesh", "u.p.", "u.p", "(p) ltd", "pvt ltd", "ltd"]
    for word in noise:
        name = name.replace(word, "")
    # Keep only alphanumeric characters and collapse whitespace
    name = re.sub(r'[^a-z0-9]', ' ', name)
    return " ".join(name.split())

def is_match(name1: str, name2: str) -> bool:
    """Checks if two hospital names refer to the same place."""
    n1 = normalize_name(name1)
    n2 = normalize_name(name2)
    
    if not n1 or not n2:
        return False
        
    # Exact or substring match
    if n1 == n2 or n1 in n2 or n2 in n1:
        return True
        
    # Word overlap check (e.g. "Sri Sai Super Speciality" and "Sri Sai Hospital")
    words1 = set(n1.split())
    words2 = set(n2.split())
    # Exclude common medical boilerplate words from the overlap check
    stop_words = {"hospital", "clinic", "centre", "center", "care", "nursing", "home", "and", "the"}
    sig1 = words1 - stop_words
    sig2 = words2 - stop_words
    
    if sig1 and sig2 and (sig1.issubset(sig2) or sig2.issubset(sig1)):
        return True
        
    return False

def merge_datasets():
    # 1. Load primary OpenStreetMap dataset
    try:
        with open("hospitals_clean.json", "r", encoding="utf-8") as f:
            master_list = json.load(f)
    except FileNotFoundError:
        print("Error: hospitals_clean.json not found.")
        return

    # 2. Load secondary scraped files if they exist
    scraped_files = ["star_health_moradabad.json", "practo_moradabad.json"]
    additional_entries = []

    for filename in scraped_files:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                additional_entries.extend(data)
                print(f"Loaded {len(data)} records from {filename}")
        except FileNotFoundError:
            print(f"Note: {filename} not found, skipping.")

    merged_count = 0
    added_count = 0

    # 3. Enrich existing entries or add new ones
    for item in additional_entries:
        target_name = item.get("name", "").strip()
        if not target_name:
            continue

        matched_record = None
        for rec in master_list:
            if is_match(rec["name"], target_name):
                matched_record = rec
                break

        if matched_record:
            # Enrich missing phone number
            item_phone = item.get("phone", "N/A")
            if (matched_record.get("phone") == "N/A" or not matched_record.get("phone")) and item_phone != "N/A":
                matched_record["phone"] = item_phone
                merged_count += 1
                print(f"Updated Phone for: {matched_record['name']} -> {item_phone}")

            # Ensure facilities dictionary exists
            if "facilities" not in matched_record:
                matched_record["facilities"] = {}

            # Mark cashless if coming from insurance roster
            if item.get("cashless"):
                matched_record["facilities"]["cashless_insurance"] = True

        else:
            # New facility not present in primary dataset: append it
            new_id = f"custom_{len(master_list) + 1}"
            new_record = {
                "id": new_id,
                "name": target_name,
                "category": item.get("category", "hospital"),
                "address": item.get("address", "Moradabad, Uttar Pradesh"),
                "locality": item.get("locality", "Moradabad"),
                "pincode": item.get("pincode", "244001"),
                "latitude": item.get("latitude", 28.8386),  # Default city center coordinates
                "longitude": item.get("longitude", 78.7733),
                "phone": item.get("phone", "N/A"),
                "facilities": {
                    "emergency_24x7": item.get("category") == "hospital",
                    "icu": False,
                    "blood_bank": False,
                    "ayushman_bharat": False,
                    "cashless_insurance": item.get("cashless", False)
                }
            }
            master_list.append(new_record)
            added_count += 1
            print(f"Added new facility: {target_name}")

    # 4. Save merged result
    with open("hospitals_clean.json", "w", encoding="utf-8") as f:
        json.dump(master_list, f, indent=2, ensure_ascii=False)

    print("\n--- Summary ---")
    print(f"Updated {merged_count} existing hospital contacts.")
    print(f"Appended {added_count} brand new facilities.")
    print(f"Total entries in hospitals_clean.json: {len(master_list)}")

if __name__ == "__main__":
    merge_datasets()