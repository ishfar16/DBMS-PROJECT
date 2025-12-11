-- CARZEO Management System Database Schema
-- Created for DBMS Project

-- Drop database if exists and create new one
DROP DATABASE IF EXISTS car_showroom_db;
CREATE DATABASE car_showroom_db;
USE car_showroom_db;

-- 1. Salespersons Table
CREATE TABLE salespersons (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE,
    hire_date DATE DEFAULT CURRENT_DATE,
    commission_rate DECIMAL(5,2) DEFAULT 5.00,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Customers Table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) UNIQUE,
    address TEXT,
    date_of_birth DATE,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('active', 'inactive') DEFAULT 'active'
);

-- 3. Cars Table (Vehicle Inventory)
CREATE TABLE cars (
    car_id INT PRIMARY KEY AUTO_INCREMENT,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    color VARCHAR(30) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    fuel_type ENUM('Petrol', 'Diesel', 'Electric', 'Hybrid', 'CNG') NOT NULL,
    transmission ENUM('Manual', 'Automatic', 'CVT') NOT NULL,
    engine_capacity DECIMAL(3,1),
    mileage DECIMAL(8,2),
    available_stock INT DEFAULT 1,
    status ENUM('available', 'sold', 'reserved', 'maintenance') DEFAULT 'available',
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Sales Table
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    car_id INT NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sale_price DECIMAL(10,2) NOT NULL,
    payment_method ENUM('Cash', 'Loan', 'Lease', 'Credit Card') NOT NULL,
    commission_amount DECIMAL(10,2),
    status ENUM('completed', 'pending', 'cancelled') DEFAULT 'completed',
    notes TEXT,
    FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (salesperson_id) REFERENCES salespersons(employee_id) ON DELETE RESTRICT
);

-- 5. Bookings Table (Test Drive Management)
CREATE TABLE bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    car_id INT NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    purpose ENUM('test_drive', 'viewing', 'consultation') DEFAULT 'test_drive',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (salesperson_id) REFERENCES salespersons(employee_id) ON DELETE SET NULL
);

-- 6. Inquiries Table
CREATE TABLE inquiries (
    inquiry_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    car_id INT,
    inquiry_type ENUM('price', 'availability', 'features', 'test_drive', 'general') NOT NULL,
    message TEXT NOT NULL,
    status ENUM('new', 'in_progress', 'resolved', 'closed') DEFAULT 'new',
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES salespersons(employee_id) ON DELETE SET NULL
);

-- Insert Sample Data

-- Sample Salespersons
INSERT INTO salespersons (name, contact, email, commission_rate) VALUES
('John Smith', '+1-555-0101', 'john.smith@showroom.com', 5.50),
('Sarah Johnson', '+1-555-0102', 'sarah.johnson@showroom.com', 6.00),
('Mike Davis', '+1-555-0103', 'mike.davis@showroom.com', 5.75),
('Lisa Wilson', '+1-555-0104', 'lisa.wilson@showroom.com', 5.25);

-- Sample Customers
INSERT INTO customers (name, phone, email, address) VALUES
('Alice Brown', '+1-555-0201', 'alice.brown@email.com', '123 Main St, City'),
('Bob Green', '+1-555-0202', 'bob.green@email.com', '456 Oak Ave, Town'),
('Carol White', '+1-555-0203', 'carol.white@email.com', '789 Pine Rd, Village'),
('David Black', '+1-555-0204', 'david.black@email.com', '321 Elm St, Borough'),
('Emma Gray', '+1-555-0205', 'emma.gray@email.com', '654 Maple Dr, County');

-- Sample Cars
INSERT INTO cars (brand, model, year, color, price, fuel_type, transmission, engine_capacity, mileage, available_stock) VALUES
('Toyota', 'Camry', 2023, 'Silver', 25000.00, 'Petrol', 'Automatic', 2.5, 15000.00, 3),
('Honda', 'Civic', 2023, 'Blue', 22000.00, 'Petrol', 'Manual', 1.8, 12000.00, 2),
('Ford', 'Mustang', 2023, 'Red', 35000.00, 'Petrol', 'Automatic', 5.0, 8000.00, 1),
('Tesla', 'Model 3', 2023, 'White', 45000.00, 'Electric', 'Automatic', 0.0, 5000.00, 2),
('BMW', 'X5', 2023, 'Black', 65000.00, 'Diesel', 'Automatic', 3.0, 10000.00, 1),
('Mercedes', 'C-Class', 2023, 'Silver', 55000.00, 'Petrol', 'Automatic', 2.0, 12000.00, 2),
('Audi', 'A4', 2023, 'Gray', 48000.00, 'Petrol', 'Automatic', 2.0, 9000.00, 1),
('Hyundai', 'Tucson', 2023, 'Green', 28000.00, 'Hybrid', 'Automatic', 1.6, 11000.00, 3);

-- Sample Sales
INSERT INTO sales (car_id, customer_id, salesperson_id, sale_price, payment_method) VALUES
(1, 1, 1, 25000.00, 'Loan'),
(3, 2, 2, 35000.00, 'Cash'),
(5, 3, 1, 65000.00, 'Credit Card'),
(2, 4, 3, 22000.00, 'Loan');

-- Sample Bookings
INSERT INTO bookings (car_id, customer_id, salesperson_id, booking_date, booking_time, purpose) VALUES
(4, 5, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00:00', 'test_drive'),
(6, 1, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:30:00', 'viewing'),
(7, 2, 2, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '11:00:00', 'test_drive');

-- Sample Inquiries
INSERT INTO inquiries (customer_id, car_id, inquiry_type, message, assigned_to) VALUES
(1, 4, 'price', 'What is the final price including taxes?', 1),
(2, 6, 'availability', 'Do you have this model in red color?', 2),
(3, NULL, 'general', 'What financing options do you offer?', 3);

-- Create Triggers

-- Trigger 1: Update car stock after sale
DELIMITER //
CREATE TRIGGER after_sale_insert
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
    UPDATE cars 
    SET available_stock = available_stock - 1,
        status = CASE 
            WHEN available_stock - 1 = 0 THEN 'sold'
            ELSE 'available'
        END
    WHERE car_id = NEW.car_id;
END//
DELIMITER ;

-- Trigger 2: Calculate commission amount
DELIMITER //
CREATE TRIGGER before_sale_insert
BEFORE INSERT ON sales
FOR EACH ROW
BEGIN
    DECLARE commission_rate DECIMAL(5,2);
    
    SELECT commission_rate INTO commission_rate
    FROM salespersons 
    WHERE employee_id = NEW.salesperson_id;
    
    SET NEW.commission_amount = (NEW.sale_price * commission_rate) / 100;
END//
DELIMITER ;

-- Trigger 3: Update inquiry status when assigned
DELIMITER //
CREATE TRIGGER after_inquiry_update
AFTER UPDATE ON inquiries
FOR EACH ROW
BEGIN
    IF NEW.status = 'resolved' AND OLD.status != 'resolved' THEN
        UPDATE inquiries 
        SET resolved_at = CURRENT_TIMESTAMP 
        WHERE inquiry_id = NEW.inquiry_id;
    END IF;
END//
DELIMITER ;

-- Create Stored Procedures

-- Procedure 1: Book test drive with validation
DELIMITER //
CREATE PROCEDURE BookTestDrive(
    IN p_car_id INT,
    IN p_customer_id INT,
    IN p_salesperson_id INT,
    IN p_booking_date DATE,
    IN p_booking_time TIME,
    OUT p_booking_id INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE car_available INT DEFAULT 0;
    DECLARE time_conflict INT DEFAULT 0;
    
    -- Check if car is available
    SELECT COUNT(*) INTO car_available
    FROM cars 
    WHERE car_id = p_car_id AND status = 'available';
    
    -- Check for time conflicts
    SELECT COUNT(*) INTO time_conflict
    FROM bookings 
    WHERE car_id = p_car_id 
    AND booking_date = p_booking_date
    AND booking_time = p_booking_time
    AND status IN ('pending', 'confirmed');
    
    IF car_available = 0 THEN
        SET p_message = 'Car is not available for test drive';
        SET p_booking_id = NULL;
    ELSEIF time_conflict > 0 THEN
        SET p_message = 'Time slot is already booked';
        SET p_booking_id = NULL;
    ELSE
        INSERT INTO bookings (car_id, customer_id, salesperson_id, booking_date, booking_time)
        VALUES (p_car_id, p_customer_id, p_salesperson_id, p_booking_date, p_booking_time);
        
        SET p_booking_id = LAST_INSERT_ID();
        SET p_message = 'Test drive booked successfully';
    END IF;
END//
DELIMITER ;

-- Procedure 2: Generate monthly sales report
DELIMITER //
CREATE PROCEDURE GenerateMonthlySalesReport(IN p_year INT, IN p_month INT)
BEGIN
    SELECT 
        c.brand,
        c.model,
        COUNT(s.sale_id) as units_sold,
        SUM(s.sale_price) as total_revenue,
        AVG(s.sale_price) as avg_price,
        sp.name as top_salesperson
    FROM cars c
    LEFT JOIN sales s ON c.car_id = s.car_id
    LEFT JOIN salespersons sp ON s.salesperson_id = sp.employee_id
    WHERE YEAR(s.sale_date) = p_year AND MONTH(s.sale_date) = p_month
    GROUP BY c.car_id, c.brand, c.model
    ORDER BY units_sold DESC, total_revenue DESC;
END//
DELIMITER ;

-- Procedure 3: Find inactive cars
DELIMITER //
CREATE PROCEDURE FindInactiveCars(IN p_months INT)
BEGIN
    SELECT 
        c.car_id,
        c.brand,
        c.model,
        c.year,
        c.price,
        c.available_stock,
        DATEDIFF(CURDATE(), c.created_at) as days_in_inventory
    FROM cars c
    WHERE c.car_id NOT IN (
        SELECT DISTINCT car_id FROM sales 
        WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL p_months MONTH)
    )
    AND c.car_id NOT IN (
        SELECT DISTINCT car_id FROM bookings 
        WHERE booking_date >= DATE_SUB(CURDATE(), INTERVAL p_months MONTH)
    )
    AND c.status = 'available'
    ORDER BY days_in_inventory DESC;
END//
DELIMITER ;

-- Create Views

-- View 1: Sales Performance by Salesperson
CREATE VIEW salesperson_performance AS
SELECT 
    sp.employee_id,
    sp.name,
    COUNT(s.sale_id) as total_sales,
    SUM(s.sale_price) as total_revenue,
    AVG(s.sale_price) as avg_sale_price,
    SUM(s.commission_amount) as total_commission
FROM salespersons sp
LEFT JOIN sales s ON sp.employee_id = s.salesperson_id
WHERE s.status = 'completed'
GROUP BY sp.employee_id, sp.name;

-- View 2: Car Inventory Status
CREATE VIEW car_inventory_status AS
SELECT 
    brand,
    model,
    year,
    COUNT(*) as total_cars,
    SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available_cars,
    SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold_cars,
    AVG(price) as avg_price
FROM cars
GROUP BY brand, model, year;

-- View 3: Customer Purchase History
CREATE VIEW customer_purchase_history AS
SELECT 
    c.customer_id,
    c.name,
    c.phone,
    COUNT(s.sale_id) as total_purchases,
    SUM(s.sale_price) as total_spent,
    MAX(s.sale_date) as last_purchase_date
FROM customers c
LEFT JOIN sales s ON c.customer_id = s.customer_id
WHERE s.status = 'completed'
GROUP BY c.customer_id, c.name, c.phone;

-- Create Indexes for better performance
CREATE INDEX idx_cars_brand_model ON cars(brand, model);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_bookings_date_time ON bookings(booking_date, booking_time);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_car ON sales(car_id); 