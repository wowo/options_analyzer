import localePl from '@angular/common/locales/pl';
import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { BigNumberPipe } from './big-number.pipe';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { FilterComponent } from './filter/filter.component';
import { FormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { registerLocaleData } from '@angular/common';
import { CommonModule, DecimalPipe } from '@angular/common';

registerLocaleData(localePl, 'pl-PL');

@NgModule({
  declarations: [
    AppComponent,
    FilterComponent,
    BigNumberPipe
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    CommonModule,
    AppRoutingModule,
    FormsModule
  ],
  providers: [
      DecimalPipe
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
