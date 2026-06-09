import requests
from requests.auth import HTTPBasicAuth


def test_emo_connection(username, password):
    response = requests.get(
        "https://emoweb.dk/emodata/test/",
        auth=HTTPBasicAuth(username, password)
    )

    return {
        "status_code": response.status_code,
        "text_start": response.text[:500]
    }