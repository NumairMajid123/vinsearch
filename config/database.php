<?php

define('DB_HOST', 'localhost');
define('DB_NAME', 'vinsearch');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_CHARSET', 'utf8mb4');

function createDatabaseConnection() {
    $dsn = sprintf(
        'mysql:host=%s;dbname=%s;charset=%s',
        DB_HOST,
        DB_NAME,
        DB_CHARSET
    );
    
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ];
    
    try {
        $pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
        return $pdo;
    } catch (PDOException $e) {
        error_log('Database Connection Error: ' . $e->getMessage());
        throw new Exception('Database connection failed. Please check your configuration.');
    }
}

try {
    $pdo = createDatabaseConnection();
} catch (Exception $e) {
    die('Database connection failed: ' . $e->getMessage());
}
