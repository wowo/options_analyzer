export class Filter {
    constructor(public column: string, public operator: string, public value: any) {}

    public getOperatorForUI(): string {
        const mapping : Record<string, string> = {
            EQ: '=',
            LTE: '<=',
            LT: '<',
            GTE: '>=',
            GT: '>'
        }

        return mapping[this.operator.toUpperCase()] || this.operator;
    }

    public getColumnForUI(): string {
        return this.column.replaceAll('_', ' ')
    }
}
