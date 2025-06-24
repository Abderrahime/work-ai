import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, GlobalStatistics } from '../../services/api.service';

@Component({
  selector: 'app-statistics-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './statistics-dashboard.component.html',
  styleUrls: ['./statistics-dashboard.component.css']
})
export class StatisticsDashboardComponent implements OnInit {
  stats: GlobalStatistics | null = null;
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.getAdvancedStatistics().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message || 'Failed to load statistics';
        this.loading = false;
      }
    });
  }

  // Helper methods for template
  hasSearchTerms(): boolean {
    return !!(this.stats?.per_search_term && Object.keys(this.stats.per_search_term).length > 0);
  }

  hasContractTypes(): boolean {
    return !!(this.stats?.per_contract_type && Object.keys(this.stats.per_contract_type).length > 0);
  }

  hasRemoteTypes(): boolean {
    return !!(this.stats?.per_remote_type && Object.keys(this.stats.per_remote_type).length > 0);
  }

  hasDailyData(): boolean {
    return !!(this.stats?.per_day && Object.keys(this.stats.per_day).length > 0);
  }

  getSearchTermBreakdown() {
    if (!this.stats?.per_search_term) return [];
    
    const total = this.stats.total_applications;
    return Object.entries(this.stats.per_search_term)
      .map(([term, count]) => ({
        term,
        count,
        percentage: total > 0 ? (count / total) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count);
  }

  getContractTypeBreakdown() {
    if (!this.stats?.per_contract_type) return [];
    
    const total = this.stats.total_applications;
    return Object.entries(this.stats.per_contract_type)
      .map(([type, count]) => ({
        type,
        count,
        percentage: total > 0 ? (count / total) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count);
  }

  getRemoteTypeBreakdown() {
    if (!this.stats?.per_remote_type) return [];
    
    const total = this.stats.total_applications;
    return Object.entries(this.stats.per_remote_type)
      .map(([type, count]) => ({
        type,
        count,
        percentage: total > 0 ? (count / total) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count);
  }

  getDailyBreakdown() {
    if (!this.stats?.per_day) return [];
    
    const maxCount = Math.max(...Object.values(this.stats.per_day));
    const maxHeight = 100; // Maximum height in pixels
    
    return Object.entries(this.stats.per_day)
      .map(([date, count]) => ({
        date: new Date(date),
        count,
        height: maxCount > 0 ? (count / maxCount) * maxHeight : 0
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime());
  }
} 