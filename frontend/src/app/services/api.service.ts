import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

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
  private apiUrl = 'http://localhost:8000';
  private authToken: string | null = null;
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadAuthToken();
    this.checkAuthStatus();
  }

  private loadAuthToken(): void {
    if (typeof window !== 'undefined') {
      this.authToken = localStorage.getItem('authToken');
      if (this.authToken) {
        this.isAuthenticatedSubject.next(true);
      }
    }
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });
    
    if (this.authToken) {
      headers = headers.set('Authorization', `Bearer ${this.authToken}`);
    }
    
    return headers;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';
    
    // Check if we're in a browser environment before using ErrorEvent
    if (typeof window !== 'undefined' && error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      errorMessage = error.error?.detail || error.message || 'Server error';
    }
    
    console.error('API Error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }

  // Authentication
  login(credentials: Credentials): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response: any) => {
          this.authToken = credentials.email; // Use email as token for now
          this.isAuthenticatedSubject.next(true);
          if (typeof window !== 'undefined' && this.authToken) {
            localStorage.setItem('authToken', this.authToken);
          }
        }),
        catchError(this.handleError)
      );
  }

  logout(): void {
    this.authToken = null;
    this.isAuthenticatedSubject.next(false);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
    }
  }

  checkAuthStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/auth/status`)
      .pipe(
        tap((response: any) => {
          if (response.authenticated) {
            this.authToken = response.email;
            this.isAuthenticatedSubject.next(true);
            if (typeof window !== 'undefined' && this.authToken) {
              localStorage.setItem('authToken', this.authToken);
            }
          }
        }),
        catchError(this.handleError)
      );
  }

  // Configuration
  getConfig(): Observable<SearchConfig> {
    return this.http.get<SearchConfig>(`${this.apiUrl}/config`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  saveConfig(config: SearchConfig): Observable<any> {
    return this.http.post(`${this.apiUrl}/config`, config, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  // Statistics
  getStatistics(): Observable<Statistics> {
    return this.http.get<Statistics>(`${this.apiUrl}/statistics`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  // Auto-save functionality
  private autoSaveTimeout: any;
  
  triggerAutoSave(config: SearchConfig): void {
    // Clear existing timeout
    if (this.autoSaveTimeout) {
      clearTimeout(this.autoSaveTimeout);
    }
    
    // Set new timeout (2 seconds delay)
    this.autoSaveTimeout = setTimeout(() => {
      this.saveConfig(config).subscribe({
        next: () => console.log('Configuration auto-saved'),
        error: (error) => console.error('Auto-save failed:', error)
      });
    }, 2000);
  }

  getAdvancedStatistics(): Observable<GlobalStatistics> {
    return this.http.get<GlobalStatistics>(`${this.apiUrl}/statistics/advanced`, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }

  // Session management
  startSession(): Observable<any> {
    return this.http.post(`${this.apiUrl}/session/start`, {}, { headers: this.getHeaders() })
      .pipe(catchError(this.handleError));
  }
} 