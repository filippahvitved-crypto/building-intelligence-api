#------------------------------
#1.Imports
#------------------------------
from fastapi import FastAPI, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os
from supabase import create_client
from scoring import *
from bbr import *
from analytics import *
from energy import *

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

class PortfolioInput(BaseModel):
    addresses: list[str]

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

def validate_api_key(api_key):

    valid_keys = [
        os.getenv("API_KEY", "test123")
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

    log_api_usage(
    supabase=supabase,
    endpoint="/analyze-address",
    address_query=q,
    normalized_address=first_address["adressebetegnelse"],
    api_key_prefix=x_api_key[:4],
    analysis=analysis,
    data_status="Building year and heating type from BBR. Energy label and consumption are temporary."
    )

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

@app.get("/")
def root():
    return {
        "status": "online",
        "product": "Building Intelligence API",
        "version": "1.0"
    }

@app.get("/debug-bbr")
def debug_bbr(username: str, password: str):
    response = requests.get(
        "https://services.datafordeler.dk/BBR/BBRPublic/1/rest/bygning",
        params={
            "status": 6,
            "username": username,
            "password": password
        }
    )

    return {
        "status_code": response.status_code,
        "text_start": response.text[:500]
    }

@app.get("/bbr-building-by-address")
def bbr_building_by_address(q: str, username: str, password: str):

    address_response = requests.get(
        f"https://api.dataforsyningen.dk/adresser?q={q}"
    )

    addresses = address_response.json()

    if not addresses:
        return {
            "error": "Address not found"
        }

    first_address = addresses[0]
    address_id = first_address["adgangsadresse"]["id"]

    bbr_response = requests.get(
        "https://services.datafordeler.dk/BBR/BBRPublic/1/rest/bygning",
        params={
            "Husnummer": address_id,
            "username": username,
            "password": password
        }
    )

    return {
        "normalized_address": first_address["adressebetegnelse"],
        "address_id": address_id,
        "status_code": bbr_response.status_code,
        "bbr_data_start": bbr_response.text[:1000]
    }

@app.get("/bbr-building-year")
def bbr_building_year(q: str, username: str, password: str):

    first_address = lookup_address(q)

    if not first_address:
        return {
            "error": "Address not found"
        }

    address_id = get_address_id(first_address)

    buildings = get_bbr_buildings(
        address_id,
        username,
        password
    )

    if not buildings:
        return {
            "error": "No BBR building found"
        }

    first_building = buildings[0]

    return {
        "normalized_address": first_address["adressebetegnelse"],
        "address_id": address_id,
        "building_year": first_building.get("byg026Opførelsesår"),
        "building_usage_code": first_building.get("byg021BygningensAnvendelse"),
        "heating_installation_code": first_building.get("byg056Varmeinstallation"),
        "building_area": first_building.get("byg038SamletBygningsareal")
    }

@app.get("/analyze-bbr-address")
def analyze_bbr_address(q: str, username: str, password: str):

    first_address = lookup_address(q)

    if not first_address:
        return {
            "error": "Address not found"
        }


    address_id = get_address_id(first_address)

    buildings = get_bbr_buildings(address_id, username, password)

    if not buildings:
        return {
            "input": q,
            "normalized_address": first_address["adressebetegnelse"],
            "address_id": address_id,
            "data_status": "Address found in DAWA, but no BBR building found for this access address",
            "error": "No BBR building found"
        }

    first_building = buildings[0]

    building = build_analysis_input(first_building)

    analysis = calculate_building_analysis(building)

    log_api_usage(
        supabase=supabase,
        endpoint="/analyze-address",
        address_query=q,
        normalized_address=first_address["adressebetegnelse"],
        api_key_prefix="bbr",
        analysis=analysis,
        data_status="Building year and heating type from BBR. Energy label and consumption are temporary."
    )

    return {
        "normalized_address": first_address["adressebetegnelse"],
        "address_id": address_id,
        "data_status": "Building year and heating type from BBR. Energy label and consumption are temporary.",
        "bbr_raw_fields": {
            "building_year": first_building.get("byg026Opførelsesår"),
            "heating_installation_code": first_building.get("byg056Varmeinstallation"),
            "building_area": first_building.get("byg038SamletBygningsareal")
        },
        "building_data_used": building,
        "analysis": analysis
    }

@app.get("/analyze-address")
def analyze_address(q: str):

    username = os.getenv("BBR_USERNAME")
    password = os.getenv("BBR_PASSWORD")

    if not username or not password:
        return {
            "error": "Missing BBR credentials in environment variables"
        }

    return analyze_bbr_address(q, username, password)

@app.get("/debug-energy-label")
def debug_energy_label(bbr_number: str):
    return search_energy_label_bbr(bbr_number)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(search: str = "", priority: str = ""):

    if not supabase:
        return "<h1>Supabase not connected</h1>"

    response = supabase.table("api_usage").select("*").order("created_at", desc=True).limit(20).execute()

    rows = response.data

    if search:
        rows = [
            row for row in rows
            if search.lower() in (row.get("normalized_address") or "").lower()
        ]

    if priority:
        rows = [
            row for row in rows
            if row.get("priority") == priority
        ]

    total_analyses = len(rows)

    scores = [row.get("score") for row in rows if row.get("score") is not None]

    if scores:
        average_score = round(sum(scores) / len(scores), 1)
    else:
        average_score = 0

    high_priority_count = len([
        row for row in rows
        if row.get("priority") == "High"
    ])

    medium_priority_count = len([
        row for row in rows
        if row.get("priority") == "Medium"
    ])

    low_priority_count = len([
        row for row in rows
        if row.get("priority") == "Low"
    ])

    latest_address = rows[0].get("normalized_address") if rows else "No analyses yet"

    top_buildings = sorted(
        rows,
        key=lambda x: x.get("score") or 0,
        reverse=True
    )[:5]

    high_risk_buildings = [
        row for row in rows
        if (row.get("score") or 0) >= 60
    ]

    html = f"""
    <html>
        <head>
            <title>Building Intelligence Dashboard</title>
        </head>
        <body style="font-family: Arial; padding: 30px; background-color: #f5f5f5;">

            <h1>Building Intelligence API Dashboard</h1>

            <form method="get" action="/dashboard" style="margin-bottom: 20px;">

                <input
                    type="text"
                    name="search"
                    placeholder="Search address..."
                    value="{search}"
                    style="padding: 10px; width: 300px;"
                >

                <select name="priority" style="padding: 10px;">
                    <option value="">All priorities</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>

                <button type="submit" style="padding: 10px;">
                    Search
                </button>

            </form>

            <div style="display: flex; gap: 20px; margin-bottom: 30px;">

                <div style="background: white; padding: 20px; border-radius: 10px; width: 220px;">
                    <h3>Total Analyses</h3>
                    <p style="font-size: 28px; font-weight: bold;">{total_analyses}</p>
                </div>

                <div style="background: white; padding: 20px; border-radius: 10px; width: 220px;">
                    <h3>Average Score</h3>
                    <p style="font-size: 28px; font-weight: bold;">{average_score}</p>
                </div>

                <div style="background: white; padding: 20px; border-radius: 10px; width: 220px;">
                    <h3>High Priority</h3>
                    <p style="font-size: 28px; font-weight: bold;">{high_priority_count}</p>
                </div>

                <div style="background: white; padding: 20px; border-radius: 10px; width: 300px;">
                    <h3>Latest Address</h3>
                    <p>{latest_address}</p>
                </div>

            </div>

            <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                <h2>Portfolio Overview</h2>

                <p>
                    🔴 High Risk Buildings: <strong>{high_priority_count}</strong>
                </p>

                <p>
                    🟠 Medium Risk Buildings: <strong>{medium_priority_count}</strong>
                </p>

                <p>
                    🟢 Low Risk Buildings: <strong>{low_priority_count}</strong>
                </p>
            </div>

            <h2>Top 5 Highest Scores</h2>
            <ul>

            <h2>Top 5 Highest Scores</h2>
            <ul>
    """

    for building in top_buildings:
        html += f"""
                <li>
                    {building.get("normalized_address")}
                    - Score: {building.get("score")}
                </li>
        """

    html += """
            <h2>High Risk Buildings</h2>
            <table border="1" cellpadding="8" style="background: white; border-collapse: collapse; margin-bottom: 30px;">
                <tr>
                    <th>Address</th>
                    <th>Score</th>
                    <th>Priority</th>
                    <th>Recommended Strategy</th>
                </tr>
    """

    for building in high_risk_buildings:
        address = building.get("normalized_address")

        html += f"""
                <tr>
                    <td>
                        <a href="/building-details?address={address}">
                            {address}
                        </a>
                    </td>
                    <td>{building.get("score")}</td>
                    <td style="color: red; font-weight: bold;">{building.get("priority")}</td>
                    <td>{building.get("recommended_strategy")}</td>
                </tr>
        """

    html += """
            </table>
    """

    html += """
            <h2>Latest API Analyses</h2>
            <table border="1" cellpadding="8">
                <tr>
                    <th>Time</th>
                    <th>Address</th>
                    <th>Score</th>
                    <th>Priority</th>
                    <th>ESG</th>
                    <th>ROI</th>
                    <th>Heat Pump</th>
                    <th>Summary</th>
                </tr>
    """

    for row in rows:

        priority = row.get("priority")

        if priority == "High":
            priority_color = "red"
        elif priority == "Medium":
            priority_color = "orange"
        else:
            priority_color = "green"

        html += f"""
                <tr>
                    <td>{row.get("created_at")}</td>
                    <td>{row.get("normalized_address")}</td>
                    <td>{row.get("score")}</td>
                    <td style="color: {priority_color}; font-weight: bold;">
                        {row.get("priority")}
                    </td>
                    <td>{row.get("esg_risk_score")}</td>
                    <td>{row.get("roi_score")}</td>
                    <td>{row.get("heat_pump_score")}</td>
                    <td>{row.get("executive_summary")}</td>
                </tr>
        """

    html += """
            </table>
        </body>
    </html>
    """

    return html


@app.get("/building-details", response_class=HTMLResponse)
def building_details(address: str):

    response = (
        supabase
        .table("api_usage")
        .select("*")
        .eq("normalized_address", address)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    rows = response.data

    if not rows:
        return "<h1>Building not found</h1>"

    building = rows[0]

    return f"""
    <html>
        <body style="font-family: Arial; padding: 30px;">
            <h1>{building.get("normalized_address")}</h1>

            <h2>Analysis Overview</h2>

            <p><strong>Upgrade Score:</strong> {building.get("score")}</p>
            <p><strong>Priority:</strong> {building.get("priority")}</p>
            <p><strong>ESG Risk Score:</strong> {building.get("esg_risk_score")}</p>
            <p><strong>ROI Score:</strong> {building.get("roi_score")}</p>
            <p><strong>Heat Pump Score:</strong> {building.get("heat_pump_score")}</p>

            <h2>Executive Summary</h2>

            <p>{building.get("executive_summary")}</p>

            <h2>Recommended Strategy</h2>

            <p>{building.get("recommended_strategy")}</p>

            <h2>Risk Flags</h2>

            <p>{building.get("risk_flags")}</p>

            <br>
            <a href="/dashboard">← Back to Dashboard</a>

        </body>
    </html>
    """

@app.post("/analyze-portfolio")
def analyze_portfolio(data: PortfolioInput):

    username = os.getenv("BBR_USERNAME")
    password = os.getenv("BBR_PASSWORD")

    results = []

    for address in data.addresses:

        try:

            result = analyze_bbr_address(
                address,
                username,
                password
            )

            results.append(result)

        except Exception as e:

            results.append({
                "address": address,
                "error": str(e)
            })

    successful_results = [
        result for result in results
        if "analysis" in result
    ]

    failed_results = [
        result for result in results
        if "analysis" not in result
    ]

    successful_results = sorted(
        successful_results,
        key=lambda x: x["analysis"]["upgrade_score"],
        reverse=True
    )

    if successful_results:
        average_score = round(
            sum(result["analysis"]["upgrade_score"] for result in successful_results)
            / len(successful_results),
            1
        )
    else:
        average_score = 0

    high_priority_count = len([
        result for result in successful_results
        if result["analysis"]["priority"] == "High"
    ])

    if average_score >= 75:
        portfolio_recommendation = "This portfolio has high renovation priority and should be reviewed for immediate upgrade opportunities."
    elif average_score >= 45:
        portfolio_recommendation = "This portfolio has medium renovation potential. Several buildings may be relevant for energy upgrades or investment review."
    else:
        portfolio_recommendation = "This portfolio has low renovation priority based on the available data."

    return {
        "total_addresses": len(data.addresses),
        "successful_analyses": len(successful_results),
        "failed_analyses": len(failed_results),
        "portfolio_summary": {
            "average_upgrade_score": average_score,
            "high_priority_count": high_priority_count,
            "portfolio_recommendation": portfolio_recommendation
        },
        "results": successful_results + failed_results
    }

@app.get("/debug-address-bbr")
def debug_address_bbr(q: str):

    first_address = lookup_address(q)

    if not first_address:
        return {
            "error": "Address not found in DAWA"
        }

    address_id = get_address_id(first_address)

    username = os.getenv("BBR_USERNAME")
    password = os.getenv("BBR_PASSWORD")

    buildings = get_bbr_buildings(address_id, username, password)

    return {
        "input": q,
        "normalized_address": first_address["adressebetegnelse"],
        "address_id": address_id,
        "bbr_buildings_found": len(buildings),
        "bbr_data": buildings
    }

@app.get("/debug-emo")
def debug_emo():

    username = os.getenv("filippa.hvitved@gmail.com")
    password = os.getenv("12345678")

    if not username or not password:
        return {
            "error": "Missing EMO credentials"
        }

    return test_emo_connection(username, password)