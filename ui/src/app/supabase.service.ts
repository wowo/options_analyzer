import { Injectable } from '@angular/core';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { environment } from '../environments/environment';
import { Filter } from './filter/filter';

@Injectable({
  providedIn: 'root'
})
export class SupabaseService {
  private supabase: SupabaseClient;

  constructor() {
    this.supabase = createClient(
      environment.supabaseUrl,
      environment.supabaseKey
    );
  }

  async fetchPuts(filters: Filter[], limit: number): Promise<any> {
    let query = this
        .supabase
        .from('puts_all')
        .select('*');
    for (let filter of filters) {
      query.filter(filter.column, filter.operator, filter.value);
    }
    const { data, error } = await query.limit(limit);
    if (error) {
      throw new Error(error.message);
    }
    return data;
  }
}
