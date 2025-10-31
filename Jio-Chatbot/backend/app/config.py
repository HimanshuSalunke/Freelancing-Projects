import os
from pathlib import Path
from typing import Dict

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent.parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env file on module import
load_env_file()

# ============================================================================
# COMPANY CONFIGURATION
# ============================================================================
# All company-specific details are now configurable via environment variables
# Defaults to "TechCorp Solutions" for demo/development purposes

def get_company_name() -> str:
    """Get the company name (replaces hardcoded references)"""
    return os.getenv("COMPANY_NAME", "TechCorp Solutions")

def get_app_name() -> str:
    """Get the application name"""
    return os.getenv("APP_NAME", "TechCorp HR Assistant")

def get_company_subtitle() -> str:
    """Get the company subtitle/tagline"""
    return os.getenv("COMPANY_SUBTITLE", "Enterprise Software & HR Solutions Provider")

def get_company_address() -> str:
    """Get the company registered address"""
    return os.getenv("COMPANY_ADDRESS", "123 Business Park, Tech District, Mumbai - 400001")

def get_company_phone() -> str:
    """Get the company phone number"""
    return os.getenv("COMPANY_PHONE", "+91-22-1234-5678")

def get_company_email() -> str:
    """Get the company email address"""
    return os.getenv("COMPANY_EMAIL", "hr@techcorp.com")

def get_company_website() -> str:
    """Get the company website"""
    return os.getenv("COMPANY_WEBSITE", "www.techcorp.com")

def get_company_cin() -> str:
    """Get the company CIN (Corporate Identity Number) - optional"""
    return os.getenv("COMPANY_CIN", "")

def get_company_gst() -> str:
    """Get the company GST number - optional"""
    return os.getenv("COMPANY_GST", "")

def get_company_config() -> Dict[str, str]:
    """Get all company configuration as a dictionary"""
    return {
        "name": get_company_name(),
        "app_name": get_app_name(),
        "subtitle": get_company_subtitle(),
        "address": get_company_address(),
        "phone": get_company_phone(),
        "email": get_company_email(),
        "website": get_company_website(),
        "cin": get_company_cin(),
        "gst": get_company_gst(),
    }

# ============================================================================
# AUTHENTICATION & SECURITY
# ============================================================================

def auth_disabled() -> bool:
    """Check if authentication is disabled (for development only)"""
    return os.getenv("DISABLE_AUTH", "false").strip().lower() in {"1", "true", "yes"}

# ============================================================================
# DATABASE & EXTERNAL SERVICES
# ============================================================================

def get_mongodb_uri() -> str:
    """Get MongoDB connection URI"""
    return os.getenv("MONGODB_URI", "")

def get_gemini_api_key() -> str:
    """Get Google Gemini API key"""
    return os.getenv("GOOGLE_GEMINI_API_KEY", "")

# Backward compatibility aliases (deprecated - use get_company_name() instead)
def org_name() -> str:
    """Deprecated: Use get_company_name() instead"""
    return get_company_name()


