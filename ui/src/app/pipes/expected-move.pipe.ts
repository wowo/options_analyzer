import { Pipe, PipeTransform } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Pipe({
  name: 'expectedMove'
})
export class ExpectedMovePipe implements PipeTransform {

  constructor(private decimalPipe: DecimalPipe) {}

  transform(value: any, asPercent: boolean = false): string {

    const iv = Number(value.iv);
    const price = Number(value.current_price);
    const daysUntilExpire = Number(value.days_until_expire);

    const expectedMove = iv * price * Math.sqrt(daysUntilExpire / 252);

    return asPercent
        ? (100 * expectedMove / price).toString()
        : expectedMove.toString();
  }

}
