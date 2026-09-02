-- VIN Search Tool Database Schema

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS vinsearch
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE vinsearch;

CREATE TABLE IF NOT EXISTS vehicle_listings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vin VARCHAR(17) NOT NULL UNIQUE,
    year INT NOT NULL,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    trim VARCHAR(100) DEFAULT NULL,
    color VARCHAR(50) DEFAULT NULL,
    mileage INT DEFAULT NULL,
    price DECIMAL(10,2) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_vin (vin),
    INDEX idx_year (year),
    INDEX idx_make (make),
    INDEX idx_model (model),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO vehicle_listings (vin, year, make, model, trim, color, mileage, price, description) VALUES
('1HGBH41JXMN109186', 2021, 'Honda', 'Civic', 'EX', 'Blue', 15000, 25000.00, 'Well-maintained Honda Civic with low mileage'),
('2T1BURHE0JC123456', 2018, 'Toyota', 'Camry', 'SE', 'Silver', 45000, 22000.00, 'Reliable Toyota Camry in excellent condition'),
('3VWDX7AJ5DM123456', 2013, 'Volkswagen', 'Jetta', 'S', 'White', 75000, 12000.00, 'Clean Volkswagen Jetta with good service history'),
('4T1B11HK5JU123456', 2018, 'Toyota', 'Corolla', 'LE', 'Red', 38000, 18000.00, 'Fuel-efficient Toyota Corolla'),
('5NPE34AF5FH123456', 2015, 'Hyundai', 'Sonata', 'Sport', 'Black', 65000, 15000.00, 'Comfortable Hyundai Sonata with sport package'),
('1FADP3F22EL123456', 2014, 'Ford', 'Focus', 'SE', 'Gray', 82000, 9500.00, 'Economical Ford Focus'),
('2G1WC5E37E1123456', 2014, 'Chevrolet', 'Malibu', 'LT', 'Silver', 78000, 11000.00, 'Spacious Chevrolet Malibu'),
('3C6RR7LT8GS123456', 2016, 'Chrysler', '200', 'Limited', 'Blue', 55000, 16000.00, 'Luxury Chrysler 200 with premium features'),
('4S3BMHB68B3286055', 2011, 'Subaru', 'Legacy', '2.5i', 'Green', 95000, 8500.00, 'All-wheel drive Subaru Legacy'),
('5FNRL38467B123456', 2007, 'Honda', 'Odyssey', 'EX-L', 'Silver', 120000, 7500.00, 'Family-friendly Honda Odyssey minivan');

CREATE OR REPLACE VIEW vehicle_summary AS
SELECT 
    id,
    vin,
    year,
    make,
    model,
    trim,
    color,
    mileage,
    price,
    created_at
FROM vehicle_listings
ORDER BY created_at DESC;

DELIMITER //
CREATE PROCEDURE SearchVehicleByVIN(IN search_vin VARCHAR(17))
BEGIN
    SELECT 
        vin,
        year,
        make,
        model,
        trim,
        color,
        mileage,
        price,
        created_at,
        updated_at
    FROM vehicle_listings
    WHERE vin = search_vin
    ORDER BY created_at DESC;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE SearchVehicleByPartialVIN(IN search_vin VARCHAR(17))
BEGIN
    SELECT 
        vin,
        year,
        make,
        model,
        trim,
        color,
        mileage,
        price,
        created_at,
        updated_at
    FROM vehicle_listings
    WHERE vin LIKE CONCAT('%', search_vin, '%')
    ORDER BY created_at DESC
    LIMIT 50;
END //
DELIMITER ;
