import { Component } from '@angular/core';
import { ConfigurationComponent } from './components/configuration/configuration.component';
import { StatisticsDashboardComponent } from './components/statistics-dashboard/statistics-dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ConfigurationComponent, StatisticsDashboardComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {}
