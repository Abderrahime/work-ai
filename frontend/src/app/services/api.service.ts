import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Credentials {
  email: string;
  password: string;
}

export interface SearchConfig {
  search_terms: string[];
  contract_types: string[];
  remote_types: string[];
  publication_timeframes: string;
  excluded_keywords: string[];
  application_message: string;
  max_applications_per_session: number;
  delay_between_applications: number;
}

export interface Statistics {
  total_applications: number;
  successful_applications: number;
  failed_applications: number;
  success_rate: number;
  last_session?: string;
  sessions: any[];
  skipped_excluded_keyword?: number;
  skipped_already_applied?: number;
  failed_other?: number;
  total_jobs_seen?: number;
  total_attempted_applications?: number;
}

export interface SessionStatus {
  status: string;
  message: string;
  progress?: number;
  current_job?: string;
}

export interface ApplicationDetail {
  job_title: string;
  company: string;
  status: string;
  timestamp: string;
  search_term: string;
  contract_type: string;
  remote_type: string;
  reason?: string;
}

export interface SessionStatistics {
  session_id: string;
  date: string;
  applications: ApplicationDetail[];
  total: number;
  successful: number;
  failed: number;
  success_rate: number;
  skipped_excluded_keyword?: number;
  skipped_already_applied?: number;
  failed_other?: number;
  total_jobs_seen?: number;
  total_attempted_applications?: number;
}

export interface PerSearchTermStats {
  search_term: string;
  jobs_found: number;
  jobs_submitted: number;
  jobs_already_applied: number;
  jobs_excluded: number;
  jobs_failed: number;
}

export interface GlobalStatistics {
  total_applications: number;
  successful_applications: number;
  failed_applications: number;
  success_rate: number;
  sessions: SessionStatistics[];
  per_search_term: PerSearchTermStats[];
  per_contract_type: { [key: string]: number };
  per_remote_type: { [key: string]: number };
  per_day: { [key: string]: number };
  last_session?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';
    if (typeof window !== 'undefined' && error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else {
      errorMessage = error.error?.detail || error.message || 'Server error';
    }
    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }

  // Stateless: pass credentials with each request
  getConfig(email: string, password: string): Observable<SearchConfig> {
    return this.http.get<SearchConfig>(`${this.apiUrl}/config`, {
      headers: this.getHeaders(),
      params: { email, password }
    }).pipe(catchError(this.handleError));
  }

  saveConfig(config: SearchConfig, email: string, password: string): Observable<any> {
    // Send credentials as additional fields in the body
    const body = { ...config, email, password };
    return this.http.post(`${this.apiUrl}/config`, body, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  getStatistics(email: string, password: string): Observable<Statistics> {
    return this.http.get<Statistics>(`${this.apiUrl}/statistics`, {
      headers: this.getHeaders(),
      params: { email, password }
    }).pipe(catchError(this.handleError));
  }

  getAdvancedStatistics(email: string, password: string): Observable<GlobalStatistics> {
    return this.http.get<GlobalStatistics>(`${this.apiUrl}/statistics/advanced`, {
      headers: this.getHeaders(),
      params: { email, password }
    }).pipe(catchError(this.handleError));
  }

  startSession(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/session/start`, { email, password }, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  clearData(email: string, password: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/data`, {
      headers: this.getHeaders(),
      params: { email, password }
    }).pipe(catchError(this.handleError));
  }
} 