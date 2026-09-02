import pytest
from services.vehicle_service import VehicleService
from data.models import Vehicle, db


class TestVehicleService:
    
    def test_search_vehicles_found(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        
        vehicles = service.search_vehicles(2015, "Toyota", "Camry")
        
        assert len(vehicles) == 5
        for vehicle in vehicles:
            assert vehicle.year == 2015
            assert vehicle.make == "toyota"
            assert vehicle.model == "camry"
    
    def test_search_vehicles_not_found(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        
        vehicles = service.search_vehicles(2020, "Tesla", "Model S")
        
        assert len(vehicles) == 0
    
    def test_search_vehicles_case_insensitive(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        
        vehicles = service.search_vehicles(2015, "TOYOTA", "CAMRY")
        
        assert len(vehicles) == 5
        for vehicle in vehicles:
            assert vehicle.make == "toyota"  # Stored in lowercase
            assert vehicle.model == "camry"
    
    def test_search_vehicles_whitespace_handling(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        
        vehicles = service.search_vehicles(2015, "  Toyota  ", "  Camry  ")
        
        assert len(vehicles) == 5
    
    def test_get_sample_listings(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        vehicles = service.search_vehicles(2015, "Toyota", "Camry")
        
        listings = service.get_sample_listings(vehicles)
        
        assert len(listings) == 5
        for listing in listings:
            assert 'id' in listing
            assert 'vehicle' in listing
            assert 'price' in listing
            assert 'mileage' in listing
            assert 'location' in listing
            assert listing['vehicle'] == "2015 toyota camry"  # Fixed case expectation
    
    def test_get_sample_listings_limit(self, populated_db, mock_config):
        with populated_db.app_context():
            for i in range(150):  # More than MAX_LISTINGS_DISPLAY (100)
                vehicle = Vehicle(
                    vin=f'TEST{i}',
                    year=2015,
                    make='toyota',
                    model='camry',
                    city='Test City',
                    state='TS',
                    listing_price=10000.0 + i,
                    listing_mileage=100000 + i
                )
                db.session.add(vehicle)
            db.session.commit()
        
        service = VehicleService(mock_config)
        vehicles = service.search_vehicles(2015, "Toyota", "Camry")
        
        listings = service.get_sample_listings(vehicles)
        
        assert len(listings) <= mock_config["MAX_LISTINGS_DISPLAY"]
    
    def test_validate_search_input_valid(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("2015", "Toyota", "Camry")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_search_input_missing_year(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("", "Toyota", "Camry")
        
        assert is_valid is False
        assert error == "Year is required"
    
    def test_validate_search_input_missing_make(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("2015", "", "Camry")
        
        assert is_valid is False
        assert error == "Make is required"
    
    def test_validate_search_input_missing_model(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("2015", "Toyota", "")
        
        assert is_valid is False
        assert error == "Model is required"
    
    def test_validate_search_input_invalid_year_format(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("abc", "Toyota", "Camry")
        
        assert is_valid is False
        assert error == "Year must be a valid number"
    
    def test_validate_search_input_year_too_old(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("1970", "Toyota", "Camry")
        
        assert is_valid is False
        assert error == "Year must be between 1980 and 2030"
    
    def test_validate_search_input_year_too_new(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("2040", "Toyota", "Camry")
        
        assert is_valid is False
        assert error == "Year must be between 1980 and 2030"
    
    def test_validate_search_input_whitespace_handling(self, mock_config):
        service = VehicleService(mock_config)
        
        is_valid, error = service.validate_search_input("  2015  ", "  Toyota  ", "  Camry  ")
        
        assert is_valid is True
        assert error is None
    
    def test_get_vehicle_statistics_empty(self, mock_config):
        service = VehicleService(mock_config)
        
        stats = service.get_vehicle_statistics([])
        
        assert stats['total_vehicles'] == 0
        assert stats['vehicles_with_prices'] == 0
        assert stats['vehicles_with_mileage'] == 0
        assert stats['price_range'] is None
        assert stats['mileage_range'] is None
    
    def test_get_vehicle_statistics_with_data(self, populated_db, mock_config):
        service = VehicleService(mock_config)
        vehicles = service.search_vehicles(2015, "Toyota", "Camry")
        
        stats = service.get_vehicle_statistics(vehicles)
        
        assert stats['total_vehicles'] == 5
        assert stats['vehicles_with_prices'] == 5
        assert stats['vehicles_with_mileage'] == 5
        assert stats['price_range'] is not None
        assert stats['mileage_range'] is not None
        assert 'min' in stats['price_range']
        assert 'max' in stats['price_range']
        assert 'avg' in stats['price_range']
        assert 'min' in stats['mileage_range']
        assert 'max' in stats['mileage_range']
        assert 'avg' in stats['mileage_range']
    
    def test_get_vehicle_statistics_partial_data(self, mock_config):
        service = VehicleService(mock_config)
        vehicles = [
            Vehicle(listing_price=10000.0, listing_mileage=100000),
            Vehicle(listing_price=None, listing_mileage=120000),
            Vehicle(listing_price=12000.0, listing_mileage=None),
            Vehicle(listing_price=None, listing_mileage=None)
        ]
        
        stats = service.get_vehicle_statistics(vehicles)
        
        assert stats['total_vehicles'] == 4
        assert stats['vehicles_with_prices'] == 2
        assert stats['vehicles_with_mileage'] == 2
        assert stats['price_range'] is not None
        assert stats['mileage_range'] is not None 