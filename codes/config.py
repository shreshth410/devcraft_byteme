"""
Configuration settings for Campus Copilot
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Campus Copilot"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Google API Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/campus_copilot")
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Flask Configuration
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    
    # College-specific Configuration
    COLLEGE_NAME: str = os.getenv("COLLEGE_NAME", "Your College Name")
    COLLEGE_TIMEZONE: str = os.getenv("COLLEGE_TIMEZONE", "America/New_York")
    
    # Webhook Configuration
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8443"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/campus_copilot.log")
    
    # AI/NLP Configuration
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        return True
        
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration as dictionary"""
        return {
            "url": cls.DATABASE_URL,
        }
        
    @classmethod
    def get_google_config(cls) -> dict:
        """Get Google API configuration as dictionary"""
        return {
            "client_id": cls.GOOGLE_CLIENT_ID,
            "client_secret": cls.GOOGLE_CLIENT_SECRET,
            "redirect_uri": cls.GOOGLE_REDIRECT_URI,
        }
        
    @classmethod
    def get_pinecone_config(cls) -> dict:
        """Get Pinecone configuration as dictionary"""
        return {
            "api_key": cls.PINECONE_API_KEY,
            "environment": cls.PINECONE_ENVIRONMENT,
        }


# Create global config instance
config = Config()


def get_config() -> Config:
    """Get configuration instance"""
    return config

