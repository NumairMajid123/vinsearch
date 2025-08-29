# VIN Search Tool - Project Outline

## Project Overview

The VIN Search Tool is a web-based application that allows users to search for vehicle listings by VIN (Vehicle Identification Number). The application provides a simple, modern interface for querying a MySQL database and displaying results in a formatted table.

## Project Structure

```
vinsearch/
├── search.php              # Main search interface (Entry point)
├── install.php             # Installation wizard
├── .htaccess              # Apache configuration
├── README.md              # Project documentation
├── PROJECT_OUTLINE.md     # This file
├── config/
│   └── database.php       # Database configuration
├── models/
│   └── Vehicle.php        # Vehicle model class
├── assets/
│   └── css/
│       └── style.css      # Stylesheets
├── database/
│   └── schema.sql         # Database schema
```

## Classes and Methods

### 1. Vehicle Class (`models/Vehicle.php`)

**Properties**:
- `$pdo` (PDO): Database connection instance
- `$tableName` (string): Database table name ('vehicle_listings')

**Methods**:

#### `__construct(PDO $pdo)`
- **Purpose**: Initialize the Vehicle model with database connection
- **Parameters**: PDO database connection instance
- **Returns**: void

#### `searchByVin($vin)`
- **Purpose**: Search for vehicles by exact VIN match
- **Parameters**: string $vin - Vehicle Identification Number
- **Returns**: array - Array of matching vehicles
- **Throws**: InvalidArgumentException, Exception
- **SQL**: `SELECT * FROM vehicle_listings WHERE vin = :vin ORDER BY created_at DESC`

## Database Schema

### vehicle_listings Table

| Column      | Type         | Null | Key | Default | Description                    |
|-------------|--------------|------|-----|---------|--------------------------------|
| id          | INT          | NO   | PRI | AUTO    | Primary key, auto increment    |
| vin         | VARCHAR(17)  | NO   | UNI | NULL    | Vehicle Identification Number  |
| year        | INT          | NO   |     | NULL    | Vehicle year                   |
| make        | VARCHAR(100) | NO   |     | NULL    | Vehicle make                   |
| model       | VARCHAR(100) | NO   |     | NULL    | Vehicle model                  |
| trim        | VARCHAR(100) | YES  |     | NULL    | Vehicle trim level             |
| color       | VARCHAR(50)  | YES  |     | NULL    | Vehicle color                  |
| mileage     | INT          | YES  |     | NULL    | Vehicle mileage                |
| price       | DECIMAL(10,2)| YES  |     | NULL    | Vehicle price                  |
| description | TEXT         | YES  |     | NULL    | Vehicle description            |
| created_at  | TIMESTAMP    | NO   |     | CURRENT | Record creation timestamp      |
| updated_at  | TIMESTAMP    | NO   |     | CURRENT | Record update timestamp        |

### Indexes
- `PRIMARY KEY` on `id`
- `UNIQUE KEY` on `vin`
- `INDEX` on `year`
- `INDEX` on `make`
- `INDEX` on `model`
- `INDEX` on `created_at`

### Views
- `vehicle_summary`: Simplified view for common queries

### Stored Procedures
- `SearchVehicleByVIN(IN search_vin VARCHAR(17))`: Exact VIN search
- `SearchVehicleByPartialVIN(IN search_vin VARCHAR(17))`: Partial VIN search

## Main Application Flow

### 1. User Interface (`search.php`)

**Entry Point**: `http://<test VM>/vinsearch/search.php`

**Components**:
- HTML form with VIN input field
- Search button
- Results table
- Error/success message display

**User Flow**:
1. User enters VIN in input field
2. User clicks "Search" button
3. Form submits via POST to same page
4. PHP processes search request
5. Results displayed in table format

### 2. Search Processing

**Input Validation**:
- Check if VIN is provided
- Trim whitespace
- Validate VIN format (optional)

**Database Query**:
- Create Vehicle model instance
- Call `searchByVin()` method
- Handle exceptions and errors

**Output Formatting**:
- Display results in HTML table
- Format numbers (mileage, price)
- Escape HTML output for security

### 3. Error Handling

**Types of Errors**:
- Database connection errors
- Invalid input errors
- No results found
- System errors

**Error Display**:
- User-friendly error messages
- Technical details logged to error log
- Graceful degradation

## Installation and Setup

### 1. Automated Installation (`install.php`)

**Features**:
- System requirements check
- Database connection test
- Schema creation
- Configuration file generation
- Sample data insertion

**Installation Flow**:
1. Access `install.php` in browser
2. Check system requirements
3. Enter database credentials
4. Execute installation
5. Verify installation success

### 2. Manual Installation

**Steps**:
1. Upload files to web server
2. Create MySQL database
3. Import schema from `database/schema.sql`
4. Configure database connection in `config/database.php`
5. Set proper file permissions

## Code Style Compliance

The project follows the coding style guide published at: http://docs.autoscale.ventures/display/AP/Coding+Style+Guide
