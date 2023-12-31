import { Component, ViewChild } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Filter } from './filter/filter';
import { FiltersStorageService } from './filter/filters-storage.service';
import { NgForm } from '@angular/forms';
import { SupabaseService } from './supabase.service';
import { animate, state, style, transition, trigger } from '@angular/animations';

@Component({
  selector: 'app-root',
  templateUrl: 'app.html',
  animations: [
    trigger('fadeInOut', [
      state('void', style({ opacity: 0 })),
      state('*', style({ opacity: 1 })),
      transition(':enter', [
          animate('300ms ease-in')
      ]),
      transition(':leave', [
          animate('300ms ease-out')
      ]),
    ]),
  ],
  providers: [DatePipe]
})
export class AppComponent {
  loading = false;
  puts: any[] = [];
  readonly Filter = Filter;
  currentDate = '';
  showFilterForm = false;
  operators = Object.entries(Filter.operatorMapping).map(([key, value]) => ({
      key,
      value,
  }));
  @ViewChild('f') filterForm!: NgForm;

  constructor(private supabaseService: SupabaseService, private datePipe: DatePipe, protected filtersStorage: FiltersStorageService   ) {
      this.currentDate = datePipe.transform(new Date(), 'yyyy-MM-dd') || '';
      if (this.filtersStorage.size() == 0) {
          this.filtersStorage.filters = [
              new Filter('in_the_money', 'eq', false),
              new Filter('current_price', 'lte', 300),
              new Filter('price_strike_ratio', 'gte', 0.1),
              new Filter('days_until_expire', 'lte', 32),
              new Filter('bid_strike_ratio', 'gte', 0.01),
              new Filter('volume', 'gte', 5),
          ];
      }
  }


  async ngOnInit() {
    await this.fetchPuts();
  }

  async fetchPuts(){
      try {
          this.loading = true;
          this.puts = await this.supabaseService.fetchPuts(this.filtersStorage.filters, 100);
      } catch (error) {
          console.error(error);
      } finally {
          this.loading = false;
      }
  }

  async addFilter() {
      this.filtersStorage.push(new Filter(
          this.filterForm.value['column'],
          this.filterForm.value['operator'],
          this.filterForm.value['value']
      ));
      this.showFilterForm = false;
      await this.fetchPuts();
  }

  async removeFilter(filter: Filter) {
    this.filtersStorage.remove(filter);
    await this.fetchPuts();
  }
}
