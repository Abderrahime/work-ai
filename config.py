import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64

class SecureConfig:
    def __init__(self):
        self.config_dir = Path.home() / ".freework_app"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.key"
        self.stats_file = self.config_dir / "statistics.json"
        self._load_or_create_key()
        
    def _load_or_create_key(self):
        """Load existing encryption key or create a new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)
    
    def _encrypt(self, data):
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data):
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def save_credentials(self, email, password):
        """Securely save user credentials"""
        config = {
            'email': self._encrypt(email),
            'password': self._encrypt(password),
            'created_at': str(Path().stat().st_mtime)
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_credentials(self):
        """Load and decrypt user credentials"""
        if not self.config_file.exists():
            return None, None
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        try:
            email = self._decrypt(config['email'])
            password = self._decrypt(config['password'])
            return email, password
        except Exception as e:
            print(f"Error decrypting credentials: {e}")
            return None, None
    
    def save_search_config(self, search_config):
        """Save search configuration"""
        config = self.load_full_config()
        config['search_config'] = search_config
        self._save_full_config(config)
    
    def load_search_config(self):
        """Load search configuration"""
        config = self.load_full_config()
        return config.get('search_config', self.get_default_search_config())
    
    def load_full_config(self):
        """Load full configuration"""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _save_full_config(self, config):
        """Save full configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_default_search_config(self):
        """Get default search configuration"""
        return {
            'search_terms': ['java', 'angular', 'react', 'python'],
            'contract_types': ['permanent', 'contractor', 'fixed-term'],
            'remote_types': ['partial', 'full'],
            'publication_timeframes': ['less_than_24_hours', 'less_than_7_days', 'less_than_30_days'],
            'excluded_keywords': ['banc', 'assurance'],
            'application_message': """Bonjour,\n\nJe suis vivement intéressé par cette mission qui correspond parfaitement à mes compétences.\n\nCordialement""",
            'max_applications_per_session': 50,
            'delay_between_applications': 2
        }
    
    def save_statistics(self, user_email, stats):
        """Save user statistics"""
        if not self.stats_file.exists():
            all_stats = {}
        else:
            with open(self.stats_file, 'r') as f:
                all_stats = json.load(f)
        
        if user_email not in all_stats:
            all_stats[user_email] = {
                'total_applications': 0,
                'successful_applications': 0,
                'failed_applications': 0,
                'sessions': [],
                'last_session': None
            }
        
        all_stats[user_email].update(stats)
        
        with open(self.stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
    
    def load_statistics(self, user_email):
        """Load user statistics"""
        if not self.stats_file.exists():
            return None
        
        with open(self.stats_file, 'r') as f:
            all_stats = json.load(f)
        
        return all_stats.get(user_email, None) 