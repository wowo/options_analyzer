import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: 'app.html',
  styles: []
})
export class AppComponent {
  rows = [{
    strike: 104, current_price: 120, contract_symbol: 'asd', symbol: 'META', long_name: 'Lorem ipsum', industry: 'Internet', sector: 'Test', bid: 5, ask: 6, iv: 0.3, delta: 0.01, expiration: '2023-11-23', days_until_expire: 23, volume: 100, trailing_eps: 10, trailing_pe: 100, forward_eps: 120, forward_pe: 130, next_earnings_date: '2023-11-30', updated_at: '2023-10-30 23:45:45'
  }];
}
