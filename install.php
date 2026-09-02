<?php

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    handleDatabaseSetup();
} else {
    displayInstallationPage();
}

function handleDatabaseSetup() {
    $host = isset($_POST['db_host']) ? $_POST['db_host'] : 'localhost';
    $name = isset($_POST['db_name']) ? $_POST['db_name'] : 'vinsearch';
    $user = isset($_POST['db_user']) ? $_POST['db_user'] : 'root';
    $pass = isset($_POST['db_pass']) ? $_POST['db_pass'] : '';
    
    try {
        $pdo = new PDO(
            "mysql:host=$host;charset=utf8mb4",
            $user,
            $pass,
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
        );
        
        $pdo->exec("CREATE DATABASE IF NOT EXISTS `$name` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
        $pdo->exec("USE `$name`");
        
        $schema = file_get_contents('database/schema.sql');
        $statements = explode(';', $schema);
        
        foreach ($statements as $statement) {
            $statement = trim($statement);
            if (!empty($statement)) {
                $pdo->exec($statement);
            }
        }
        
        updateConfigFile($host, $name, $user, $pass);
        
        $success = "Installation completed successfully! You can now access the VIN Search Tool.";
        
    } catch (Exception $e) {
        $error = "Database setup failed: " . $e->getMessage();
    }
    
    displayInstallationPage(isset($success) ? $success : null, isset($error) ? $error : null);
}

function updateConfigFile($host, $name, $user, $pass) {
    $configContent = "<?php

define('DB_HOST', '$host');
define('DB_NAME', '$name');
define('DB_USER', '$user');
define('DB_PASS', '$pass');
define('DB_CHARSET', 'utf8mb4');

function createDatabaseConnection() {
    \$dsn = sprintf(
        'mysql:host=%s;dbname=%s;charset=%s',
        DB_HOST,
        DB_NAME,
        DB_CHARSET
    );
    
    \$options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];
    
    try {
        \$pdo = new PDO(\$dsn, DB_USER, DB_PASS, \$options);
        return \$pdo;
    } catch (PDOException \$e) {
        error_log('Database Connection Error: ' . \$e->getMessage());
        throw new Exception('Database connection failed. Please check your configuration.');
    }
}

try {
    \$pdo = createDatabaseConnection();
} catch (Exception \$e) {
    die('Database connection failed: ' . \$e->getMessage());
}
";
    
    file_put_contents('config/database.php', $configContent);
}

function displayInstallationPage($success = null, $error = null) {
    $requirements = checkRequirements();
    ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIN Search Tool - Installation</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        .header {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
        }
        .content {
            padding: 30px;
        }
        .requirement {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .requirement:last-child {
            border-bottom: none;
        }
        .status {
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        .status.pass {
            background: #d4edda;
            color: #155724;
        }
        .status.fail {
            background: #f8d7da;
            color: #721c24;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #dee2e6;
            border-radius: 4px;
            font-size: 16px;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VIN Search Tool Installation</h1>
            <p>Welcome to the VIN Search Tool installation wizard</p>
        </div>
        
        <div class="content">
            <?php if ($success): ?>
                <div class="alert alert-success">
                    <?php echo htmlspecialchars($success); ?>
                </div>
            <?php endif; ?>
            
            <?php if ($error): ?>
                <div class="alert alert-error">
                    <?php echo htmlspecialchars($error); ?>
                </div>
            <?php endif; ?>
            
            <h2>System Requirements</h2>
            <?php foreach ($requirements as $requirement => $status): ?>
                <div class="requirement">
                    <span><?php echo htmlspecialchars($requirement); ?></span>
                    <span class="status <?php echo $status ? 'pass' : 'fail'; ?>">
                        <?php echo $status ? 'PASS' : 'FAIL'; ?>
                    </span>
                </div>
            <?php endforeach; ?>
            
            <?php if (array_search(false, $requirements) === false): ?>
                <h2>Database Configuration</h2>
                <form method="POST">
                    <div class="form-group">
                        <label for="db_host">Database Host:</label>
                        <input type="text" id="db_host" name="db_host" value="localhost" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="db_name">Database Name:</label>
                        <input type="text" id="db_name" name="db_name" value="vinsearch" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="db_user">Database Username:</label>
                        <input type="text" id="db_user" name="db_user" value="root" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="db_pass">Database Password:</label>
                        <input type="password" id="db_pass" name="db_pass">
                    </div>
                    
                    <button type="submit" class="btn">Install VIN Search Tool</button>
                </form>
            <?php else: ?>
                <div class="alert alert-error">
                    Please fix the failed requirements before proceeding with installation.
                </div>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
    <?php
}

function checkRequirements() {
    $requirements = [];
    
    $requirements['PHP Version (>= 5.6)'] = version_compare(PHP_VERSION, '5.6.0', '>=');
    
    $requirements['PDO Extension'] = extension_loaded('pdo');
    
    $requirements['PDO MySQL Extension'] = extension_loaded('pdo_mysql');
    
    $requirements['Config Directory Writable'] = is_writable('config') || is_writable('.');
    
    $requirements['Database Schema File'] = file_exists('database/schema.sql');
    
    return $requirements;
}
?>
