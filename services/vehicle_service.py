import logging
from typing import List, Optional

from data.models import Vehicle, db

logger = logging.getLogger(__name__)


class VehicleService:

    def __init__(self, config):
        self.config = config
        self.max_listings = config["MAX_LISTINGS_DISPLAY"]

    def search_vehicles(self, year: int, make: str, model: str) -> List[Vehicle]:
        try:
            normalized_make = make.lower().strip()
            normalized_model = model.lower().strip()

            vehicles = Vehicle.query.filter_by(
                year=year, make=normalized_make, model=normalized_model
            ).all()

            logger.info(f"Found {len(vehicles)} vehicles for {year} {make} {model}")
            return vehicles

        except Exception as e:
            logger.error(f"Error searching vehicles: {str(e)}")
            return []

    def get_sample_listings(self, vehicles: List[Vehicle]) -> List[dict]:

        try:
            # Limit to max listings and convert to dict
            limited_vehicles = vehicles[: self.max_listings]
            listings = [v.to_dict() for v in limited_vehicles]

            logger.info(f"Returning {len(listings)} sample listings")
            return listings

        except Exception as e:
            logger.error(f"Error getting sample listings: {str(e)}")
            return []

    def validate_search_input(
        self, year: str, make: str, model: str
    ) -> tuple[bool, Optional[str]]:

        if not year or not year.strip():
            return False, "Year is required"

        if not make or not make.strip():
            return False, "Make is required"

        if not model or not model.strip():
            return False, "Model is required"

        try:
            year_int = int(year.strip())
            if year_int < self.config["MIN_YEAR"] or year_int > self.config["MAX_YEAR"]:
                return (
                    False,
                    f"Year must be between {self.config["MIN_YEAR"]} and {self.config["MAX_YEAR"]}",
                )
        except ValueError:
            return False, "Year must be a valid number"

        return True, None

    def get_vehicle_statistics(self, vehicles: List[Vehicle]) -> dict:
        if not vehicles:
            return {
                "total_vehicles": 0,
                "vehicles_with_prices": 0,
                "vehicles_with_mileage": 0,
                "price_range": None,
                "mileage_range": None,
            }

        vehicles_with_prices = [v for v in vehicles if v.listing_price is not None]
        vehicles_with_mileage = [v for v in vehicles if v.listing_mileage is not None]

        price_range = None
        if vehicles_with_prices:
            prices = [v.listing_price for v in vehicles_with_prices]
            price_range = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices),
            }

        mileage_range = None
        if vehicles_with_mileage:
            mileages = [v.listing_mileage for v in vehicles_with_mileage]
            mileage_range = {
                "min": min(mileages),
                "max": max(mileages),
                "avg": sum(mileages) / len(mileages),
            }

        return {
            "total_vehicles": len(vehicles),
            "vehicles_with_prices": len(vehicles_with_prices),
            "vehicles_with_mileage": len(vehicles_with_mileage),
            "price_range": price_range,
            "mileage_range": mileage_range,
        }
