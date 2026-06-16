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

    energy_proposals = building.get("energy_proposals", [])

    recommended_proposal_count = len(energy_proposals)

    total_recommended_investment = sum(
        proposal.get("investment") or 0
        for proposal in energy_proposals
    )

    total_recommended_savings = sum(
        proposal.get("money_saving") or 0
        for proposal in energy_proposals
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

    if not recommended_strategy:
        recommended_strategy.append("No immediate action recommended based on current data")

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
        "recommended_proposal_count": recommended_proposal_count,
        "total_recommended_investment": total_recommended_investment,
        "total_recommended_savings": total_recommended_savings,
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
        os.getenv("API_KEY", "test123")
    ]

    return api_key in valid_keys
