import logging
import requests
import csv
from io import StringIO
from typing import Optional, Dict, Any
from data.models import db, Vehicle

logger = logging.getLogger(__name__)

class DataImporter:    
    def __init__(self, config):
        self.config = config
        self.data_url = config["INVENTORY_DATA_URL"]
        self.timeout = config["DATA_IMPORT_TIMEOUT"]
    
    def import_inventory_data(self, app) -> bool:
        try:
            logger.info("Starting inventory data import")
            
            with app.app_context():
                if Vehicle.query.first():
                    logger.info("Data already exists, skipping import")
                    return True
                
                data = self._download_data()
                if not data:
                    logger.error("Failed to download data")
                    return False
                
                success = self._process_and_store_data(data, app)
                
                if success:
                    logger.info("Inventory data import completed successfully")
                else:
                    logger.error("Inventory data import failed")
                
                return success
                
        except Exception as e:
            logger.error(f"Unexpected error during data import: {str(e)}")
            return False
    
    def _download_data(self) -> Optional[str]:
        try:
            logger.info(f"Downloading data from: {self.data_url}")
            
            response = requests.get(self.data_url, timeout=self.timeout)
            response.raise_for_status()
            
            logger.info(f"Successfully downloaded {len(response.text)} characters")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Failed to download data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading data: {str(e)}")
            return None
    
    def _process_and_store_data(self, data: str, app) -> bool:
        try:
            content = StringIO(data)
            reader = csv.DictReader(content, delimiter='|')
            
            with app.app_context():
                db.create_all()
                
                processed_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        vehicle = self._create_vehicle_from_row(row)
                        if vehicle:
                            db.session.add(vehicle)
                            processed_count += 1
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        logger.warning(f"Error processing row {row_num}: {str(e)}")
                        error_count += 1
                
                db.session.commit()
                
                logger.info(f"Data processing completed: {processed_count} vehicles imported, {error_count} errors")
                return processed_count > 0
                
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return False
    
    def _create_vehicle_from_row(self, row: Dict[str, Any]) -> Optional[Vehicle]:
        try:
            vin = row.get('vin', '').strip()
            if not vin:
                return None
            
            year_str = row.get('year', '').strip()
            if not year_str:
                return None
            
            try:
                year = int(year_str)
            except ValueError:
                return None
            
            make = row.get('make', '').strip().lower()
            model = row.get('model', '').strip().lower()
            
            if not make or not model:
                return None
            
            price = self._parse_float(row.get('listing_price'))
            mileage = self._parse_int(row.get('listing_mileage'))
            
            city = row.get('dealer_city', '').strip()
            state = row.get('dealer_state', '').strip()
            
            vehicle = Vehicle(
                vin=vin,
                year=year,
                make=make,
                model=model,
                city=city,
                state=state,
                listing_price=price,
                listing_mileage=mileage
            )
            
            return vehicle
            
        except Exception as e:
            logger.debug(f"Error creating vehicle from row: {str(e)}")
            return None
    
    def _parse_float(self, value: str) -> Optional[float]:
        if not value or not value.strip():
            return None
        
        try:
            return float(value.strip())
        except ValueError:
            return None
    
    def _parse_int(self, value: str) -> Optional[int]:
        if not value or not value.strip():
            return None
        
        try:
            return int(value.strip())
        except ValueError:
            return None 