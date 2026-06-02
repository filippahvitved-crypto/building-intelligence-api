import requests


def search_energy_label_bbr(bbr_number):
    response = requests.get(
        "https://emoweb.dk/EMOData/emodata.svc/SearchEnergyLabelBBR",
        params={
            "bbr": bbr_number
        }
    )

    return {
        "status_code": response.status_code,
        "text_start": response.text[:500]
    }