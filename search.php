<?php

date_default_timezone_set('UTC');

require_once 'config/database.php';

require_once 'models/Vehicle.php';

$vin = '';
$searchResults = [];
$error = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['vin'])) {
    $vin = trim($_POST['vin']);
    
    if (empty($vin)) {
        $error = 'Please enter a VIN number.';
    } else {
        try {
            $vehicleModel = new Vehicle($pdo);
            $searchResults = $vehicleModel->searchByVin($vin);
            
            if (empty($searchResults)) {
                $success = 'No vehicles found with the provided VIN.';
            }
        } catch (Exception $e) {
            $error = 'An error occurred while searching. Please try again.';
            error_log('VIN Search Error: ' . $e->getMessage());
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Search Tool</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>VIN Search Tool</h1>
            <p>Search for vehicle listings by VIN number</p>
        </header>

        <main>
            <section class="search-section">
                <form method="POST" action="" class="search-form">
                    <div class="form-group">
                        <label for="vin">VIN:</label>
                        <input 
                            type="text" 
                            id="vin" 
                            name="vin" 
                            value="<?php echo htmlspecialchars($vin); ?>"
                            placeholder="Enter VIN number"
                            maxlength="17"
                            required
                        >
                        <button type="submit" class="btn-search">Search</button>
                    </div>
                </form>
            </section>

            <?php if (!empty($error)): ?>
                <div class="alert alert-error">
                    <?php echo htmlspecialchars($error); ?>
                </div>
            <?php endif; ?>

            <?php if (!empty($success)): ?>
                <div class="alert alert-success">
                    <?php echo htmlspecialchars($success); ?>
                </div>
            <?php endif; ?>

            <?php if (!empty($searchResults)): ?>
                <section class="results-section">
                    <h2>Search Results</h2>
                    <div class="table-container">
                        <table class="results-table">
                            <thead>
                                <tr>
                                    <th>VIN</th>
                                    <th>Year</th>
                                    <th>Make</th>
                                    <th>Model</th>
                                    <th>Trim</th>
                                    <th>Color</th>
                                    <th>Mileage</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($searchResults as $vehicle): ?>
                                    <tr>
                                        <td><?php echo htmlspecialchars($vehicle['vin']); ?></td>
                                        <td><?php echo htmlspecialchars($vehicle['year']); ?></td>
                                        <td><?php echo htmlspecialchars($vehicle['make']); ?></td>
                                        <td><?php echo htmlspecialchars($vehicle['model']); ?></td>
                                        <td><?php echo htmlspecialchars($vehicle['trim']); ?></td>
                                        <td><?php echo htmlspecialchars($vehicle['color']); ?></td>
                                        <td><?php echo number_format($vehicle['mileage']); ?></td>
                                        <td>$<?php echo number_format($vehicle['price'], 2); ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </section>
            <?php endif; ?>
        </main>

        <footer>
            <p>&copy; <?php echo date('Y'); ?> VIN Search Tool. All rights reserved.</p>
        </footer>
    </div>
</body>
</html>
