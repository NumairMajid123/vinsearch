# VIN Search

A web-based car valuation system that estimates market values for vehicles based on year, make, model, and optional mileage input.

## 🎯 Project Overview

This project implements a clean, simple web interface for estimating average market values for vehicles. Users can search by year, make, and model (required) with optional mileage input to get more accurate price estimates.

### Key Features

- **Search Interface**: Clean, responsive web form for vehicle searches
- **Price Estimation**: Calculates market value based on similar vehicle listings
- **Mileage Adjustment**: Uses linear regression to adjust prices based on mileage
- **Sample Listings**: Displays up to 100 comparable vehicle listings

## 🏗️ Technical Architecture

### Technology Stack

- **Backend**: Python Flask web framework
- **Database**: MySQL with SQLAlchemy ORM
- **Data Processing**: SciPy for statistical analysis (Linear Regression)
- **Frontend**: HTML/CSS with Jinja2 templating

## 🗄️ Database Schema

### Vehicle Table

| Column            | Type        | Description                   |
| ----------------- | ----------- | ----------------------------- |
| `id`              | Integer     | Primary key                   |
| `vin`             | String(64)  | Vehicle identification number |
| `year`            | Integer     | Vehicle year                  |
| `make`            | String(100) | Vehicle make                  |
| `model`           | String(100) | Vehicle model                 |
| `city`            | String(100) | Dealer city                   |
| `state`           | String(10)  | Dealer state                  |
| `listing_price`   | Float       | Vehicle listing price         |
| `listing_mileage` | Integer     | Vehicle mileage               |

## 🔧 Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL server
- pip (Python package manager)

### Installation

1. **Clone and setup environment**

   ```bash
   cd vinsearch
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup MySQL database**

   ```sql
   CREATE DATABASE car_value_project_db;
   ```

3. **Configure environment**
   Create `.env` file:

   ```
   FLASK_SECRET_KEY=your_secret_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 🚀 Usage

### Web Interface

1. Navigate to `http://localhost:5000`
2. Enter vehicle details:
   - Year (required): e.g., 2015
   - Make (required): e.g., Toyota
   - Model (required): e.g., Camry
   - Mileage (optional): e.g., 150,000
3. View estimated market price and sample listings

## 📊 Price Estimation Algorithm

### Base Calculation

Average price of all vehicles matching year, make, and model criteria.

### Mileage Adjustment

When mileage is provided, uses linear regression:

```
Estimated Price = Intercept + (Depreciation Rate × Input Mileage)
```

## 🧪 Testing

### Manual Test Cases

1. **Basic Search**: Year=2015, Make=Toyota, Model=Camry
2. **With Mileage**: Add mileage=150000 for adjusted price
3. **Invalid Input**: Test missing required fields
4. **No Results**: Test non-existent vehicle combinations

## 📈 Data Processing

### Data Import Process

1. Downloads data from external URL
2. Processes CSV format with pipe delimiter
3. Handles missing/invalid data gracefully
4. Stores clean data in MySQL database

## 🔮 Future Improvements

### Enhanced Price Estimation

- Multiple factors (condition, location, trends)
- Machine learning models
- Time series analysis
