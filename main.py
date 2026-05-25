#------------------------------
#1.Imports
#------------------------------
from fastapi import FastAPI
from pydantic import BaseModel
import requests
from fastapi import Header
import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

#------------------------------
#2.App
#------------------------------
app = FastAPI()

#------------------------------
#3.Input models
#------------------------------
class BuildingInput(BaseModel):
    energy_label: str
    building_year: int
    heating_type: str
    energy_consumption_kwh_m2: float


class AddressInput(BaseModel):
    address: str


class BBRInput(BaseModel):
    adgangsadresseid: str
    username: str
    password: str

#------------------------------
#4.Fake database
#------------------------------
fake_buildings = {
    "Fælledvej 12": {
        "energy_label": "F",
        "building_year": 1958,
        "heating_type": "oil",
        "energy_consumption_kwh_m2": 240
    },
    "Nørrebrogade 20": {
        "energy_label": "C",
        "building_year": 1998,
        "heating_type": "gas",
        "energy_consumption_kwh_m2": 140
    },
    "Østerbrogade 5": {
        "energy_label": "A",
        "building_year": 2020,
        "heating_type": "heat_pump",
        "energy_consumption_kwh_m2": 55
    }
}

#------------------------------
#5.Scoring functions
#------------------------------
def score_energy_label(label: str) -> int:
    scores = {
        "A": 0,
        "B": 15,
        "C": 35,
        "D": 55,
        "E": 75,
        "F": 90,
        "G": 100
    }
    return scores.get(label.upper(), 50)


def score_building_year(year: int) -> int:
    if year < 1961:
        return 100
    elif year < 1979:
        return 80
    elif year < 1998:
        return 55
    elif year < 2010:
        return 30
    else:
        return 10


def score_heating_type(heating: str) -> int:
    heating = heating.lower()

    scores = {
        "oil": 100,
        "olie": 100,
        "gas": 80,
        "district_heating": 35,
        "fjernvarme": 35,
        "heat_pump": 15,
        "varmepumpe": 15,
        "electric": 65,
        "el": 65
    }

    return scores.get(heating, 50)


def score_energy_consumption(consumption: float) -> int:
    if consumption > 250:
        return 100
    elif consumption > 180:
        return 80
    elif consumption > 120:
        return 55
    elif consumption > 70:
        return 30
    else:
        return 10

def score_location_risk(x: float, y: float) -> int:
    if y > 55.65:
        return 70
    else:
        return 40

def calculate_building_analysis(building):

    energy_label_score = score_energy_label(building["energy_label"])
    year_score = score_building_year(building["building_year"])
    heating_score = score_heating_type(building["heating_type"])
    consumption_score = score_energy_consumption(
        building["energy_consumption_kwh_m2"]
    )

    final_score = round(
        energy_label_score * 0.40 +
        year_score * 0.25 +
        heating_score * 0.20 +
        consumption_score * 0.15
    )

    if final_score >= 75:
        priority = "High"
        recommended_action = "Prioritize renovation immediately"
        target_customers = ["bank", "investor", "contractor", "municipality"]
        confidence = "high"
    elif final_score >= 45:
        priority = "Medium"
        recommended_action = "Review renovation potential"
        target_customers = ["investor", "contractor", "insurance"]
        confidence = "medium"
    else:
        priority = "Low"
        recommended_action = "No urgent renovation needed"
        target_customers = ["insurance", "property owner"]
        confidence = "medium"

    risk_flags = []

    if energy_label_score >= 75:
        risk_flags.append("Poor energy label")
    if year_score >= 80:
        risk_flags.append("Old building")
    if heating_score >= 80:
        risk_flags.append("High-risk heating type")
    if consumption_score >= 80:
        risk_flags.append("High energy consumption")

    if risk_flags:
        explanation = "Scoren er højere fordi: " + ", ".join(risk_flags) + "."
    else:
        explanation = "Bygningen har ikke tydelige tegn på akut opgraderingsbehov."

    esg_risk_score = round(
        energy_label_score * 0.45 +
        heating_score * 0.30 +
        consumption_score * 0.25
    )

    if esg_risk_score >= 75:
        esg_risk_level = "High"
    elif esg_risk_score >= 45:
        esg_risk_level = "Medium"
    else:
        esg_risk_level = "Low"

    heat_pump_score = score_heat_pump_compatibility(building)

    if heat_pump_score >= 75:
        heat_pump_recommendation = "High compatibility for heat pump"
    elif heat_pump_score >= 45:
        heat_pump_recommendation = "Medium compatibility for heat pump"
    else:
        heat_pump_recommendation = "Low compatibility for heat pump"

    roi_score = score_roi_potential(building)

    if roi_score >= 75:
        roi_level = "High ROI potential"
    elif roi_score >= 45:
        roi_level = "Medium ROI potential"
    else:
        roi_level = "Low ROI potential"

    recommended_strategy = []

    if building["heating_type"] in ["oil", "gas"]:
        recommended_strategy.append("Replace existing heating system")

    if building["energy_consumption_kwh_m2"] > 180:
        recommended_strategy.append("Improve insulation")

    if heat_pump_score >= 70:
        recommended_strategy.append("Install heat pump")

    if roi_score >= 75:
        recommended_strategy.append("Prioritize renovation for investment upside")

    executive_summary = f"""
    This building has an upgrade score of {final_score} and an ESG risk level of {esg_risk_level}.

    The analysis indicates {priority.lower()} renovation priority with {roi_level.lower()}.

    Main drivers include:
    - {", ".join(risk_flags) if risk_flags else "No major risk factors"}

    Recommended actions:
    - {", ".join(recommended_strategy)}
    """

    return {
        "upgrade_score": final_score,
        "priority": priority,
        "recommended_action": recommended_action,
        "target_customers": target_customers,
        "confidence": confidence,
        "heat_pump_compatibility_score": heat_pump_score,
        "heat_pump_recommendation": heat_pump_recommendation,
        "roi_score": roi_score,
        "roi_level": roi_level,
        "recommended_strategy": recommended_strategy,
        "executive_summary": executive_summary,
        "esg_risk_score": esg_risk_score,
        "esg_risk_level": esg_risk_level,
        "risk_flags": risk_flags,
        "explanation": explanation,
        "breakdown": {
            "energy_label_score": energy_label_score,
            "building_year_score": year_score,
            "heating_type_score": heating_score,
            "energy_consumption_score": consumption_score
        }
    }

def score_heat_pump_compatibility(building) -> int:

    score = 50

    heating_type = building["heating_type"].lower()
    building_year = building["building_year"]
    energy_consumption = building["energy_consumption_kwh_m2"]

    if heating_type in ["oil", "olie", "gas"]:
        score += 25

    if building_year >= 1998:
        score += 15
    elif building_year < 1979:
        score -= 15

    if energy_consumption < 120:
        score += 15
    elif energy_consumption > 200:
        score -= 15

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    return score

def score_roi_potential(building) -> int:

    score = 50

    energy_label = building["energy_label"].upper()
    building_year = building["building_year"]
    energy_consumption = building["energy_consumption_kwh_m2"]

    if energy_label in ["E", "F", "G"]:
        score += 25

    if building_year < 1979:
        score += 15

    if energy_consumption > 180:
        score += 20
    elif energy_consumption < 80:
        score -= 20

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    return score

def validate_api_key(api_key):

    valid_keys = [
        os.getenv("API_KEY")
    ]

    return api_key in valid_keys

#------------------------------
#6.Helper functions
#------------------------------



#------------------------------
#7.Endpoints
#------------------------------
@app.post("/upgrade-score")
def calculate_upgrade_score(building: BuildingInput):
    energy_label_score = score_energy_label(building.energy_label)
    year_score = score_building_year(building.building_year)
    heating_score = score_heating_type(building.heating_type)
    consumption_score = score_energy_consumption(building.energy_consumption_kwh_m2)

    final_score = round(
        energy_label_score * 0.40 +
        year_score * 0.25 +
        heating_score * 0.20 +
        consumption_score * 0.15
    )

    if final_score >= 75:
        priority = "High"
    elif final_score >= 45:
        priority = "Medium"
    else:
        priority = "Low"

    if final_score >= 75:
        recommended_action = "Prioritize renovation immediately"
        target_customers = ["bank", "investor", "contractor", "municipality"]
        confidence = "high"
    elif final_score >= 45:
        recommended_action = "Review renovation potential"
        target_customers = ["investor", "contractor", "insurance"]
        confidence = "medium"
    else:
        recommended_action = "No urgent renovation needed"
        target_customers = ["insurance", "property owner"]
        confidence = "medium"

    risk_flags = []

    if energy_label_score >= 75:
        risk_flags.append("Poor energy label")
    if year_score >= 80:
        risk_flags.append("Old building")
    if heating_score >= 80:
        risk_flags.append("High-risk heating type")
    if consumption_score >= 80:
        risk_flags.append("High energy consumption")

    if risk_flags:
        explanation = "Scoren er højere fordi: " + ", ".join(risk_flags) + "."
    else:
        explanation = "Bygningen har ikke tydelige tegn på akut opgraderingsbehov."

    esg_risk_score = round(
        energy_label_score * 0.45 +
        heating_score * 0.30 +
        consumption_score * 0.25
    )

    if esg_risk_score >= 75:
        esg_risk_level = "High"
    elif esg_risk_score >= 45:
        esg_risk_level = "Medium"
    else:
        esg_risk_level = "Low"

    return {
        "model_version": "1.0",
        "score_type": "upgrade_priority_score",
        "upgrade_score": final_score,
        "priority": priority,
        "esg_risk_score": esg_risk_score,
        "esg_risk_level": esg_risk_level,
        "recommended_action": recommended_action,
        "target_customers": target_customers,
        "confidence": confidence,
        "explanation": explanation,
        "risk_flags": risk_flags,
        "input_summary": {
            "energy_label": building.energy_label,
            "building_year": building.building_year,
            "heating_type": building.heating_type,
            "energy_consumption_kwh_m2": building.energy_consumption_kwh_m2
        },
        "breakdown": {
            "energy_label_score": energy_label_score,
            "building_year_score": year_score,
            "heating_type_score": heating_score,
            "energy_consumption_score": consumption_score
        }
    }


@app.post("/lookup-building")
def lookup_building(data: AddressInput):
    building = fake_buildings.get(data.address)

    if not building:
        return {
            "error": "Building not found"
        }

    return building

@app.post("/analyze-building")
def analyze_building(data: AddressInput):

    building = fake_buildings.get(data.address)

    if not building:
        return {
            "error": "Building not found"
        }

    energy_label_score = score_energy_label(building["energy_label"])
    year_score = score_building_year(building["building_year"])
    heating_score = score_heating_type(building["heating_type"])
    consumption_score = score_energy_consumption(
        building["energy_consumption_kwh_m2"]
    )

    final_score = round(
        energy_label_score * 0.40 +
        year_score * 0.25 +
        heating_score * 0.20 +
        consumption_score * 0.15
    )

    if final_score >= 75:
        priority = "High"
    elif final_score >= 45:
        priority = "Medium"
    else:
        priority = "Low"

    risk_flags = []

    if energy_label_score >= 75:
        risk_flags.append("Poor energy label")

    if year_score >= 80:
        risk_flags.append("Old building")

    if heating_score >= 80:
        risk_flags.append("High-risk heating type")

    if consumption_score >= 80:
        risk_flags.append("High energy consumption")

    return {
        "address": data.address,
        "upgrade_score": final_score,
        "priority": priority,
        "risk_flags": risk_flags,
        "building_data": building
    }

@app.get("/test-api")
def test_api():
    response = requests.get("https://api.github.com")
    return response.json()

@app.get("/search-address")
def search_address(q: str):

    response = requests.get(
        f"https://api.dataforsyningen.dk/adresser?q={q}"
    )

    return response.json()

@app.get("/normalize-address")
def normalize_address(q: str):

    response = requests.get(
        f"https://api.dataforsyningen.dk/adresser?q={q}"
    )

    addresses = response.json()

    if not addresses:
        return {
            "error": "Address not found"
        }

    first_address = addresses[0]

    return {
        "input": q,
        "normalized_address": first_address["adressebetegnelse"],
        "street": first_address["adgangsadresse"]["vejstykke"]["navn"],
        "house_number": first_address["adgangsadresse"]["husnr"],
        "postal_code": first_address["adgangsadresse"]["postnummer"]["nr"],
        "city": first_address["adgangsadresse"]["postnummer"]["navn"],
        "municipality": first_address["adgangsadresse"]["kommune"]["navn"],
        "address_id": first_address["id"],
        "x": first_address["adgangsadresse"]["adgangspunkt"]["koordinater"][0],
        "y": first_address["adgangsadresse"]["adgangspunkt"]["koordinater"][1],
    }

@app.get("/analyze-real-address")
def analyze_real_address(
    q: str,
    x_api_key: str = Header(None)
):

    if not validate_api_key(x_api_key):
        return {
            "error": "Invalid API key"
        }
    
    print({
    "event": "api_request",
    "endpoint": "/analyze-real-address",
    "address_query": q,
    "api_key_used": x_api_key[:4] + "..."
    })

    if supabase:
        supabase.table("api_usage").insert({
            "endpoint": "/analyze-real-address",
            "address_query": q,
            "api_key_prefix": x_api_key[:4]
        }).execute()

    response = requests.get(
        f"https://api.dataforsyningen.dk/adresser?q={q}"
    )

    addresses = response.json()

    if not addresses:
        return {
            "error": "Address not found"
        }

    first_address = addresses[0]

    x = first_address["adgangsadresse"]["adgangspunkt"]["koordinater"][0]
    y = first_address["adgangsadresse"]["adgangspunkt"]["koordinater"][1]

    location_risk_score = score_location_risk(x, y)

    building = {
        "energy_label": "E",
        "building_year": 1970,
        "heating_type": "gas",
        "energy_consumption_kwh_m2": 180
    }

    analysis = calculate_building_analysis(building)

    return {
        "input": q,
        "normalized_address": first_address["adressebetegnelse"],
        "address_id": first_address["id"],
        "x": x,
        "y": y,
        "location_risk_score": location_risk_score,
        "data_status": "Address is real, building data is temporary",
        "analysis": analysis,
        "building_data_used": building,
    }

@app.post("/test-bbr-building")
def test_bbr_building(data: BBRInput):

    response = requests.get(
        "https://services.datafordeler.dk/BBR/BBRPublic/1/REST/bygning",
        params={
            "Husnummer": data.adgangsadresseid,
            "status": 6,
            "username": data.username,
            "password": data.password
        }
    )

    return {
        "status_code": response.status_code,
        "text": response.text
    }

@app.get("/")
def root():
    return {
        "status": "online",
        "product": "Building Intelligence API",
        "version": "1.0"
    }