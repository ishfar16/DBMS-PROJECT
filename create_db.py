from app import app, db, Admin, Salesperson, Customer, Car, Sale, Booking, Inquiry
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash

def create_database():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Creating admin user...")
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username='admin').first()
        if not existing_admin:
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@carzeo.com'
            )
            db.session.add(admin)
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
        
        print("Creating sample data...")
        
        # Create sample salespersons
        salespersons = [
            Salesperson(
                name='John Smith',
                contact='+8801918-666696',
                email='john.smith@carzeo.com',
                hire_date=date(2023, 1, 15),
                commission_rate=5.00
            ),
            Salesperson(
                name='Sarah Johnson',
                contact='+8801918-666697',
                email='sarah.johnson@carzeo.com',
                hire_date=date(2023, 3, 20),
                commission_rate=5.50
            )
        ]
        
        for sp in salespersons:
            existing = Salesperson.query.filter_by(email=sp.email).first()
            if not existing:
                db.session.add(sp)
        
        # Create sample customers
        customers = [
            Customer(
                name='Alice Brown',
                phone='+8801918-666698',
                email='alice.brown@email.com',
                address='Dhaka, Bangladesh',
                password_hash=generate_password_hash('password123'),
                registration_date=datetime(2024, 1, 15)
            ),
            Customer(
                name='Bob Wilson',
                phone='+8801918-666699',
                email='bob.wilson@email.com',
                address='Chittagong, Bangladesh',
                password_hash=generate_password_hash('password123'),
                registration_date=datetime(2024, 2, 20)
            )
        ]
        
        for customer in customers:
            existing = Customer.query.filter_by(email=customer.email).first()
            if not existing:
                db.session.add(customer)
        
        # Create sample cars
        cars = [
            Car(
                brand='Toyota',
                model='Camry',
                year=2023,
                color='Silver',
                price=2500000.00,  # BDT
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
                price=3200000.00,  # BDT
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
                price=4500000.00,  # BDT
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
                price=4200000.00,  # BDT
                fuel_type='Electric',
                transmission='Automatic',
                engine_capacity=0.0,
                mileage=5000.00,
                available_stock=2,
                description='Electric sedan with advanced autopilot features'
            )
        ]
        
        for car in cars:
            existing = Car.query.filter_by(brand=car.brand, model=car.model, year=car.year).first()
            if not existing:
                db.session.add(car)
        
        try:
            db.session.commit()
            print("Database created successfully!")
            print("\n=== LOGIN CREDENTIALS ===")
            print("Admin Login:")
            print("Username: admin")
            print("Password: admin123")
            print("\nSample Customer Logins:")
            print("Email: alice.brown@email.com, Password: password123")
            print("Email: bob.wilson@email.com, Password: password123")
            print("\nYou can now start the application with: python app.py")
            
        except Exception as e:
            print(f"Error creating database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_database() 