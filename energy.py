import requests
from requests.auth import HTTPBasicAuth


def search_energy_label_bbr(
    username,
    password,
    municipality,
    property_number,
    building
):

    url = (
        "https://emoweb.dk/emodata/emodata.svc/"
        f"SearchEnergyLabelBBR/{municipality}/{property_number}/{building}"
    )

    response = requests.get(
        url,
        auth=HTTPBasicAuth(username, password)
    )

    return response.json()


def get_latest_energy_label(search_result):

    results = search_result.get("SearchResults", [])

    if not results:
        return None

    valid_labels = [
        r for r in results
        if r.get("LabelStatus") == "VALID"
    ]

    if valid_labels:
        return valid_labels[0]

    return results[0]