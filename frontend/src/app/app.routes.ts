import { Routes } from '@angular/router';
import { ConfigurationComponent } from './components/configuration/configuration.component';

export const routes: Routes = [
  { path: '', redirectTo: '/config', pathMatch: 'full' },
  { path: 'config', component: ConfigurationComponent }
];
