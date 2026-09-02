import logging
import re
from typing import List, Tuple, Dict, Any, Optional
from scipy.stats import linregress
from data.models import Vehicle

logger = logging.getLogger(__name__)


class PriceEstimator:

    def __init__(self, config):
        self.config = config
        self.min_vehicles_for_regression = config["MIN_VEHICLES_FOR_REGRESSION"]
        self.price_rounding_factor = config["PRICE_ROUNDING_FACTOR"]
        self.max_mileage = config["MAX_MILEAGE"]

    def estimate_price(
        self, vehicles: List[Vehicle], mileage: Optional[int] = None
    ) -> Tuple[float, Dict[str, Any]]:
        if not vehicles:
            return 0.0, {'method': 'no_data', 'vehicle_count': 0}

        valid_vehicles = [v for v in vehicles if v.listing_price is not None]
        if not valid_vehicles:
            return 0.0, {'method': 'no_valid_prices', 'vehicle_count': 0}

        base_price = sum(v.listing_price for v in valid_vehicles) / len(valid_vehicles)

        if mileage is None:
            rounded_price = self._round_to_nearest(base_price, self.price_rounding_factor)
            return rounded_price, {
                'method': 'average',
                'vehicle_count': len(valid_vehicles),
                'base_price': base_price
            }
        
        print("base_price", base_price)

        adjusted_price, metadata = self._apply_mileage_adjustment(
            valid_vehicles, base_price, mileage
        )
        print("adjusted_price", adjusted_price)


        rounded_price = self._round_to_nearest(adjusted_price, self.price_rounding_factor)
        metadata['vehicle_count'] = len(valid_vehicles)
        metadata['base_price'] = base_price

        return rounded_price, metadata

    def _apply_mileage_adjustment(
        self, vehicles: List[Vehicle], base_price: float, target_mileage: int
    ) -> Tuple[float, Dict[str, Any]]:

        regression_vehicles = [
            v for v in vehicles
            if v.listing_mileage is not None and v.listing_price is not None
        ]
        print("len(regression_vehicles)", len(regression_vehicles))

        if len(regression_vehicles) < self.min_vehicles_for_regression:

            return base_price, {
                'method': 'average',
                'regression': 'insufficient_data',
                'regression_vehicles': len(regression_vehicles)
            }

        mileages = [v.listing_mileage for v in regression_vehicles]
        prices = [v.listing_price for v in regression_vehicles]

        try:
            slope, intercept, r_value, p_value, std_err = linregress(mileages, prices)
            r_squared = r_value ** 2

            predicted_price = slope * target_mileage + intercept
            adjusted_price = max(0, predicted_price)

            return adjusted_price, {
                'method': 'regression',
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
                'p_value': p_value,
                'std_err': std_err,
                'target_mileage': target_mileage,
                'regression_vehicles': len(regression_vehicles)
            }

        except Exception as e:
            logger.warning(f"Regression failed: {str(e)}")
            return base_price, {
                'method': 'average',
                'regression': 'failed',
                'error': str(e)
            }

    def validate_mileage(self, mileage_str: str) -> Optional[int]:
        if not mileage_str or not mileage_str.strip():
            return None

        cleaned = re.sub(r'[,\s]', '', mileage_str.strip())

        try:
            mileage = int(cleaned)
            if mileage < 0 or mileage > self.max_mileage:
                return None
            return mileage
        except ValueError:
            return None

    def _round_to_nearest(self, value: float, factor: int) -> float:
        return round(value / factor) * factor
