import requests

def map_bbr_heating_code(code):
    heating_map = {
        "1": "district_heating",
        "2": "gas",
        "3": "electric",
        "5": "heat_pump",
        "6": "oil"
    }

    return heating_map.get(str(code), "unknown")

def lookup_address(q):

    response = requests.get(
        f"https://api.dataforsyningen.dk/adresser?q={q}"
    )

    addresses = response.json()

    if not addresses:
        return None

    return addresses[0]


def get_bbr_buildings(address_id, username, password):

    response = requests.get(
        "https://services.datafordeler.dk/BBR/BBRPublic/1/rest/bygning",
        params={
            "Husnummer": address_id,
            "status": 6,
            "username": username,
            "password": password
        }
    )

    return response.json()

def get_address_id(first_address):

    return first_address["adgangsadresse"]["id"]

def build_analysis_input(first_building):

    return {
        "energy_label": "E",
        "building_year": first_building.get("byg026Opførelsesår"),
        "heating_type": map_bbr_heating_code(
            first_building.get("byg056Varmeinstallation")
        ),
        "energy_consumption_kwh_m2": 180
    }

def get_property_number_from_grund(grund_id, username, password):

    response = requests.get(
        "https://services.datafordeler.dk/BBR/BBRPublic/1/rest/grund",
        params={
            "id": grund_id,
            "username": username,
            "password": password
        }
    )

    data = response.json()

    if not data:
        return None

    grund = data[0]

    bestemt_fast_ejendom = grund.get("bestemtFastEjendom")

    if not bestemt_fast_ejendom:
        return None

    return bestemt_fast_ejendom.get("ejendomsnummer")