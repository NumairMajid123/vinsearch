import pytest
from flask import url_for


class TestSearchFlow:
    
    def test_search_page_loads(self, client):
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Search Page' in response.data
        assert b'Year:' in response.data
        assert b'Make:' in response.data
        assert b'Model:' in response.data
        assert b'Mileage:' in response.data
    
    def test_search_with_valid_data(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': '125000'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'2015 Toyota Camry' in response.data
        assert b'$13' in response.data  # Estimated price
        assert b'Listings: 5' in response.data
    
    def test_search_without_mileage(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'2015 Toyota Camry' in response.data
        assert b'Listings: 5' in response.data
    
    def test_search_missing_required_fields(self, client):
        response = client.post('/', data={
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Year, Make, and Model are required fields' in response.data
        
        response = client.post('/', data={
            'year': '2015',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Year, Make, and Model are required fields' in response.data
        
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota'
        })
        
        assert response.status_code == 200
        assert b'Year, Make, and Model are required fields' in response.data
    
    def test_search_invalid_year(self, client):
        response = client.post('/', data={
            'year': 'abc',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Year must be a valid number' in response.data
    
    def test_search_year_out_of_range(self, client):
        response = client.post('/', data={
            'year': '1970',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Year must be between 1980 and 2030' in response.data
        
        response = client.post('/', data={
            'year': '2040',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Year must be between 1980 and 2030' in response.data
    
    def test_search_invalid_mileage(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': 'abc'
        })
        
        assert response.status_code == 200
        assert b'Invalid mileage format' in response.data
    
    def test_search_mileage_out_of_range(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': '600000'
        })
        
        assert response.status_code == 200
        assert b'Invalid mileage format' in response.data
        
        # Negative mileage
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': '-1000'
        })
        
        assert response.status_code == 200
        assert b'Invalid mileage format' in response.data
    
    def test_search_vehicle_not_found(self, client, populated_db):
        response = client.post('/', data={
            'year': '2020',
            'make': 'Tesla',
            'model': 'Model S'
        })
        
        assert response.status_code == 200
        assert b'No vehicles found for 2020 Tesla Model S' in response.data
    
    def test_search_results_display(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'2015 Toyota Camry' in response.data
        assert b'Listings: 5' in response.data
    
    def test_search_with_mileage_adjustment(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': '100000'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'100000' in response.data  # User input mileage
    
    def test_search_form_persistence(self, client):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': 'abc'  # Invalid mileage
        })
        
        assert response.status_code == 200
        assert b'Year: 2015' in response.data
        assert b'Make: Toyota' in response.data
        assert b'Model: Camry' in response.data
        assert b'Mileage: abc' in response.data
    
    def test_new_search_link(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Search Page' in response.data
    
    def test_search_case_insensitive(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'TOYOTA',
            'model': 'CAMRY'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'2015 TOYOTA CAMRY' in response.data
    
    def test_search_whitespace_handling(self, client, populated_db):
        response = client.post('/', data={
            'year': '  2015  ',
            'make': '  Toyota  ',
            'model': '  Camry  '
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'2015 Toyota Camry' in response.data
    
    def test_mileage_format_handling(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry',
            'mileage': '150,000'
        })
        
        assert response.status_code == 200
        assert b'Results Page' in response.data
        assert b'150,000' in response.data
    
    def test_price_rounding(self, client, populated_db):
        response = client.post('/', data={
            'year': '2015',
            'make': 'Toyota',
            'model': 'Camry'
        })
        
        assert response.status_code == 200
        
        assert b'$' in response.data
    
    def test_error_handling(self, client):
        response = client.post('/', data={
            'year': '',
            'make': '',
            'model': ''
        })
        
        assert response.status_code == 200
        assert b'Year, Make, and Model are required fields' in response.data 