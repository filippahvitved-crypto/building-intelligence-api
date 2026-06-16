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

def get_energy_label_details(
    username,
    password,
    entity_identifier
):

    url = (
        "https://emoweb.dk/emodata/EMOData.svc/"
        f"FetchEnergyLabelDetails/{entity_identifier}"
    )

    response = requests.get(
        url,
        auth=HTTPBasicAuth(username, password)
    )

    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def get_energy_consumption_per_m2(
    energy_details,
    building_area
):

    try:
        total_consumption = float(
            energy_details["ProposalCalculation"]["CalculatedEnergyConsumption"]
        )

        area = float(building_area)

        if area <= 0:
            return None

        return round(total_consumption / area, 1)

    except Exception:
        return None

def get_recommended_energy_proposals(energy_details):

    try:
        proposals = energy_details["ProposalOverview"]["RecommendedProposals"]

        return [
            {
                "title": proposal.get("Shorttext"),
                "investment": proposal.get("Investment"),
                "money_saving": proposal.get("MoneySaving"),
                "renovation_time": proposal.get("RenovationTime"),
                "category": proposal.get("Category")
            }
            for proposal in proposals
        ]

    except Exception:
        return []