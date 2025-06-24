import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from config import SecureConfig
from logger import SecureLogger
import threading
import time

class FreeWorkInterface:
    def __init__(self):
        self.config = SecureConfig()
        self.logger = SecureLogger()
        self.auto_save_timer = None
        self.changes_pending = False
        
        self.root = tk.Tk()
        self.root.title("FreeWork Job Application Assistant")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # --- Scrollable main frame setup ---
        self.canvas = tk.Canvas(self.root, borderwidth=0, background='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # --- End scrollable main frame setup ---
        
        self.setup_ui()
        self.load_existing_config()
        
        # Auto-save status label
        self.status_label = ttk.Label(self.root, text="✅ Configuration saved", foreground="green")
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=2)
        self.status_label.pack_forget()  # Hide initially
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = self.scrollable_frame
        
        # Title
        title_label = ttk.Label(main_frame, text="FreeWork Job Application Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Security message
        security_frame = ttk.LabelFrame(main_frame, text="🔒 Security Information", padding="10")
        security_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        security_text = """Your credentials are encrypted and stored securely on your local machine. 
        We use industry-standard encryption (Fernet) to protect your data. 
        Your password and email are never stored in plain text and are only used to log into FreeWork.
        
        🔐 Your data is stored in: ~/.freework_app/
        📁 Logs are stored in: ~/.freework_app/logs/
        🗑️  You can delete these folders anytime to remove all data."""
        
        security_label = ttk.Label(security_frame, text=security_text, wraplength=700, justify=tk.LEFT)
        security_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="👤 Account Credentials", padding="10")
        cred_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(cred_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(cred_frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Search configuration section
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Search Configuration", padding="10")
        search_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Search terms
        ttk.Label(search_frame, text="Search Terms (one per line):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_terms_text = scrolledtext.ScrolledText(search_frame, height=4, width=50)
        self.search_terms_text.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Contract types
        ttk.Label(search_frame, text="Contract Types:").grid(row=1, column=0, sticky=tk.W, pady=5)
        contract_frame = ttk.Frame(search_frame)
        contract_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.contract_vars = {}
        contract_options = [
            ('permanent', 'CDI'),
            ('contractor', 'Freelance'),
            ('fixed-term', 'CDD'),
            ('apprenticeship', 'Alternance'),
            ('internship', 'Stage')
        ]
        
        for i, (value, label) in enumerate(contract_options):
            var = tk.BooleanVar()
            self.contract_vars[value] = var
            ttk.Checkbutton(contract_frame, text=label, variable=var).grid(row=i//2, column=i%2, sticky=tk.W)
        
        # Remote types
        ttk.Label(search_frame, text="Remote Work Types:").grid(row=2, column=0, sticky=tk.W, pady=5)
        remote_frame = ttk.Frame(search_frame)
        remote_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        self.remote_vars = {}
        remote_options = [
            ('partial', 'Télétravail partiel'),
            ('full', 'Télétravail 100%'),
            ('none', 'Présentiel')
        ]
        
        for i, (value, label) in enumerate(remote_options):
            var = tk.BooleanVar()
            self.remote_vars[value] = var
            ttk.Checkbutton(remote_frame, text=label, variable=var).grid(row=0, column=i, sticky=tk.W)
        
        # Publication timeframe
        ttk.Label(search_frame, text="Publication Timeframe:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.timeframe_var = tk.StringVar()
        timeframe_combo = ttk.Combobox(search_frame, textvariable=self.timeframe_var, state="readonly")
        timeframe_combo['values'] = [
            'less_than_24_hours',
            'less_than_7_days', 
            'less_than_14_days',
            'less_than_30_days'
        ]
        timeframe_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        timeframe_combo.set('less_than_30_days')
        
        # Application settings
        app_frame = ttk.LabelFrame(main_frame, text="📝 Application Settings", padding="10")
        app_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(app_frame, text="Application Message:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.message_text = scrolledtext.ScrolledText(app_frame, height=6, width=50)
        self.message_text.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Excluded keywords
        ttk.Label(app_frame, text="Excluded Keywords (comma-separated):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.excluded_keywords_var = tk.StringVar()
        ttk.Entry(app_frame, textvariable=self.excluded_keywords_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Max applications
        ttk.Label(app_frame, text="Max Applications per Session:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_apps_var = tk.StringVar(value="50")
        ttk.Entry(app_frame, textvariable=self.max_apps_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="🚀 Start Application Session", 
                  command=self.start_session).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="📊 View Statistics", 
                  command=self.show_statistics).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="🗑️  Clear All Data", 
                  command=self.clear_data).grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        for frame in [cred_frame, search_frame, app_frame]:
            frame.columnconfigure(1, weight=1)
        
        # Set up auto-save triggers
        self.setup_auto_save_triggers()
    
    def setup_auto_save_triggers(self):
        """Set up triggers for auto-save functionality"""
        # Bind text changes to auto-save
        self.search_terms_text.bind('<KeyRelease>', self.trigger_auto_save)
        self.message_text.bind('<KeyRelease>', self.trigger_auto_save)
        
        # Bind variable changes to auto-save
        self.email_var.trace_add('write', self.trigger_auto_save)
        self.password_var.trace_add('write', self.trigger_auto_save)
        self.timeframe_var.trace_add('write', self.trigger_auto_save)
        self.excluded_keywords_var.trace_add('write', self.trigger_auto_save)
        self.max_apps_var.trace_add('write', self.trigger_auto_save)
        
        # Bind checkbox changes to auto-save
        for var in self.contract_vars.values():
            var.trace_add('write', self.trigger_auto_save)
        for var in self.remote_vars.values():
            var.trace_add('write', self.trigger_auto_save)
    
    def trigger_auto_save(self, *args):
        """Trigger auto-save with a delay to avoid too frequent saves"""
        self.changes_pending = True
        
        # Cancel existing timer
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Set new timer (save after 2 seconds of no changes)
        self.auto_save_timer = self.root.after(2000, self.perform_auto_save)
        
        # Show "saving..." status
        self.show_status("⏳ Saving...", "blue")
    
    def perform_auto_save(self):
        """Perform the actual auto-save operation"""
        if not self.changes_pending:
            return
        
        try:
            # Save credentials
            email = self.email_var.get().strip()
            password = self.password_var.get().strip()
            
            if email and password:
                self.config.save_credentials(email, password)
            
            # Prepare search configuration
            search_terms = [term.strip() for term in self.search_terms_text.get(1.0, tk.END).strip().split('\n') if term.strip()]
            
            contract_types = [value for value, var in self.contract_vars.items() if var.get()]
            remote_types = [value for value, var in self.remote_vars.items() if var.get()]
            
            excluded_keywords = [kw.strip() for kw in self.excluded_keywords_var.get().split(',') if kw.strip()]
            
            search_config = {
                'search_terms': search_terms,
                'contract_types': contract_types,
                'remote_types': remote_types,
                'publication_timeframes': [self.timeframe_var.get()],
                'excluded_keywords': excluded_keywords,
                'application_message': self.message_text.get(1.0, tk.END).strip(),
                'max_applications_per_session': int(self.max_apps_var.get()) if self.max_apps_var.get().isdigit() else 50,
                'delay_between_applications': 2
            }
            
            self.config.save_search_config(search_config)
            
            self.changes_pending = False
            self.show_status("✅ Configuration saved automatically", "green")
            self.logger.success("Configuration auto-saved successfully")
            
        except Exception as e:
            self.show_status("❌ Auto-save failed", "red")
            self.logger.error(f"Auto-save failed: {str(e)}")
    
    def show_status(self, message, color):
        """Show status message at the bottom of the window"""
        self.status_label.config(text=message, foreground=color)
        self.status_label.pack(side="bottom", fill="x", padx=5, pady=2)
        
        # Hide status after 3 seconds
        self.root.after(3000, self.hide_status)
    
    def hide_status(self):
        """Hide the status message"""
        self.status_label.pack_forget()
    
    def load_existing_config(self):
        """Load existing configuration"""
        email, password = self.config.load_credentials()
        if email and password:
            self.email_var.set(email)
            self.password_var.set(password)
        
        search_config = self.config.load_search_config()
        
        # Load search terms
        self.search_terms_text.delete(1.0, tk.END)
        self.search_terms_text.insert(1.0, '\n'.join(search_config['search_terms']))
        
        # Load contract types
        for value, var in self.contract_vars.items():
            var.set(value in search_config['contract_types'])
        
        # Load remote types
        for value, var in self.remote_vars.items():
            var.set(value in search_config['remote_types'])
        
        # Load timeframe
        if search_config['publication_timeframes']:
            self.timeframe_var.set(search_config['publication_timeframes'][0])
        
        # Load message
        self.message_text.delete(1.0, tk.END)
        self.message_text.insert(1.0, search_config['application_message'])
        
        # Load excluded keywords
        self.excluded_keywords_var.set(', '.join(search_config['excluded_keywords']))
        
        # Load max applications
        self.max_apps_var.set(str(search_config['max_applications_per_session']))
    
    def start_session(self):
        """Start the application session"""
        # Validate credentials
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please enter your email and password.\n\nYour credentials will be saved automatically as you type.")
            return
        
        # Validate search terms
        search_terms = [term.strip() for term in self.search_terms_text.get(1.0, tk.END).strip().split('\n') if term.strip()]
        if not search_terms:
            messagebox.showerror("Error", "Please enter at least one search term.\n\nYour configuration is saved automatically as you make changes.")
            return
        
        # Load the current configuration (which should be auto-saved)
        search_config = self.config.load_search_config()
        if not search_config['search_terms']:
            messagebox.showerror("Error", "Please configure at least one search term.\n\nYour configuration is saved automatically as you make changes.")
            return
        
        # Close the interface and start the main application
        self.root.destroy()
        
        # Import and run the main application
        from main import main
        main(email, password, search_config, self.config, self.logger)
    
    def show_statistics(self):
        """Show user statistics"""
        email, _ = self.config.load_credentials()
        if not email:
            messagebox.showerror("Error", "No user credentials found")
            return
        
        stats = self.config.load_statistics(email)
        if not stats:
            messagebox.showinfo("Statistics", "No statistics available yet.\nStart your first session to see your progress!")
            return
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Application Statistics")
        stats_window.geometry("500x400")
        
        # Calculate success rate
        success_rate = (stats['successful_applications']/(stats['total_applications'])*100) if stats['total_applications'] > 0 else 0
        
        stats_text = f"""
📊 Application Statistics for {email}

Total Applications: {stats['total_applications']}
✅ Successful: {stats['successful_applications']}
❌ Failed: {stats['failed_applications']}

Success Rate: {success_rate:.1f}%

Last Session: {stats.get('last_session', 'Never')}

Recent Sessions:
"""
        
        for session in stats.get('sessions', [])[-5:]:  # Show last 5 sessions
            stats_text += f"• {session}\n"
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, stats_text)
        text_widget.config(state=tk.DISABLED)
    
    def clear_data(self):
        """Clear all stored data"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all stored data?\n\nThis will remove:\n• Your encrypted credentials\n• Search configuration\n• Application statistics\n• All logs\n\nThis action cannot be undone!"):
            try:
                import shutil
                config_dir = self.config.config_dir
                if config_dir.exists():
                    shutil.rmtree(config_dir)
                messagebox.showinfo("Success", "All data has been cleared successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
    
    def run(self):
        """Run the interface"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FreeWorkInterface()
    app.run() 