import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, FormArray, ReactiveFormsModule } from '@angular/forms';
import { ApiService, SearchConfig, Statistics } from '../../services/api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.css'],
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule]
})
export class ConfigurationComponent implements OnInit {
  configForm: FormGroup;
  saveStatus = '';
  showStatistics = false;
  currentStats: Statistics | null = null;

  contractOptions = [
    { value: 'permanent', label: 'CDI' },
    { value: 'contractor', label: 'Freelance' },
    { value: 'fixed-term', label: 'CDD' },
    { value: 'apprenticeship', label: 'Alternance' },
    { value: 'internship', label: 'Stage' }
  ];

  remoteOptions = [
    { value: 'partial', label: 'Télétravail partiel' },
    { value: 'full', label: 'Télétravail 100%' },
    { value: 'none', label: 'Présentiel' }
  ];

  publicationOptions = [
    { value: 'less_than_24_hours', label: 'Moins de 24h' },
    { value: 'less_than_7_days', label: 'Moins de 7 jours' },
    { value: 'less_than_14_days', label: 'Moins de 14 jours' },
    { value: 'less_than_30_days', label: 'Moins de 30 jours' }
  ];

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.configForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      search_terms: this.fb.array([this.fb.control('', Validators.required)]),
      contract_types: this.fb.array([]),
      remote_types: this.fb.array([]),
      publication_timeframes: ['less_than_30_days', Validators.required],
      excluded_keywords: this.fb.array([this.fb.control('')]),
      application_message: ['', Validators.required],
      max_applications_per_session: [10, [Validators.required, Validators.min(1), Validators.max(1000)]],
      delay_between_applications: [5, [Validators.required, Validators.min(1), Validators.max(60)]]
    });
  }

  ngOnInit(): void {
    // Load config if email and password are present and valid
    this.configForm.get('email')?.valueChanges.subscribe(() => this.tryLoadConfig());
    this.configForm.get('password')?.valueChanges.subscribe(() => this.tryLoadConfig());
    this.tryLoadConfig();
    this.configForm.valueChanges.subscribe(() => {
      if (this.configForm.valid) {
        this.saveConfig();
      }
    });
  }

  private tryLoadConfig(): void {
    const email = this.configForm.get('email')?.value;
    const password = this.configForm.get('password')?.value;
    if (email && password && this.configForm.get('email')?.valid && this.configForm.get('password')?.valid) {
      this.api.getConfig(email, password).subscribe({
        next: (config: SearchConfig) => {
          let publication_timeframes = config.publication_timeframes;
          if (Array.isArray(publication_timeframes)) {
            publication_timeframes = publication_timeframes[0] || 'less_than_30_days';
          }
          const formValue = {
            ...config,
            publication_timeframes
          };
          this.configForm.patchValue(formValue);
        },
        error: (error: any) => {
          // No saved configuration found, using defaults
        }
      });
    }
  }

  getSearchTermsArray(): FormArray {
    return this.configForm.get('search_terms') as FormArray;
  }

  getExcludedKeywordsArray(): FormArray {
    return this.configForm.get('excluded_keywords') as FormArray;
  }

  saveConfig() {
    if (this.configForm.invalid) return;
    const formValue = this.configForm.value;
    const config: SearchConfig = {
      search_terms: formValue.search_terms.filter((term: string) => term.trim()),
      contract_types: formValue.contract_types,
      remote_types: formValue.remote_types,
      publication_timeframes: formValue.publication_timeframes,
      excluded_keywords: formValue.excluded_keywords.filter((keyword: string) => keyword.trim()),
      application_message: formValue.application_message,
      max_applications_per_session: formValue.max_applications_per_session,
      delay_between_applications: formValue.delay_between_applications
    };
    const email = formValue.email;
    const password = formValue.password;
    this.api.saveConfig(config, email, password).subscribe({
      next: () => {
        this.saveStatus = 'Configuration saved!';
        setTimeout(() => this.saveStatus = '', 2000);
      },
      error: (error: any) => {
        this.saveStatus = 'Failed to save configuration';
        setTimeout(() => this.saveStatus = '', 3000);
      }
    });
  }

  onPublicationTimeframeChange(event: any) {
    console.log('Dropdown changed, selected publication_timeframes:', event.target.value);
  }

  addSearchTerm() {
    this.getSearchTermsArray().push(this.fb.control('', Validators.required));
  }

  removeSearchTerm(index: number) {
    if (this.getSearchTermsArray().controls.length > 1) {
      this.getSearchTermsArray().removeAt(index);
    }
  }

  addExcludedKeyword() {
    this.getExcludedKeywordsArray().push(this.fb.control(''));
  }

  removeExcludedKeyword(index: number) {
    if (this.getExcludedKeywordsArray().controls.length > 1) {
      this.getExcludedKeywordsArray().removeAt(index);
    }
  }

  onContractTypeChange(event: any, value: string) {
    const contractTypes = this.configForm.get('contract_types') as FormArray;
    if (event.target.checked) {
      contractTypes.push(this.fb.control(value));
    } else {
      const index = contractTypes.controls.findIndex(control => control.value === value);
      if (index >= 0) {
        contractTypes.removeAt(index);
      }
    }
  }

  onRemoteTypeChange(event: any, value: string) {
    const remoteTypes = this.configForm.get('remote_types') as FormArray;
    if (event.target.checked) {
      remoteTypes.push(this.fb.control(value));
    } else {
      const index = remoteTypes.controls.findIndex(control => control.value === value);
      if (index >= 0) {
        remoteTypes.removeAt(index);
      }
    }
  }

  startSession() {
    if (this.configForm.invalid) {
      this.saveStatus = '❌ Please fix form errors before starting session';
      setTimeout(() => this.saveStatus = '', 3000);
      return;
    }
    this.saveStatus = '🚀 Starting application session...';
    const email = this.configForm.get('email')?.value;
    const password = this.configForm.get('password')?.value;
    this.api.startSession(email, password).subscribe({
      next: () => {
        this.saveStatus = '✅ Application session started successfully!';
        setTimeout(() => this.saveStatus = '', 3000);
        this.viewStatistics();
      },
      error: (error: any) => {
        this.saveStatus = '❌ Failed to start session: ' + error.message;
        setTimeout(() => this.saveStatus = '', 5000);
      }
    });
  }

  viewStatistics() {
    if (this.configForm.invalid) {
      this.saveStatus = '❌ Please fix form errors before viewing statistics';
      setTimeout(() => this.saveStatus = '', 3000);
      return;
    }
    this.showStatistics = !this.showStatistics;
    if (this.showStatistics) {
      const email = this.configForm.get('email')?.value;
      const password = this.configForm.get('password')?.value;
      this.api.getStatistics(email, password).subscribe({
        next: (stats: Statistics) => {
          this.currentStats = stats;
          this.saveStatus = `📊 Statistics loaded: ${stats.total_applications} total applications, ${stats.successful_applications} successful (${stats.success_rate.toFixed(1)}% success rate)`;
          setTimeout(() => this.saveStatus = '', 5000);
        },
        error: (error: any) => {
          this.saveStatus = '❌ Failed to load statistics: ' + error.message;
          setTimeout(() => this.saveStatus = '', 5000);
        }
      });
    }
  }

  scrollToStatistics() {
    const statsElement = document.querySelector('app-statistics-dashboard');
    if (statsElement) {
      statsElement.scrollIntoView({ behavior: 'smooth' });
    }
  }
} 