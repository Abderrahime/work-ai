import logging
import os
from datetime import datetime
from pathlib import Path
import json

class SecureLogger:
    def __init__(self, user_email=None):
        self.user_email = user_email
        self.log_dir = Path.home() / ".freework_app" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('FreeWorkApp')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # File handler for all logs
        log_file = self.log_dir / f"freework_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler for user-friendly messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter('%(message)s')
        
        file_handler.setFormatter(file_formatter)
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _sanitize_message(self, message):
        """Remove sensitive information from log messages"""
        sensitive_words = ['password', 'email', 'credential', 'token', 'key']
        sanitized = message
        
        for word in sensitive_words:
            if word in message.lower():
                sanitized = sanitized.replace(word, '[REDACTED]')
        
        return sanitized
    
    def info(self, message):
        """Log info message"""
        sanitized_message = self._sanitize_message(message)
        self.logger.info(sanitized_message)
    
    def warning(self, message):
        """Log warning message"""
        sanitized_message = self._sanitize_message(message)
        self.logger.warning(sanitized_message)
    
    def error(self, message):
        """Log error message"""
        sanitized_message = self._sanitize_message(message)
        self.logger.error(sanitized_message)
    
    def success(self, message):
        """Log success message with special formatting"""
        sanitized_message = self._sanitize_message(message)
        self.logger.info(f"✅ {sanitized_message}")
    
    def application_log(self, job_title, company, status, search_term):
        """Log application attempt with details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_email': self.user_email,
            'job_title': job_title,
            'company': company,
            'status': status,
            'search_term': search_term
        }
        
        # Save to application log file
        app_log_file = self.log_dir / "applications.json"
        applications = []
        
        if app_log_file.exists():
            with open(app_log_file, 'r') as f:
                applications = json.load(f)
        
        applications.append(log_entry)
        
        with open(app_log_file, 'w') as f:
            json.dump(applications, f, indent=2)
        
        # Log to main log
        status_emoji = "✅" if status == "success" else "❌"
        self.logger.info(f"{status_emoji} Application: {job_title} at {company} ({search_term})")
    
    def session_start(self, search_config):
        """Log session start"""
        self.logger.info("🚀 Starting new application session")
        self.logger.info(f"📋 Search terms: {', '.join(search_config['search_terms'])}")
        self.logger.info(f"📄 Contract types: {', '.join(search_config['contract_types'])}")
        self.logger.info(f"🏠 Remote types: {', '.join(search_config['remote_types'])}")
    
    def session_end(self, stats):
        """Log session end with statistics"""
        self.logger.info("🏁 Session completed")
        self.logger.info(f"📊 Applications submitted: {stats['successful_applications']}")
        self.logger.info(f"❌ Failed applications: {stats['failed_applications']}")
        total = stats['successful_applications'] + stats['failed_applications']
        if total > 0:
            success_rate = (stats['successful_applications'] / total) * 100
        else:
            success_rate = 0
        self.logger.info(f"📈 Success rate: {success_rate:.1f}%") 