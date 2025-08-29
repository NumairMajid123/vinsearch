# VIN Search Tool

A simple and modern web-based search tool for finding vehicle listings by VIN (Vehicle Identification Number).

## Features

- **VIN Search**: Search for vehicles by exact VIN match
- **Responsive Design**: Modern, mobile-friendly interface
- **Real-time Results**: Instant search results with clean table display
- **Error Handling**: Comprehensive error handling and user feedback

## Requirements

- PHP 5.6 or higher
- MySQL 5.7 or higher
- Web server (Apache/Nginx)
- PDO MySQL extension

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd vinsearch
```

### 2. Database Setup

1. Create a MySQL database named `vinsearch`
2. Import the database schema:

```bash
mysql -u root -p < database/schema.sql
```

Or manually run the SQL commands from `database/schema.sql`

### 3. Configuration

1. Edit `config/database.php` and update the database credentials:

```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'vinsearch');
define('DB_USER', 'your_username');
define('DB_PASS', 'your_password');
```

## Usage

1. Access the application at `http://your-domain/vinsearch/search.php`
2. Enter a VIN number in the search field
3. Click "Search" to find matching vehicles
4. View results in the formatted table below

## Project Structure

```
vinsearch/
├── search.php              # Main search interface
├── config/
│   └── database.php        # Database configuration
├── models/
│   └── Vehicle.php         # Vehicle model class
├── assets/
│   └── css/
│       └── style.css       # Stylesheets
├── database/
│   └── schema.sql          # Database schema
└── README.md               # This file
```

## Database Schema

### vehicle_listings Table

| Column      | Type         | Description                    |
|-------------|--------------|--------------------------------|
| id          | INT          | Primary key, auto increment    |
| vin         | VARCHAR(17)  | Vehicle Identification Number  |
| year        | INT          | Vehicle year                   |
| make        | VARCHAR(100) | Vehicle make                   |
| model       | VARCHAR(100) | Vehicle model                  |
| trim        | VARCHAR(100) | Vehicle trim level             |
| color       | VARCHAR(50)  | Vehicle color                  |
| mileage     | INT          | Vehicle mileage                |
| price       | DECIMAL(10,2)| Vehicle price                  |
| description | TEXT         | Vehicle description            |
| created_at  | TIMESTAMP    | Record creation timestamp      |
| updated_at  | TIMESTAMP    | Record update timestamp        |

## API Methods

### Vehicle Class Methods

- `searchByVin($vin)`: Search for vehicles by exact VIN match


## Testing

### Manual Testing

1. **Valid VIN Search**: Test with sample VINs from the database
2. **Invalid VIN Search**: Test with non-existent VINs
3. **Empty Search**: Test with empty input
4. **Special Characters**: Test with special characters in input

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database credentials in `config/database.php`
   - Ensure MySQL service is running
   - Verify database exists

2. **Page Not Found**
   - Check web server configuration
   - Verify file permissions
   - Ensure URL rewriting is enabled

3. **No Search Results**
   - Verify database contains data
   - Check VIN format (17 characters)
   - Review database connection

## Version History

- **v1.0**: Initial release with basic VIN search functionality
