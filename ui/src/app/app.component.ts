import { Component } from '@angular/core';
import { SupabaseService } from './supabase.service';
import {Filter} from "./model/filter";

@Component({
  selector: 'app-root',
  templateUrl: 'app.html',
})
export class AppComponent {
  puts: any[] = [];
  filters: Filter[] = [
      new Filter('in_the_money', 'eq', false),
      new Filter('current_price', 'lte', 300),
      new Filter('price_strike_ratio', 'gte', 0.1),
      new Filter('days_until_expire', 'lte', 32),
      new Filter('bid_strike_ratio', 'gte', 0.01),
  ];

  constructor(private supabaseService: SupabaseService) {}


  async ngOnInit() {
    this.puts = await this.supabaseService.fetchPuts(this.filters, 100);
  }
}
