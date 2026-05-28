def map_bbr_heating_code(code):
    heating_map = {
        "1": "district_heating",
        "2": "gas",
        "3": "electric",
        "5": "heat_pump",
        "6": "oil"
    }

    return heating_map.get(str(code), "unknown")