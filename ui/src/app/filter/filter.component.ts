import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Filter } from './filter';

@Component({
  selector: 'app-filter',
  templateUrl: 'filter.html'
})
export class FilterComponent {
  @Input() filter!: Filter;
  @Output() remove = new EventEmitter<Filter>();

  removeFilter() {
    this.remove.emit(this.filter);
  }
}
