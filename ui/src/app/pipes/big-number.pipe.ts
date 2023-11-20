import { Pipe, PipeTransform } from '@angular/core';
import { DecimalPipe } from '@angular/common';

@Pipe({
  name: 'bigNumber'
})
export class BigNumberPipe implements PipeTransform {

  constructor(private decimalPipe: DecimalPipe) {}

  transform(value: any, ...args: unknown[]): unknown {

    let num = Number(value);
    if (num >= 1e12) {
      return this.decimalPipe.transform(num / 1e12, '.2-2') + 'T';
    }
    if (num >= 1e9) {
      return this.decimalPipe.transform(num / 1e9, '.2-2') + 'B';
    }
    if (num >= 1e6) {
      return this.decimalPipe.transform(num / 1e6, '.2-2') + 'M';
    }
    return this.decimalPipe.transform(num, '.0-0');
  }

}
