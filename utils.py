from supabase import Client


def get_symbols_from_database(supabase: Client) -> ():
    response = supabase.table('stocks') \
        .select('symbol') \
        .execute()
    return sorted([x['symbol'] for x in response.data])
