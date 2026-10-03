import json

def enrich_from_tpa():
    # 1. Verified Directory from TPA & Cashless Provider records
    tpa_registry = {
        "Apex Hospital": {
            "phone": "8865080178",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Cosmos Hospital": {
            "phone": "0591-2555500",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Asian Vivekananda Hospital and Research Center": {
            "phone": "0591-2551100",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Bhavya Hospital": {
            "phone": "0591-2970375",
            "cashless": True,
            "icu": False,
            "emergency_24x7": True
        },
        "C.L. Gupta Eye Institute": {
            "phone": "8937834443",
            "cashless": True,
            "icu": False,
            "emergency_24x7": True
        },
        "Brightstar Hospital": {
            "phone": "9389808062",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Crest Hospital": {
            "phone": "7088022999",
            "cashless": True,
            "icu": False,
            "emergency_24x7": True
        },
        "Sadbhawana Nursing Home": {
            "phone": "9837039830",
            "cashless": True,
            "icu": False,
            "emergency_24x7": False
        },
        "Teerthankar Mahaveer Hospital and Research Centre": {
            "phone": "0591-2360500",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Sri Sai Super Speciality Hospital": {
            "phone": "0591-2479800",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "Centre For Sight": {
            "phone": "0591-2452405",
            "cashless": True,
            "icu": False,
            "emergency_24x7": True
        },
        "District Hospital, Moradabad": {
            "phone": "0591-2410670",
            "cashless": True,
            "icu": True,
            "emergency_24x7": True
        },
        "District Female Hospital": {
            "phone": "0591-2410670",
            "cashless": True,
            "icu": False,
            "emergency_24x7": True
        }
    }

    input_file = "hospitals_clean.json"
    with open(input_file, "r", encoding="utf-8") as f:
        hospitals = json.load(f)

    updated_count = 0
    for h in hospitals:
        name = h.get("name", "").strip()
        
        # Check for direct or partial match
        matched_key = None
        for key in tpa_registry:
            if key.lower() in name.lower() or name.lower() in key.lower():
                matched_key = key
                break
        
        if matched_key:
            data = tpa_registry[matched_key]
            h["phone"] = data["phone"]
            h["facilities"]["ayushman_bharat"] = data["cashless"]
            h["facilities"]["icu"] = data["icu"]
            h["facilities"]["emergency_24x7"] = data["emergency_24x7"]
            updated_count += 1

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(hospitals, f, indent=2, ensure_ascii=False)

    print(f"Enriched {updated_count} hospitals with verified contacts and cashless status!")

if __name__ == "__main__":
    enrich_from_tpa()