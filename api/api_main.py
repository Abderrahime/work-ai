from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from datetime import datetime
import json
import os

# Import existing modules
import sys
sys.path.append('..')
from config import SecureConfig
from logger import SecureLogger
from main import main as run_automation

app = FastAPI(
    title="FreeWork Job Application Assistant API",
    description="API for automated job applications on FreeWork",
    version="1.0.0"
)

# CORS middleware for Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
config_manager = SecureConfig()

# Pydantic models
class Credentials(BaseModel):
    email: str
    password: str

class SearchConfig(BaseModel):
    search_terms: List[str]
    contract_types: List[str]
    remote_types: List[str]
    publication_timeframes: str
    excluded_keywords: List[str]
    application_message: str
    max_applications_per_session: int
    delay_between_applications: int = 2

class JobApplication(BaseModel):
    job_title: str
    company: str
    status: str
    timestamp: datetime
    search_term: str

class ApplicationDetail(BaseModel):
    job_title: str
    company: str
    status: str
    timestamp: datetime
    search_term: str
    contract_type: List[str]
    remote_type: List[str]
    reason: Optional[str] = None

class SessionStatistics(BaseModel):
    session_id: str
    date: datetime
    applications: List[ApplicationDetail]
    total: int
    successful: int
    failed: int
    success_rate: float
    per_search_term: Optional[List[dict]] = None

class Statistics(BaseModel):
    total_applications: int
    successful_applications: int
    failed_applications: int
    success_rate: float
    last_session: Optional[str]
    sessions: List[SessionStatistics]

class SessionStatus(BaseModel):
    status: str
    message: str
    progress: Optional[float] = None
    current_job: Optional[str] = None

class GlobalStatistics(BaseModel):
    total_applications: int
    successful_applications: int
    failed_applications: int
    success_rate: float
    sessions: List[SessionStatistics]
    per_search_term: List[dict]
    per_contract_type: Dict[str, int]
    per_remote_type: Dict[str, int]
    per_day: Dict[str, int]

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        # In a real app, you'd validate JWT tokens
        # For now, we'll use the email as the token
        email = credentials.credentials
        stored_email, _ = config_manager.load_credentials()
        if email != stored_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        return email
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

# Utility function to ensure a value is always a list of strings
def ensure_list(val):
    if isinstance(val, list):
        return [str(v) for v in val]
    if val is None:
        return []
    if isinstance(val, str):
        # Split comma-separated strings, strip whitespace
        return [v.strip() for v in val.split(',') if v.strip()]
    return [str(val)]

# API Routes
@app.get("/")
async def root():
    return {"message": "FreeWork Job Application Assistant API"}

@app.post("/auth/login")
async def login(credentials: Credentials):
    """Save user credentials"""
    try:
        config_manager.save_credentials(credentials.email, credentials.password)
        logger = SecureLogger(credentials.email)
        logger.success("Login successful via API")
        return {"message": "Credentials saved successfully", "email": credentials.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/status")
async def auth_status():
    """Check if user is authenticated"""
    try:
        email, _ = config_manager.load_credentials()
        if email:
            return {"authenticated": True, "email": email}
        return {"authenticated": False}
    except Exception:
        return {"authenticated": False}

@app.get("/config")
async def get_configuration(current_user: str = Depends(get_current_user)):
    """Get current configuration"""
    try:
        search_config = config_manager.load_search_config()
        return search_config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config")
async def save_configuration(
    config: SearchConfig,
    current_user: str = Depends(get_current_user)
):
    """Save configuration"""
    try:
        config_dict = config.dict()
        config_manager.save_search_config(config_dict)
        logger = SecureLogger(current_user)
        logger.success("Configuration saved via API")
        return {"message": "Configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics(current_user: str = Depends(get_current_user)):
    """Get user statistics"""
    try:
        stats = config_manager.load_statistics(current_user)
        if not stats:
            return Statistics(
                total_applications=0,
                successful_applications=0,
                failed_applications=0,
                success_rate=0.0,
                last_session=None,
                sessions=[]
            )
        
        success_rate = (
            (stats['successful_applications'] / stats['total_applications'] * 100)
            if stats['total_applications'] > 0 else 0.0
        )
        
        return Statistics(
            total_applications=stats['total_applications'],
            successful_applications=stats['successful_applications'],
            failed_applications=stats['failed_applications'],
            success_rate=success_rate,
            last_session=stats.get('last_session'),
            sessions=stats.get('sessions', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/start")
async def start_session(current_user: str = Depends(get_current_user)):
    """Start a new application session"""
    try:
        # Validate configuration
        search_config = config_manager.load_search_config()
        if not search_config['search_terms']:
            raise HTTPException(
                status_code=400,
                detail="No search terms configured"
            )
        
        # Start session in background (in production, use Celery or similar)
        # For now, we'll run it synchronously
        logger = SecureLogger(current_user)
        
        # Run the automation
        run_automation(
            email=current_user,
            password=None,  # Will be loaded from config
            search_config=search_config,
            config_manager=config_manager,
            logger=logger
        )
        
        return {"message": "Session completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data")
async def clear_data(current_user: str = Depends(get_current_user)):
    """Clear all stored data"""
    try:
        import shutil
        config_dir = config_manager.config_dir
        if config_dir.exists():
            shutil.rmtree(config_dir)
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics/advanced")
async def get_advanced_statistics(current_user: str = Depends(get_current_user)):
    """Get enhanced user statistics"""
    try:
        # Load user statistics
        stats = config_manager.load_statistics(current_user)
        
        if not stats:
            return GlobalStatistics(
                total_applications=0,
                successful_applications=0,
                failed_applications=0,
                success_rate=0.0,
                sessions=[],
                per_search_term=[],  # Return as list
                per_contract_type={},
                per_remote_type={},
                per_day={}
            )
        
        # Calculate success rate
        success_rate = (
            (stats['successful_applications'] / stats['total_applications'] * 100)
            if stats['total_applications'] > 0 else 0.0
        )
        
        # Process sessions data
        sessions = []
        per_search_term_dict = {}
        per_contract_type = {}
        per_remote_type = {}
        per_day = {}
        
        for session_data in stats.get('sessions', []):
            # Convert session data to SessionStatistics format
            session_stats = SessionStatistics(
                session_id=session_data.get('session_id', 'unknown'),
                date=datetime.fromisoformat(session_data.get('date', datetime.now().isoformat())),
                applications=[],
                total=session_data.get('total', 0),
                successful=session_data.get('successful', 0),
                failed=session_data.get('failed', 0),
                success_rate=session_data.get('success_rate', 0.0)
            )
            
            # Process applications in this session
            for app_data in session_data.get('applications', []):
                app_detail = ApplicationDetail(
                    job_title=app_data.get('job_title', 'Unknown'),
                    company=app_data.get('company', 'Unknown'),
                    status=app_data.get('status', 'unknown'),
                    timestamp=datetime.fromisoformat(app_data.get('timestamp', datetime.now().isoformat())),
                    search_term=app_data.get('search_term', 'unknown'),
                    contract_type=ensure_list(app_data.get('contract_type', [])),
                    remote_type=ensure_list(app_data.get('remote_type', [])),
                    reason=app_data.get('reason')
                )
                session_stats.applications.append(app_detail)
                
                # Aggregate statistics by search term
                search_term = app_data.get('search_term', 'unknown')
                if search_term not in per_search_term_dict:
                    per_search_term_dict[search_term] = {
                        'search_term': search_term,
                        'jobs_found': 0,
                        'jobs_submitted': 0,
                        'jobs_already_applied': 0,
                        'jobs_excluded': 0,
                        'jobs_failed': 0
                    }
                per_search_term_dict[search_term]['jobs_found'] += 1
                if app_data.get('status') == 'submitted':
                    per_search_term_dict[search_term]['jobs_submitted'] += 1
                elif app_data.get('status') == 'already_applied':
                    per_search_term_dict[search_term]['jobs_already_applied'] += 1
                elif app_data.get('status') == 'excluded':
                    per_search_term_dict[search_term]['jobs_excluded'] += 1
                elif app_data.get('status') == 'failed':
                    per_search_term_dict[search_term]['jobs_failed'] += 1
                
                # Aggregate by contract type
                for contract_type in ensure_list(app_data.get('contract_type', [])):
                    per_contract_type[contract_type] = per_contract_type.get(contract_type, 0) + 1
                
                # Aggregate by remote type
                for remote_type in ensure_list(app_data.get('remote_type', [])):
                    per_remote_type[remote_type] = per_remote_type.get(remote_type, 0) + 1
                
                # Aggregate by day
                app_date = datetime.fromisoformat(app_data.get('timestamp', datetime.now().isoformat())).strftime('%Y-%m-%d')
                per_day[app_date] = per_day.get(app_date, 0) + 1
            
            sessions.append(session_stats)
        
        # Convert per_search_term_dict to a list for frontend compatibility
        per_search_term = list(per_search_term_dict.values())
        
        return GlobalStatistics(
            total_applications=stats['total_applications'],
            successful_applications=stats['successful_applications'],
            failed_applications=stats['failed_applications'],
            success_rate=success_rate,
            sessions=sessions,
            per_search_term=per_search_term,
            per_contract_type=per_contract_type,
            per_remote_type=per_remote_type,
            per_day=per_day
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_main:app", host="0.0.0.0", port=port)