#!/usr/bin/env python3
"""
Database initialization script for CARZEO Management System
Creates tables and inserts sample data for SQLite database
"""

from app import app, db, Admin, Salesperson, Customer, Car, Sale, Booking, Inquiry
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            email='admin@carzeo.com'
        )
        db.session.add(admin)
        
        # Create sample salespersons
        salespersons = [
            Salesperson(
                name='John Smith',
                contact='+1-555-0101',
                email='john.smith@carzeo.com',
                hire_date=date(2023, 1, 15),
                commission_rate=5.00
            ),
            Salesperson(
                name='Sarah Johnson',
                contact='+1-555-0102',
                email='sarah.johnson@carzeo.com',
                hire_date=date(2023, 3, 20),
                commission_rate=5.50
            ),
            Salesperson(
                name='Mike Davis',
                contact='+1-555-0103',
                email='mike.davis@carzeo.com',
                hire_date=date(2023, 6, 10),
                commission_rate=4.75
            )
        ]
        for sp in salespersons:
            db.session.add(sp)
        
        # Create sample customers
        customers = [
            Customer(
                name='Alice Brown',
                phone='+1-555-0201',
                email='alice.brown@email.com',
                address='123 Main St, City, State 12345',
                password_hash=generate_password_hash('password123'),
                registration_date=datetime(2024, 1, 15)
            ),
            Customer(
                name='Bob Wilson',
                phone='+1-555-0202',
                email='bob.wilson@email.com',
                address='456 Oak Ave, City, State 12345',
                password_hash=generate_password_hash('password123'),
                registration_date=datetime(2024, 2, 20)
            ),
            Customer(
                name='Carol Martinez',
                phone='+1-555-0203',
                email='carol.martinez@email.com',
                address='789 Pine Rd, City, State 12345',
                password_hash=generate_password_hash('password123'),
                registration_date=datetime(2024, 3, 10)
            )
        ]
        for customer in customers:
            db.session.add(customer)
        
        # Create sample cars
        cars = [
            Car(
                brand='Toyota',
                model='Camry',
                year=2023,
                color='Silver',
                price=25000.00,
                fuel_type='Gasoline',
                transmission='Automatic',
                engine_capacity=2.5,
                mileage=15000.00,
                available_stock=3,
                description='Reliable sedan with excellent fuel economy'
            ),
            Car(
                brand='Honda',
                model='CR-V',
                year=2023,
                color='Blue',
                price=32000.00,
                fuel_type='Gasoline',
                transmission='Automatic',
                engine_capacity=1.5,
                mileage=12000.00,
                available_stock=2,
                description='Popular SUV with great safety ratings'
            ),
            Car(
                brand='Ford',
                model='Mustang',
                year=2023,
                color='Red',
                price=45000.00,
                fuel_type='Gasoline',
                transmission='Manual',
                engine_capacity=5.0,
                mileage=8000.00,
                available_stock=1,
                description='Iconic sports car with powerful V8 engine'
            ),
            Car(
                brand='Tesla',
                model='Model 3',
                year=2023,
                color='White',
                price=42000.00,
                fuel_type='Electric',
                transmission='Automatic',
                engine_capacity=0.0,
                mileage=5000.00,
                available_stock=2,
                description='Electric sedan with advanced autopilot features'
            ),
            Car(
                brand='BMW',
                model='X5',
                year=2023,
                color='Black',
                price=65000.00,
                fuel_type='Gasoline',
                transmission='Automatic',
                engine_capacity=3.0,
                mileage=10000.00,
                available_stock=1,
                description='Luxury SUV with premium features'
            ),
            Car(
                brand='Mercedes',
                model='C-Class',
                year=2023,
                color='Silver',
                price=48000.00,
                fuel_type='Gasoline',
                transmission='Automatic',
                engine_capacity=2.0,
                mileage=12000.00,
                available_stock=0,
                status='sold',
                description='Luxury sedan with elegant design'
            )
        ]
        for car in cars:
            db.session.add(car)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample sales
        sales = [
            Sale(
                car_id=6,  # Mercedes C-Class
                customer_id=1,  # Alice Brown
                salesperson_id=1,  # John Smith
                sale_date=datetime(2024, 1, 20),
                sale_price=48000.00,
                payment_method='Finance',
                commission_amount=2400.00
            )
        ]
        for sale in sales:
            db.session.add(sale)
        
        # Create sample bookings
        bookings = [
            Booking(
                car_id=1,  # Toyota Camry
                customer_id=2,  # Bob Wilson
                salesperson_id=2,  # Sarah Johnson
                booking_date=date(2024, 4, 15),
                booking_time=time(14, 30),
                purpose='test_drive',
                status='confirmed',
                notes='Customer interested in fuel efficiency'
            ),
            Booking(
                car_id=3,  # Ford Mustang
                customer_id=3,  # Carol Martinez
                booking_date=date(2024, 4, 16),
                booking_time=time(10, 0),
                purpose='test_drive',
                status='pending',
                notes='First-time sports car buyer'
            )
        ]
        for booking in bookings:
            db.session.add(booking)
        
        # Create sample inquiries
        inquiries = [
            Inquiry(
                customer_id=1,  # Alice Brown
                car_id=4,  # Tesla Model 3
                inquiry_type='price_inquiry',
                message='What is the current price for the Tesla Model 3? Are there any available discounts?',
                status='new'
            ),
            Inquiry(
                customer_id=2,  # Bob Wilson
                car_id=2,  # Honda CR-V
                inquiry_type='availability',
                message='When will the Honda CR-V be available for test drive?',
                status='in_progress',
                assigned_to=1  # John Smith
            )
        ]
        for inquiry in inquiries:
            db.session.add(inquiry)
        
        # Final commit
        db.session.commit()
        
        print("Database initialized successfully!")
        print("\nDefault Admin Login:")
        print("Username: admin")
        print("Password: admin123")
        print("\nSample Customer Logins:")
        print("Email: alice.brown@email.com, Password: password123")
        print("Email: bob.wilson@email.com, Password: password123")
        print("Email: carol.martinez@email.com, Password: password123")

if __name__ == '__main__':
    init_database() 