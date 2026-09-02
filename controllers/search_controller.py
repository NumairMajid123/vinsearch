import logging
from flask import request, render_template, flash
from services.vehicle_service import VehicleService
from services.price_estimator import PriceEstimator

logger = logging.getLogger(__name__)


class SearchController:

    def __init__(self, config):
        self.config = config
        self.vehicle_service = VehicleService(config)
        self.price_estimator = PriceEstimator(config)

    def handle_search_page(self):
        return render_template('search.html')

    def handle_search_request(self):
        try:
            year = request.form.get("year", "").strip()
            make = request.form.get("make", "").strip()
            model = request.form.get("model", "").strip()
            mileage = request.form.get("mileage", "").strip()

            is_valid, error = self.vehicle_service.validate_search_input(year, make, model)
            if not is_valid:
                flash(error)
                return render_template(
                    'search.html',
                    year=year,
                    make=make,
                    model=model,
                    mileage=mileage
                )

            vehicles = self.vehicle_service.search_vehicles(int(year), make, model)

            if not vehicles:
                flash(f"No vehicles found for {year} {make} {model}")
                return render_template(
                    'search.html',
                    year=year,
                    make=make,
                    model=model,
                    mileage=mileage
                )

            parsed_mileage = None
            if mileage:
                parsed_mileage = self.price_estimator.validate_mileage(mileage)
                if parsed_mileage is None:
                    flash("Invalid mileage format. Please enter a valid number.")
                    return render_template(
                        'search.html',
                        year=year,
                        make=make,
                        model=model,
                        mileage=mileage
                    )

            estimated_price, metadata = self.price_estimator.estimate_price(
                vehicles, parsed_mileage
            )

            listings = self.vehicle_service.get_sample_listings(vehicles)

            return render_template(
                'results.html',
                ymm=f"{year} {make} {model}",
                mileage=mileage if mileage else None,
                estimated_price=estimated_price,
                listings=listings,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error in search request: {str(e)}")
            flash("An error occurred while processing your request.")
            return render_template('search.html')
