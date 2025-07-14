# 🚗 CARZEO Management System

A comprehensive database-backed web application for managing car showroom operations including vehicle inventory, customer management, sales tracking, and booking management.

## 📋 Features

### Core Modules
- **Vehicle Inventory Management**: Add, edit, delete, and search cars
- **Customer Management**: Store customer details and view purchase history
- **Sales Management**: Log sales transactions with automatic commission calculation
- **Booking/Test Drive Management**: Schedule and manage test drives
- **Comprehensive Reports**: Sales analytics, inventory status, and performance metrics

### Database Features
- **Relational Design**: 6 interconnected tables with foreign keys
- **Triggers**: Auto-update stock, calculate commissions, track inquiry status
- **Stored Procedures**: Booking validation, monthly reports, inactive car detection
- **Views**: Performance analysis, inventory status, customer history
- **Indexes**: Optimized queries for better performance

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **ORM**: SQLAlchemy

## 📦 Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Quick Setup

1. **Clone or download the project files**

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Manual setup** (if setup script fails):
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Import database schema
   mysql -u root -p < database_schema.sql
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## 🗄️ Database Schema

### Tables
1. **salespersons** - Employee information and commission rates
2. **customers** - Customer details and contact information
3. **cars** - Vehicle inventory with specifications
4. **sales** - Sales transactions and payment details
5. **bookings** - Test drive and appointment scheduling
6. **inquiries** - Customer inquiries and support tickets

### Key Features
- **Foreign Key Relationships**: Maintains data integrity
- **Triggers**: Automatic stock updates and commission calculations
- **Stored Procedures**: Complex business logic for bookings and reports
- **Views**: Pre-defined queries for common reports

## 🎯 Demo Walkthrough

### 1. Dashboard
- View key metrics (total cars, sales, customers)
- Recent sales and upcoming bookings
- Quick action buttons

### 2. Vehicle Inventory
- Browse all cars with search/filter functionality
- Add new cars with detailed specifications
- Edit existing car information
- Delete cars (with confirmation)

### 3. Customer Management
- View customer list with contact information
- Add new customers
- View detailed customer history (purchases, bookings, inquiries)

### 4. Sales Management
- Record new sales transactions
- Automatic stock reduction
- Commission calculation
- Sales history and receipts

### 5. Booking Management
- Schedule test drives and appointments
- Time slot conflict detection
- Booking status tracking

### 6. Reports
- **Sales Report**: Monthly sales, top models, salesperson performance
- **Inventory Report**: Stock levels, low stock alerts
- **Performance Analytics**: Revenue trends and insights

## 🔧 Configuration

### Database Configuration
Edit `app.py` to modify database connection:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://username:password@localhost/car_showroom_db'
```

### Sample Data
The database comes pre-loaded with sample data:
- 4 salespersons with different commission rates
- 5 customers with contact information
- 8 cars from various brands (Toyota, Honda, Ford, Tesla, BMW, Mercedes, Audi, Hyundai)
- Sample sales, bookings, and inquiries

## 📊 Database Justification

### Depth of Knowledge
- **Relational Design**: Proper normalization and foreign key relationships
- **SQL JOINs**: Complex queries for meaningful reports
- **Triggers**: Automated business logic (stock updates, commission calculation)
- **Stored Procedures**: Encapsulated complex operations (booking validation)

### Depth of Analysis
- **Trend Analysis**: Top-selling models and brands
- **Performance Metrics**: Salesperson performance tracking
- **Inventory Management**: Low stock alerts and inactive car detection
- **Business Intelligence**: Revenue analysis and forecasting

### Conflicting Requirements Resolution
1. **Instant Booking vs. Limited Availability**: Implemented booking system with slot validation
2. **Quick Entry vs. Detailed Reporting**: Balanced form design with optional fields
3. **Real-time Updates vs. Data Integrity**: Used triggers for automatic updates

## 🚀 Presentation Tips

### Demo Flow
1. **Start with Dashboard**: Show key metrics and recent activity
2. **Inventory Management**: Add a new car, demonstrate search/filter
3. **Customer Management**: Add customer, show purchase history
4. **Sales Process**: Record a sale, show automatic stock update
5. **Booking System**: Schedule test drive, demonstrate conflict detection
6. **Reports**: Show sales analytics and inventory status

### Key Points to Highlight
- **Database Triggers**: Show how stock updates automatically
- **Foreign Key Relationships**: Demonstrate data integrity
- **Stored Procedures**: Explain complex business logic
- **Search Functionality**: Real-time AJAX search
- **Responsive Design**: Works on all devices

## 📁 Project Structure

```
DBMS PROJECT/
├── app.py                 # Main Flask application
├── database_schema.sql    # Complete database schema
├── requirements.txt       # Python dependencies
├── setup.py              # Setup script
├── README.md             # This file
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── dashboard.html    # Dashboard page
    ├── cars/            # Car management templates
    ├── customers/       # Customer management templates
    ├── sales/           # Sales management templates
    ├── bookings/        # Booking management templates
    └── reports/         # Report templates
```

## 🎓 Academic Justification

This project demonstrates:
- **Database Design**: Normalization, relationships, constraints
- **SQL Mastery**: Complex queries, triggers, procedures, views
- **Web Development**: Full-stack application with modern UI
- **Business Logic**: Real-world problem solving and requirements analysis
- **System Integration**: Database, backend, and frontend working together

## 🔍 Troubleshooting

### Common Issues
1. **MySQL Connection Error**: Ensure MySQL is running and accessible
2. **Import Error**: Install requirements with `pip install -r requirements.txt`
3. **Database Not Found**: Run the database schema import
4. **Port Already in Use**: Change port in `app.py` or kill existing process

### Support
For issues or questions, check the error messages in the terminal or browser console.

---

**Happy Presenting! 🚗✨** 