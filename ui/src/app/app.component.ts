import { Component } from '@angular/core';
import { SupabaseService } from './supabase.service';
import { Filter } from './filter/filter';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: 'app.html',
  providers: [DatePipe]
})
export class AppComponent {
  puts: any[] = [];
  readonly Filter = Filter;
  filters: Filter[] = [
      new Filter('in_the_money', 'eq', false),
      new Filter('current_price', 'lte', 300),
      new Filter('price_strike_ratio', 'gte', 0.1),
      new Filter('days_until_expire', 'lte', 32),
      new Filter('bid_strike_ratio', 'gte', 0.01),
  ];
  currentDate = '';
  showFilterForm = false;
  column = '';
  operator = 'eq';
  value = '';
  operators = Object.entries(Filter.operatorMapping).map(([key, value]) => ({
      key,
      value,
  }));

  constructor(private supabaseService: SupabaseService, private datePipe: DatePipe) {
      this.currentDate = datePipe.transform(new Date(), 'yyyy-MM-dd') || '';
  }


  async ngOnInit() {
    await this.fetchPuts();
  }

  async fetchPuts(){
      this.puts = await this.supabaseService.fetchPuts(this.filters, 100);
  }

  async addFilter() {
      this.filters.push(new Filter(this.column, this.operator, this.value));
      this.showFilterForm = false;
      this.resetForm();
      await this.fetchPuts();
  }

  async removeFilter(filter: Filter) {
    this.filters = this.filters.filter(f=> f !== filter);
    await this.fetchPuts();
  }

  private resetForm() {
      this.column = '';
      this.operator = 'eq';
      this.value = ''
  }
}
