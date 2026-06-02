def log_api_usage(
    supabase,
    endpoint,
    address_query,
    normalized_address,
    api_key_prefix,
    analysis,
    data_status
):

    if supabase:
        supabase.table("api_usage").insert({
            "endpoint": endpoint,
            "address_query": address_query,
            "normalized_address": normalized_address,
            "api_key_prefix": api_key_prefix,
            "status": "success",
            "score": analysis["upgrade_score"],
            "priority": analysis["priority"],
            "esg_risk_score": analysis["esg_risk_score"],
            "roi_score": analysis["roi_score"],
            "heat_pump_score": analysis["heat_pump_compatibility_score"],
            "data_status": data_status,
            "executive_summary": analysis["executive_summary"],
            "recommended_strategy": analysis["recommended_strategy"],
            "risk_flags": analysis["risk_flags"]
        }).execute()