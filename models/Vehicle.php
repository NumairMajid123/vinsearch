<?php

class Vehicle
{
    private $pdo;
    
    private $tableName = 'vehicle_listings';
    
    public function __construct(PDO $pdo)
    {
        $this->pdo = $pdo;
    }
    
    public function searchByVin($vin)
    {
        if (empty($vin)) {
            throw new InvalidArgumentException('VIN cannot be empty');
        }
        
        $sql = "SELECT 
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
                FROM {$this->tableName}
                WHERE vin = :vin
                ORDER BY created_at DESC";
        
        try {
            $stmt = $this->pdo->prepare($sql);
            $stmt->bindParam(':vin', $vin, PDO::PARAM_STR);
            $stmt->execute();
            
            return $stmt->fetchAll();
        } catch (PDOException $e) {
            error_log('Vehicle Search Error: ' . $e->getMessage());
            throw new Exception('Failed to search for vehicle');
        }
    }
}
