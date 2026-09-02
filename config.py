import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/car_value_project_db_5'
    )

    # Data Import Configuration
    INVENTORY_DATA_URL = os.getenv(
        'INVENTORY_DATA_URL',
        'https://linkgrid.com/downloads/carvalue_project/inventory-listing-2022-08-17_first1000.txt'
    )
    DATA_IMPORT_TIMEOUT = int(os.getenv('DATA_IMPORT_TIMEOUT', '30'))

    # Application Configuration
    MAX_LISTINGS_DISPLAY = int(os.getenv('MAX_LISTINGS_DISPLAY', '100'))
    PRICE_ROUNDING_FACTOR = int(os.getenv('PRICE_ROUNDING_FACTOR', '100'))
    MIN_VEHICLES_FOR_REGRESSION = int(os.getenv('MIN_VEHICLES_FOR_REGRESSION', '2'))

    # Validation Configuration
    MIN_YEAR = int(os.getenv('MIN_YEAR', '1920'))
    MAX_YEAR = int(os.getenv('MAX_YEAR', '2025'))
    MAX_MILEAGE = int(os.getenv('MAX_MILEAGE', '500000'))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
