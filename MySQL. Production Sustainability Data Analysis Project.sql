-- 1.1 Corrected MySQL Database Schema --

-- Creating Database --
CREATE DATABASE Production_Sustain;

-- Use Database --
USE Production_Sustain;

-- Create Production Table --
CREATE TABLE Productions(
    production_id INT AUTO_INCREMENT PRIMARY KEY,  -- Changed from SERIAL
    production_name VARCHAR(255) NOT NULL,
    production_type VARCHAR(50),    -- Film, TV Series, Documentary --
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Active'
);

-- Creating Fuel Consumption Tracking (Fixed table name) --
CREATE TABLE Fuel_Consumption(  -- Fixed: removed extra underscore
    record_id INT AUTO_INCREMENT PRIMARY KEY,  -- Changed from SERIAL
    production_id INT,
    date_recorded DATE NOT NULL,
    equipment_type VARCHAR(100), -- Generator, Vehicle, Lighting --
    fuel_type VARCHAR(50), -- Diesel, Gasoline, Propane --
    gallons_consumed DECIMAL(10,2),
    hours_operated DECIMAL(8,2),
    location VARCHAR(255),
    recorded_by VARCHAR(100),
    validation_status VARCHAR(50) DEFAULT 'Pending',
    
    -- Add foreign key constraint separately for MySQL
    FOREIGN KEY (production_id) REFERENCES Productions(production_id)
);

-- Creating Data Quality Tracking --
CREATE TABLE Data_Quality_Log(
    log_id INT AUTO_INCREMENT PRIMARY KEY,  -- Changed from SERIAL
    table_name VARCHAR(100),
    record_id INT, 
    issue_type VARCHAR(100),
    issue_description TEXT,
    severity VARCHAR(20), -- Low, Medium, High, Critical --
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_date TIMESTAMP NULL,
    resolved_by VARCHAR(100)
);

-- Insert Sample Productions Data --
INSERT INTO Productions (production_name, production_type, location) VALUES
('Sunset Boulevard Revival', 'Film', 'Los Angeles, CA'),
('Tech Titans S3', 'TV Series', 'Atlanta, GA'),
('Ocean Depths', 'Documentary', 'Miami, FL');

-- Insert Sample Fuel Consumption Data --
INSERT INTO Fuel_Consumption 
(production_id, date_recorded, equipment_type, fuel_type, gallons_consumed, hours_operated, recorded_by) 
VALUES
(1, '2025-06-01', 'Generator', 'Diesel', 247.50, 12.5, 'John Smith'),
(1, '2025-06-02', 'Vehicle', 'Gasoline', 45.20, 8.0, 'Jane Doe'),
(2, '2025-06-01', 'Lighting Truck', 'Diesel', 156.75, 10.5, 'Mike Johnson'),
(2, '2025-06-02', 'Generator', 'Diesel', 2470.00, 12.0, 'Sarah Wilson'), -- Intentional outlier
(3, '2025-06-01', 'Vehicle', 'Gasoline', 67.30, 6.5, 'Tom Brown'),
(3, '2025-06-02', 'Generator', 'Diesel', 189.45, 14.0, 'Lisa Davis');


-- 4.1 MySQL Reporting Queries

-- Monthly Sustainability Report--
SELECT 
    p.production_name,
    DATE_FORMAT(fc.date_recorded, '%Y-%m') as month,
    SUM(fc.gallons_consumed) as total_fuel,
    SUM(fc.gallons_consumed * 
        CASE fc.fuel_type 
            WHEN 'Diesel' THEN 10.15 
            WHEN 'Gasoline' THEN 8.89 
            ELSE 0 
        END) as carbon_emissions_kg,
    COUNT(*) as total_records,
    COUNT(CASE WHEN fc.validation_status = 'Validated' THEN 1 END) as validated_records
FROM Production_Sustain.Fuel_Consumption fc
JOIN Production_Sustain.Productions p ON fc.production_id = p.production_id
WHERE fc.date_recorded >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY p.production_name, DATE_FORMAT(fc.date_recorded, '%Y-%m')
ORDER BY month DESC;

-- Data Quality Outlier Detection --
SELECT 
    fc.record_id,
    p.production_name,
    fc.gallons_consumed,
    fc.hours_operated,
    CASE 
        WHEN fc.gallons_consumed > 1000 THEN 'High Fuel Outlier'
        WHEN fc.gallons_consumed < 0 THEN 'Negative Value'
        WHEN fc.hours_operated > 24 THEN 'Invalid Hours'
        WHEN fc.date_recorded > CURDATE() THEN 'Future Date'
        ELSE 'Normal'
    END as quality_flag
FROM Production_Sustain.Fuel_Consumption fc
JOIN Production_Sustain.Productions p ON fc.production_id = p.production_id
WHERE fc.gallons_consumed > 1000 
   OR fc.gallons_consumed < 0 
   OR fc.hours_operated > 24
   OR fc.date_recorded > CURDATE();
   
-- Production Rankings by Emissions --
SELECT 
    p.production_name,
    SUM(fc.gallons_consumed * 
        CASE fc.fuel_type 
            WHEN 'Diesel' THEN 10.15 
            WHEN 'Gasoline' THEN 8.89 
            ELSE 0 
        END) as total_emissions_kg,
    RANK() OVER (ORDER BY SUM(fc.gallons_consumed * 
        CASE fc.fuel_type 
            WHEN 'Diesel' THEN 10.15 
            WHEN 'Gasoline' THEN 8.89 
            ELSE 0 
        END) DESC) as emission_rank
FROM Production_Sustain.Fuel_Consumption fc
JOIN Production_Sustain.Productions p ON fc.production_id = p.production_id
GROUP BY p.production_name
ORDER BY total_emissions_kg DESC;