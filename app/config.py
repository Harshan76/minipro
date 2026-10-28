import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(basedir, '..'))
load_dotenv(os.path.join(project_root, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key_college_ai_team_builder_2026'
    
    # Database configuration
    # Supports MySQL via pymysql: mysql+pymysql://user:password@localhost:3306/teambuilder_db
    # Seamless fallback to SQLite for easy evaluation if MySQL is not available
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(project_root, 'teambuilder.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True
    }

    # Model save directory
    MODEL_DIR = os.path.join(project_root, 'saved_models')
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Algorithm Default Normalized Weights
    WEIGHT_SKILL = float(os.environ.get('WEIGHT_SKILL', 0.40))
    WEIGHT_INTEREST = float(os.environ.get('WEIGHT_INTEREST', 0.20))
    WEIGHT_EXPERIENCE = float(os.environ.get('WEIGHT_EXPERIENCE', 0.15))
    WEIGHT_AVAILABILITY = float(os.environ.get('WEIGHT_AVAILABILITY', 0.15))
    WEIGHT_ROLE = float(os.environ.get('WEIGHT_ROLE', 0.10))
