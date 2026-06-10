import requests
from requests.auth import HTTPBasicAuth


def search_energy_label_bbr(username, password, municipality, property_number, building):
    url = (
        "https://emoweb.dk/emodata/emodata.svc/"
        f"SearchEnergyLabelBBR/{municipality}/{property_number}/{building}"
    )

    response = requests.get(
        url,
        auth=HTTPBasicAuth(username, password)
    )

    return {
        "status_code": response.status_code,
        "data": response.json()
    }