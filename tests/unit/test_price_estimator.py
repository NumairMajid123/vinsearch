import pytest
from services.price_estimator import PriceEstimator
from data.models import Vehicle


class TestPriceEstimator:
    
    def test_estimate_price_no_vehicles(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = []
        
        price, metadata = estimator.estimate_price(vehicles)
        
        assert price == 0.0
        assert metadata['method'] == 'no_data'
        assert metadata['vehicle_count'] == 0
    
    def test_estimate_price_no_valid_prices(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = [
            Vehicle(listing_price=None, listing_mileage=100000),
            Vehicle(listing_price=None, listing_mileage=120000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles)
        
        assert price == 0.0
        assert metadata['method'] == 'no_valid_prices'
        assert metadata['vehicle_count'] == 0
    
    def test_estimate_price_average_only(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = [
            Vehicle(listing_price=10000.0, listing_mileage=100000),
            Vehicle(listing_price=12000.0, listing_mileage=120000),
            Vehicle(listing_price=11000.0, listing_mileage=110000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles)
        
        assert price == 11000.0  # Average rounded to nearest 100
        assert metadata['method'] == 'average'
        assert metadata['vehicle_count'] == 3
        assert metadata['base_price'] == 11000.0
    
    def test_estimate_price_with_mileage_regression(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = [
            Vehicle(listing_price=15000.0, listing_mileage=50000),
            Vehicle(listing_price=14000.0, listing_mileage=75000),
            Vehicle(listing_price=13000.0, listing_mileage=100000),
            Vehicle(listing_price=12000.0, listing_mileage=125000),
            Vehicle(listing_price=11000.0, listing_mileage=150000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles, mileage=80000)
        
        assert price > 0
        assert metadata['method'] == 'regression'
        assert metadata['regression_vehicles'] == 5
        assert metadata['target_mileage'] == 80000
        assert 'slope' in metadata
        assert 'intercept' in metadata
        assert 'r_squared' in metadata
    
    def test_estimate_price_insufficient_regression_data(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = [
            Vehicle(listing_price=15000.0, listing_mileage=50000),
            Vehicle(listing_price=14000.0, listing_mileage=75000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles, mileage=80000)
        
        # Should fall back to average method
        assert price == 14500.0  # Average rounded to nearest 100
        assert metadata['method'] == 'average'
        assert metadata['regression'] == 'insufficient_data'
    
    def test_validate_mileage_valid(self, mock_config):
        estimator = PriceEstimator(mock_config)
        
        result = estimator.validate_mileage("150,000")
        assert result == 150000
        
        result = estimator.validate_mileage("75000")
        assert result == 75000
        
        result = estimator.validate_mileage(" 100000 ")
        assert result == 100000
    
    def test_validate_mileage_invalid(self, mock_config):
        estimator = PriceEstimator(mock_config)
        
        # Invalid format
        assert estimator.validate_mileage("abc") is None
        assert estimator.validate_mileage("") is None
        assert estimator.validate_mileage("   ") is None
        
        # Out of range
        assert estimator.validate_mileage("-1000") is None
        assert estimator.validate_mileage("600000") is None  # Above MAX_MILEAGE
    
    def test_validate_mileage_edge_cases(self, mock_config):
        estimator = PriceEstimator(mock_config)
        
        # Edge cases
        assert estimator.validate_mileage("0") == 0
        assert estimator.validate_mileage("500000") == 500000  # MAX_MILEAGE
        assert estimator.validate_mileage("500001") is None  # Above MAX_MILEAGE
    
    def test_regression_calculation_accuracy(self, mock_config):
        estimator = PriceEstimator(mock_config)
        
        # Create a perfect linear relationship
        vehicles = [
            Vehicle(listing_price=20000.0, listing_mileage=0),
            Vehicle(listing_price=18000.0, listing_mileage=20000),
            Vehicle(listing_price=16000.0, listing_mileage=40000),
            Vehicle(listing_price=14000.0, listing_mileage=60000),
            Vehicle(listing_price=12000.0, listing_mileage=80000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles, mileage=30000)
        
        # Should predict 17000 (20000 - 0.1 * 30000)
        assert abs(price - 17000) <= 100  # Allow for rounding
        assert metadata['r_squared'] > 0.99  # Perfect correlation
        assert metadata['slope'] < 0  # Negative slope (price decreases with mileage)
    
    def test_price_rounding(self, mock_config):
        estimator = PriceEstimator(mock_config)
        vehicles = [
            Vehicle(listing_price=12345.0, listing_mileage=100000),
            Vehicle(listing_price=12355.0, listing_mileage=110000)
        ]
        
        price, metadata = estimator.estimate_price(vehicles)
        
        # Should round to nearest 100
        # Average is 12350, but rounding to nearest 100 gives 12400
        assert price == 12400.0
        assert price % 100 == 0 