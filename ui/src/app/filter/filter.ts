export class Filter {
    public static operatorMapping : Record<string, string> = {
        EQ: '=',
        LTE: '<=',
        LT: '<',
        GTE: '>=',
        GT: '>'
    }

    public static columns = [
        'symbol',
        'expiration',
        'bid',
        'ask',
        'iv',
        'days_until_expire',
        'next_earnings_date',
        'diff',
        'strike',
        'current_price',
        'previous_close',
        'volume',
        'open_interest',
        'last_trade_date',
        'forward_eps',
        'forward_pe',
        'trailing_eps',
        'trailing_pe',
        'market_cap',
        'updated_at',
        'contract_symbol',
        'delta',
        'in_the_money',
        'bid_strike_ratio',
        'price_strike_ratio',

]
    constructor(public column: string, public operator: string, public value: any) {
        if (this.column == 'symbol') {
            this.value = this.value.toUpperCase();
        }
    }

    public getOperatorForUI(): string {
        return Filter.operatorMapping[this.operator.toUpperCase()] || this.operator;
    }

    public getColumnForUI(): string {
        return this.column.replaceAll('_', ' ')
    }
}
