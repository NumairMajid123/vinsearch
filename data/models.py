from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(64))
    year = db.Column(db.Integer)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(10))
    listing_price = db.Column(db.Float)
    listing_mileage = db.Column(db.Integer)

    def to_dict(self):

        return {
            "id": self.vin,
            "vehicle": f"{self.year} {self.make} {self.model}",
            "price": self.listing_price,
            "mileage": self.listing_mileage,
            "location": f"{self.city}, {self.state}",
        }
