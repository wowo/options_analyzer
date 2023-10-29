from supabase import Client


def get_options_with_filters(supabase: Client, filters: list, orders: list, limit: int):
    print(filters)
    puts = supabase.table('puts_all') \
        .select('*') \
        .limit(limit)
    for filter_value in filters:
        puts.filter(filter_value['column'], filter_value['op'], filter_value['criteria'])

    for order_value in orders:
        puts.order(order_value['column'], desc='dir' in order_value and order_value['dir'] == 'desc')

    return puts.execute().data
