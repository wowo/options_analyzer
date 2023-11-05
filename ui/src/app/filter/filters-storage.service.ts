import { Filter } from './filter';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class FiltersStorageService {

  private _filters: Filter[] = [];

  get filters(): Filter[]  {
    return this._filters;
  }

  set filters(value: Filter[]) {
    this._filters = value;
    this.onFilterChange();
  }

  constructor() {
    const savedFilters = localStorage.getItem('filters');
    if (savedFilters) {
      this._filters = JSON.parse(savedFilters).map((filter: any) => new Filter(filter.column, filter.operator, filter.value));;
    }
  }

  size(): number {
    return this._filters.length;
  }

  push(filter: Filter) {
    this._filters.push(filter);
    this.onFilterChange();
  }

  remove(filter: Filter) {
    this._filters = this._filters.filter(f=> f !== filter);
    this.onFilterChange();
  }

  private onFilterChange() {
    localStorage.setItem('filters', JSON.stringify(this._filters));
  }
}
