import { Component, OnInit, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, GlobalStatistics as ApiGlobalStatistics } from '../../services/api.service';

// Extend the interface here for template type safety
interface GlobalStatistics extends ApiGlobalStatistics {
  total_jobs_seen?: number;
  total_attempted_applications?: number;
  skipped_excluded_keyword?: number;
  skipped_already_applied?: number;
  failed_other?: number;
}

@Component({
  selector: 'app-statistics-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './statistics-dashboard.component.html',
  styleUrls: ['./statistics-dashboard.component.css']
})
export class StatisticsDashboardComponent implements OnInit {
  @Input() email: string = '';
  @Input() password: string = '';
  stats: GlobalStatistics | null = null;
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    if (this.email && this.password) {
      this.api.getAdvancedStatistics(this.email, this.password).subscribe({
        next: (stats) => {
          this.stats = stats;
          this.loading = false;
        },
        error: (err) => {
          this.error = err.message || 'Failed to load statistics';
          this.loading = false;
        }
      });
    } else {
      this.loading = false;
      this.error = 'Email and password are required to load statistics.';
    }
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
    if (!this.stats?.per_search_term || !Array.isArray(this.stats.per_search_term)) return [];
    const total = Number(this.stats.total_applications);
    return this.stats.per_search_term
      .map((term: any) => ({
        term: term.search_term,
        count: Number(term.jobs_submitted),
        percentage: total > 0 ? (Number(term.jobs_submitted) / total) * 100 : 0
      }))
      .sort((a, b) => Number(b.count) - Number(a.count));
  }

  getContractTypeBreakdown() {
    if (!this.stats?.per_contract_type) return [];
    const total = Number(this.stats.total_applications);
    return Object.entries(this.stats.per_contract_type)
      .map(([type, count]) => ({
        type,
        count: Number(count),
        percentage: total > 0 ? (Number(count) / total) * 100 : 0
      }))
      .sort((a, b) => Number(b.count) - Number(a.count));
  }

  getRemoteTypeBreakdown() {
    if (!this.stats?.per_remote_type) return [];
    const total = Number(this.stats.total_applications);
    return Object.entries(this.stats.per_remote_type)
      .map(([type, count]) => ({
        type,
        count: Number(count),
        percentage: total > 0 ? (Number(count) / total) * 100 : 0
      }))
      .sort((a, b) => Number(b.count) - Number(a.count));
  }

  getDailyBreakdown() {
    if (!this.stats?.per_day) return [];
    const maxCount = Math.max(...Object.values(this.stats.per_day).map(Number));
    const maxHeight = 100; // Maximum height in pixels
    return Object.entries(this.stats.per_day)
      .map(([date, count]) => ({
        date: new Date(date),
        count: Number(count),
        height: maxCount > 0 ? (Number(count) / maxCount) * maxHeight : 0
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime());
  }
} 