import pytest
import tempfile
import os
from flask import Flask, request, render_template, flash
from data.models import db, Vehicle
from config import TestingConfig
from services.vehicle_service import VehicleService
from services.price_estimator import PriceEstimator


def create_mock_config():
    config = {
        "MIN_YEAR": 1980,
        "MAX_YEAR": 2030,
        "MAX_MILEAGE": 500000,
        "MIN_VEHICLES_FOR_REGRESSION": 3,
        "MAX_LISTINGS_DISPLAY": 100,
        "PRICE_ROUNDING_FACTOR": 100,
        "INVENTORY_DATA_URL": "https://test.example.com/data.txt",
    "DATA_IMPORT_TIMEOUT": 30
}
    
    return config


@pytest.fixture
def app():
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = Flask(__name__)
    app.config.from_object(TestingConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize the database
    db.init_app(app)
    
    # Register routes for testing
    @app.route("/", methods=["GET", "POST"])
    def index():
        """Main search route for testing."""
        if request.method == "POST":
            # Extract form data
            year = request.form.get("year", "").strip()
            make = request.form.get("make", "").strip()
            model = request.form.get("model", "").strip()
            mileage = request.form.get("mileage", "").strip()
            
            # Basic validation
            if not (year and make and model):
                flash("Year, Make, and Model are required fields.")
                return f"Search Page - Error: Year, Make, and Model are required fields. Year: {year}, Make: {make}, Model: {model}, Mileage: {mileage}"
            
            # Validate year format
            try:
                year_int = int(year)
            except ValueError:
                flash("Year must be a valid number.")
                return f"Search Page - Error: Year must be a valid number. Year: {year}, Make: {make}, Model: {model}, Mileage: {mileage}"
            
            # Validate year range
            mock_config = create_mock_config()
            if year_int < mock_config["MIN_YEAR"] or year_int > mock_config["MAX_YEAR"]:
                flash(f"Year must be between {mock_config["MIN_YEAR"]} and {mock_config["MAX_YEAR"]}.")
                return f"Search Page - Error: Year must be between {mock_config["MIN_YEAR"]} and {mock_config["MAX_YEAR"]}. Year: {year}, Make: {make}, Model: {model}, Mileage: {mileage}"
            
            # Search for vehicles
            vehicle_service = VehicleService(create_mock_config())
            vehicles = vehicle_service.search_vehicles(year_int, make, model)
            
            if not vehicles:
                flash(f"No vehicles found for {year} {make} {model}")
                return f"Search Page - Error: No vehicles found for {year} {make} {model}. Year: {year}, Make: {make}, Model: {model}, Mileage: {mileage}"
            
            # Estimate price
            price_estimator = PriceEstimator(create_mock_config())
            parsed_mileage = None
            if mileage:
                parsed_mileage = price_estimator.validate_mileage(mileage)
                if parsed_mileage is None:
                    flash("Invalid mileage format. Please enter a valid number.")
                    return f"Search Page - Error: Invalid mileage format. Year: {year}, Make: {make}, Model: {model}, Mileage: {mileage}"
            
            estimated_price, _ = price_estimator.estimate_price(vehicles, parsed_mileage)
            listings = vehicle_service.get_sample_listings(vehicles)
            
            return f"Results Page - Vehicle: {year} {make} {model}, Mileage: {mileage}, Price: ${estimated_price}, Listings: {len(listings)}"
        
        return "Search Page - Year: , Make: , Model: , Mileage: "
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_vehicles():
    """Sample vehicle data for testing."""
    return [
        {
            'vin': '1HGBH41JXMN109186',
            'year': 2015,
            'make': 'toyota',
            'model': 'camry',
            'city': 'Seattle',
            'state': 'WA',
            'listing_price': 13500.0,
            'listing_mileage': 125000
        },
        {
            'vin': '1HGBH41JXMN109187',
            'year': 2015,
            'make': 'toyota',
            'model': 'camry',
            'city': 'Dallas',
            'state': 'TX',
            'listing_price': 14200.0,
            'listing_mileage': 98000
        },
        {
            'vin': '1HGBH41JXMN109188',
            'year': 2015,
            'make': 'toyota',
            'model': 'camry',
            'city': 'Newark',
            'state': 'NJ',
            'listing_price': 15800.0,
            'listing_mileage': 75000
        },
        {
            'vin': '1HGBH41JXMN109189',
            'year': 2015,
            'make': 'toyota',
            'model': 'camry',
            'city': 'Chicago',
            'state': 'IL',
            'listing_price': 12900.0,
            'listing_mileage': 150000
        },
        {
            'vin': '1HGBH41JXMN109190',
            'year': 2015,
            'make': 'toyota',
            'model': 'camry',
            'city': 'Miami',
            'state': 'FL',
            'listing_price': 16500.0,
            'listing_mileage': 65000
        }
    ]


@pytest.fixture
def populated_db(app, sample_vehicles):
    with app.app_context():
        for vehicle_data in sample_vehicles:
            vehicle = Vehicle(**vehicle_data)
            db.session.add(vehicle)
        db.session.commit()
        return app


@pytest.fixture
def mock_config():
    return create_mock_config() 