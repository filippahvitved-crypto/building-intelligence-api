def log_api_usage(supabase, endpoint, address_query, normalized_address, api_key_prefix, score):

    if supabase:
        supabase.table("api_usage").insert({
            "endpoint": endpoint,
            "address_query": address_query,
            "normalized_address": normalized_address,
            "api_key_prefix": api_key_prefix,
            "status": "success",
            "score": score
        }).execute()