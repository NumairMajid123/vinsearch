import pytest
from unittest.mock import patch, MagicMock
from scripts.data_importer import DataImporter
from data.models import Vehicle, db


class TestDataImporter:
    
    def test_import_inventory_data_success(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        csv_data = """vin|year|make|model|dealer_city|dealer_state|listing_price|listing_mileage
1HGBH41JXMN109186|2015|toyota|camry|Seattle|WA|13500|125000
1HGBH41JXMN109187|2015|toyota|camry|Dallas|TX|14200|98000"""
        
        with patch('scripts.data_importer.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = csv_data
            mock_get.return_value = mock_response
            
            with app.app_context():
                success = importer.import_inventory_data(app)
                
                assert success is True
                
                vehicles = Vehicle.query.all()
                assert len(vehicles) == 2
                
                vehicle1 = vehicles[0]
                assert vehicle1.vin == '1HGBH41JXMN109186'
                assert vehicle1.year == 2015
                assert vehicle1.make == 'toyota'
                assert vehicle1.model == 'camry'
                assert vehicle1.city == 'Seattle'
                assert vehicle1.state == 'WA'
                assert vehicle1.listing_price == 13500.0
                assert vehicle1.listing_mileage == 125000
    
    def test_import_inventory_data_download_failure(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        with patch('scripts.data_importer.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            with app.app_context():
                success = importer.import_inventory_data(app)
                
                assert success is False
    
    def test_import_inventory_data_network_error(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        with patch('scripts.data_importer.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            with app.app_context():
                success = importer.import_inventory_data(app)
                
                assert success is False
    
    def test_import_inventory_data_invalid_row(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        # Mock CSV data with invalid row
        csv_data = """vin|year|make|model|dealer_city|dealer_state|listing_price|listing_mileage
1HGBH41JXMN109186|2015|toyota|camry|Seattle|WA|13500|125000
INVALID_ROW|abc|toyota|camry|Seattle|WA|invalid|invalid
1HGBH41JXMN109187|2015|toyota|camry|Dallas|TX|14200|98000"""
        
        with patch('scripts.data_importer.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = csv_data
            mock_get.return_value = mock_response
            
            with app.app_context():
                success = importer.import_inventory_data(app)
                
                assert success is True
                
                vehicles = Vehicle.query.all()
                assert len(vehicles) == 2
    
    def test_import_inventory_data_missing_fields(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        # Mock CSV data with missing fields
        csv_data = """vin|year|make|model|dealer_city|dealer_state|listing_price|listing_mileage
1HGBH41JXMN109186|2015|toyota|camry|Seattle|WA||125000
1HGBH41JXMN109187|2015|toyota|camry|Dallas|TX|14200|
1HGBH41JXMN109188||toyota|camry|Seattle|WA|13500|125000"""
        
        with patch('scripts.data_importer.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = csv_data
            mock_get.return_value = mock_response
            
            with app.app_context():
                success = importer.import_inventory_data(app)
                
                assert success is True
                
                # Check that vehicles with missing data are handled properly
                vehicles = Vehicle.query.all()
                assert len(vehicles) == 2  # Only 2 valid vehicles (missing year row is skipped)
                
                # Check that missing prices are None
                vehicle1 = vehicles[0]
                assert vehicle1.listing_price is None
                assert vehicle1.listing_mileage == 125000
                
                # Check that missing mileage is None
                vehicle2 = vehicles[1]
                assert vehicle2.listing_price == 14200.0
                assert vehicle2.listing_mileage is None
    
    def test_import_inventory_data_already_exists(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        with app.app_context():
            existing_vehicle = Vehicle(
                vin='EXISTING123',
                year=2015,
                make='toyota',
                model='camry',
                city='Test',
                state='TS',
                listing_price=10000.0,
                listing_mileage=100000
            )
            db.session.add(existing_vehicle)
            db.session.commit()
            
            success = importer.import_inventory_data(app)
            
            assert success is True
            
            vehicles = Vehicle.query.all()
            assert len(vehicles) == 1
    
    def test_parse_float_valid(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        assert importer._parse_float("123.45") == 123.45
        assert importer._parse_float("1000") == 1000.0
        assert importer._parse_float("0") == 0.0
    
    def test_parse_float_invalid(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        assert importer._parse_float("") is None
        assert importer._parse_float("abc") is None
        assert importer._parse_float("   ") is None
        assert importer._parse_float(None) is None
    
    def test_parse_int_valid(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        assert importer._parse_int("123") == 123
        assert importer._parse_int("0") == 0
        assert importer._parse_int("100000") == 100000
    
    def test_parse_int_invalid(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        assert importer._parse_int("") is None
        assert importer._parse_int("abc") is None
        assert importer._parse_int("123.45") is None
        assert importer._parse_int("   ") is None
        assert importer._parse_int(None) is None
    
    def test_create_vehicle_from_row_valid(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        row = {
            'vin': '1HGBH41JXMN109186',
            'year': '2015',
            'make': 'toyota',
            'model': 'camry',
            'dealer_city': 'Seattle',
            'dealer_state': 'WA',
            'listing_price': '13500',
            'listing_mileage': '125000'
        }
        
        vehicle = importer._create_vehicle_from_row(row)
        
        assert vehicle is not None
        assert vehicle.vin == '1HGBH41JXMN109186'
        assert vehicle.year == 2015
        assert vehicle.make == 'toyota'
        assert vehicle.model == 'camry'
        assert vehicle.city == 'Seattle'
        assert vehicle.state == 'WA'
        assert vehicle.listing_price == 13500.0
        assert vehicle.listing_mileage == 125000
    
    def test_create_vehicle_from_row_missing_required(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        row = {
            'vin': '',
            'year': '2015',
            'make': 'toyota',
            'model': 'camry',
            'dealer_city': 'Seattle',
            'dealer_state': 'WA',
            'listing_price': '13500',
            'listing_mileage': '125000'
        }
        
        vehicle = importer._create_vehicle_from_row(row)
        assert vehicle is None
        
        row = {
            'vin': '1HGBH41JXMN109186',
            'year': '',
            'make': 'toyota',
            'model': 'camry',
            'dealer_city': 'Seattle',
            'dealer_state': 'WA',
            'listing_price': '13500',
            'listing_mileage': '125000'
        }
        
        vehicle = importer._create_vehicle_from_row(row)
        assert vehicle is None
        
        row = {
            'vin': '1HGBH41JXMN109186',
            'year': '2015',
            'make': '',
            'model': 'camry',
            'dealer_city': 'Seattle',
            'dealer_state': 'WA',
            'listing_price': '13500',
            'listing_mileage': '125000'
        }
        
        vehicle = importer._create_vehicle_from_row(row)
        assert vehicle is None
    
    def test_create_vehicle_from_row_invalid_year(self, app, mock_config):
        importer = DataImporter(mock_config)
        
        row = {
            'vin': '1HGBH41JXMN109186',
            'year': 'abc',
            'make': 'toyota',
            'model': 'camry',
            'dealer_city': 'Seattle',
            'dealer_state': 'WA',
            'listing_price': '13500',
            'listing_mileage': '125000'
        }
        
        vehicle = importer._create_vehicle_from_row(row)
        assert vehicle is None 