from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
# from image_utils import optimize_image_upload

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_showroom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# Authentication decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please login as admin to access this page', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_logged_in' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('customer_login'))
        return f(*args, **kwargs)
    return decorated_function

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Salesperson(db.Model):
    __tablename__ = 'salespersons'
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True)
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    commission_rate = db.Column(db.Numeric(5,2), default=5.00)
    status = db.Column(db.String(10), default='active')

class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True)
    address = db.Column(db.Text)
    password_hash = db.Column(db.String(255), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), default='active')

class Car(db.Model):
    __tablename__ = 'cars'
    car_id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    fuel_type = db.Column(db.String(10), nullable=False)
    transmission = db.Column(db.String(10), nullable=False)
    engine_capacity = db.Column(db.Numeric(3,1))
    mileage = db.Column(db.Numeric(8,2))
    available_stock = db.Column(db.Integer, default=1)
    status = db.Column(db.String(15), default='available')
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('salespersons.employee_id'), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    sale_price = db.Column(db.Numeric(10,2), nullable=False)
    payment_method = db.Column(db.String(15), nullable=False)
    commission_amount = db.Column(db.Numeric(10,2))
    status = db.Column(db.String(15), default='completed')
    notes = db.Column(db.Text)

class Booking(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    salesperson_id = db.Column(db.Integer, db.ForeignKey('salespersons.employee_id'))
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    status = db.Column(db.String(15), default='pending')
    purpose = db.Column(db.String(15), default='test_drive')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    inquiry_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'))
    inquiry_type = db.Column(db.String(15), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(15), default='new')
    assigned_to = db.Column(db.Integer, db.ForeignKey('salespersons.employee_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

# Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.admin_id
            session['admin_username'] = admin.username
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Customer login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        customer = Customer.query.filter_by(email=email).first()
        if customer and check_password_hash(customer.password_hash, password):
            session['customer_logged_in'] = True
            session['customer_id'] = customer.customer_id
            session['customer_name'] = customer.name
            flash(f'Welcome back, {customer.name}!', 'success')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('customer/login.html')

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    """Customer registration page"""
    if request.method == 'POST':
        try:
            # Check if email already exists
            existing_customer = Customer.query.filter_by(email=request.form['email']).first()
            if existing_customer:
                flash('Email already registered. Please login instead.', 'error')
                return render_template('customer/register.html')
            
            customer = Customer(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form['email'],
                address=request.form['address'],
                password_hash=generate_password_hash(request.form['password'])
            )
            db.session.add(customer)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('customer_login'))
        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
    
    return render_template('customer/register.html')

@app.route('/customer/logout')
def customer_logout():
    """Customer logout"""
    session.pop('customer_logged_in', None)
    session.pop('customer_id', None)
    session.pop('customer_name', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('customer_login'))

# Public Routes
@app.route('/')
def home():
    """Public home page with car catalog"""
    try:
        cars = Car.query.filter(Car.available_stock > 0).order_by(Car.created_at.desc()).all()
        return render_template('public/home.html', cars=cars)
    except Exception as e:
        flash(f'Error loading catalog: {str(e)}', 'error')
        return render_template('public/home.html', cars=[])

@app.route('/search')
def search_cars():
    """Public car search"""
    try:
        brand = request.args.get('brand', '')
        model = request.args.get('model', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        availability = request.args.get('availability', '')
        
        query = Car.query
        
        if brand:
            query = query.filter(Car.brand.ilike(f'%{brand}%'))
        if model:
            query = query.filter(Car.model.ilike(f'%{model}%'))
        if min_price:
            query = query.filter(Car.price >= float(min_price))
        if max_price:
            query = query.filter(Car.price <= float(max_price))
        if availability == 'available':
            query = query.filter(Car.available_stock > 0)
        elif availability == 'out_of_stock':
            query = query.filter(Car.available_stock == 0)
        
        cars = query.order_by(Car.created_at.desc()).all()
        return render_template('public/search.html', cars=cars, 
                             brand=brand, model=model, min_price=min_price, 
                             max_price=max_price, availability=availability)
    except Exception as e:
        flash(f'Error searching cars: {str(e)}', 'error')
        return render_template('public/search.html', cars=[])

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with key metrics"""
    try:
        # Get key metrics
        total_cars = Car.query.count()
        available_cars = Car.query.filter_by(status='available').count()
        total_sales = Sale.query.filter_by(status='completed').count()
        total_customers = Customer.query.count()
        
        # Recent sales
        recent_sales = db.session.query(Sale, Car, Customer, Salesperson).join(
            Car, Sale.car_id == Car.car_id
        ).join(
            Customer, Sale.customer_id == Customer.customer_id
        ).join(
            Salesperson, Sale.salesperson_id == Salesperson.employee_id
        ).order_by(Sale.sale_date.desc()).limit(5).all()
        
        # Upcoming bookings
        upcoming_bookings = db.session.query(Booking, Car, Customer).join(
            Car, Booking.car_id == Car.car_id
        ).join(
            Customer, Booking.customer_id == Customer.customer_id
        ).filter(
            Booking.booking_date >= datetime.now().date(),
            Booking.status.in_(['pending', 'confirmed'])
        ).order_by(Booking.booking_date, Booking.booking_time).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                             total_cars=total_cars,
                             available_cars=available_cars,
                             total_sales=total_sales,
                             total_customers=total_customers,
                             recent_sales=recent_sales,
                             upcoming_bookings=upcoming_bookings)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html')

# Vehicle Inventory Management (Admin only)
@app.route('/admin/cars')
@admin_required
def admin_cars():
    """List all cars (admin)"""
    try:
        cars = Car.query.order_by(Car.created_at.desc()).all()
        return render_template('admin/cars/list.html', cars=cars)
    except Exception as e:
        flash(f'Error loading cars: {str(e)}', 'error')
        return render_template('admin/cars/list.html', cars=[])

@app.route('/admin/cars/add', methods=['GET', 'POST'])
@admin_required
def admin_add_car():
    """Add new car (admin)"""
    if request.method == 'POST':
        try:
            # Handle image upload
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    # Process and optimize the image
                    # if optimize_image_upload(file, app.config['UPLOAD_FOLDER'], filename):
                    #     image_url = f"uploads/{filename}"
                    # else:
                    #     flash('Error processing image. Please try again.', 'error')
                    #     return render_template('admin/cars/add.html')
                    
                    # Simple file save for now
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_url = f"uploads/{filename}"
            
            car = Car(
                brand=request.form['brand'],
                model=request.form['model'],
                year=int(request.form['year']),
                color=request.form['color'],
                price=float(request.form['price']),
                fuel_type=request.form['fuel_type'],
                transmission=request.form['transmission'],
                engine_capacity=float(request.form['engine_capacity']) if request.form['engine_capacity'] else None,
                mileage=float(request.form['mileage']) if request.form['mileage'] else None,
                available_stock=int(request.form['available_stock']),
                description=request.form['description'],
                image_url=image_url
            )
            db.session.add(car)
            db.session.commit()
            flash('Car added successfully!', 'success')
            return redirect(url_for('admin_cars'))
        except Exception as e:
            flash(f'Error adding car: {str(e)}', 'error')
    
    return render_template('admin/cars/add.html')

@app.route('/admin/cars/edit/<int:car_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_car(car_id):
    """Edit car (admin)"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            # Handle image removal
            if request.form.get('remove_image') == 'true':
                car.image_url = None
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add timestamp to make filename unique
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    
                    # Process and optimize the image
                    # if optimize_image_upload(file, app.config['UPLOAD_FOLDER'], filename):
                    #     car.image_url = f"uploads/{filename}"
                    # else:
                    #     flash('Error processing image. Please try again.', 'error')
                    #     return render_template('admin/cars/edit.html', car=car)
                    
                    # Simple file save for now
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    car.image_url = f"uploads/{filename}"
            
            car.brand = request.form['brand']
            car.model = request.form['model']
            car.year = int(request.form['year'])
            car.color = request.form['color']
            car.price = float(request.form['price'])
            car.fuel_type = request.form['fuel_type']
            car.transmission = request.form['transmission']
            car.engine_capacity = float(request.form['engine_capacity']) if request.form['engine_capacity'] else None
            car.mileage = float(request.form['mileage']) if request.form['mileage'] else None
            car.available_stock = int(request.form['available_stock'])
            car.description = request.form['description']
            
            db.session.commit()
            flash('Car updated successfully!', 'success')
            return redirect(url_for('admin_cars'))
        except Exception as e:
            flash(f'Error updating car: {str(e)}', 'error')
    
    return render_template('admin/cars/edit.html', car=car)

@app.route('/admin/cars/delete/<int:car_id>', methods=['POST'])
@admin_required
def admin_delete_car(car_id):
    """Delete car (admin)"""
    try:
        car = Car.query.get_or_404(car_id)
        db.session.delete(car)
        db.session.commit()
        flash('Car deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting car: {str(e)}', 'error')
    
    return redirect(url_for('admin_cars'))

# Customer Management (Admin only)
@app.route('/admin/customers')
@admin_required
def admin_customers():
    """List all customers (admin)"""
    try:
        customers = Customer.query.order_by(Customer.registration_date.desc()).all()
        return render_template('admin/customers/list.html', customers=customers)
    except Exception as e:
        flash(f'Error loading customers: {str(e)}', 'error')
        return render_template('admin/customers/list.html', customers=[])

@app.route('/admin/customers/add', methods=['GET', 'POST'])
@admin_required
def admin_add_customer():
    """Add new customer (admin)"""
    if request.method == 'POST':
        try:
            customer = Customer(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form['email'],
                address=request.form['address'],
                password_hash=generate_password_hash(request.form['password'])
            )
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('admin_customers'))
        except Exception as e:
            flash(f'Error adding customer: {str(e)}', 'error')
    
    return render_template('admin/customers/add.html')

@app.route('/admin/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_customer(customer_id):
    """Edit customer (admin)"""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.phone = request.form['phone']
            customer.email = request.form['email']
            customer.address = request.form['address']
            
            # Update password if provided
            if request.form.get('new_password'):
                customer.password_hash = generate_password_hash(request.form['new_password'])
            
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('admin_customers'))
        except Exception as e:
            flash(f'Error updating customer: {str(e)}', 'error')
    
    return render_template('admin/customers/edit.html', customer=customer)

@app.route('/admin/customers/delete/<int:customer_id>', methods=['POST'])
@admin_required
def admin_delete_customer(customer_id):
    """Delete customer (admin)"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'error')
    
    return redirect(url_for('admin_customers'))

@app.route('/admin/customers/<int:customer_id>')
@admin_required
def admin_customer_detail(customer_id):
    """Customer detail with purchase history (admin)"""
    try:
        customer = Customer.query.get_or_404(customer_id)
        sales = Sale.query.filter_by(customer_id=customer_id).all()
        bookings = Booking.query.filter_by(customer_id=customer_id).all()
        inquiries = Inquiry.query.filter_by(customer_id=customer_id).all()
        
        return render_template('admin/customers/detail.html', 
                             customer=customer, 
                             sales=sales, 
                             bookings=bookings, 
                             inquiries=inquiries)
    except Exception as e:
        flash(f'Error loading customer details: {str(e)}', 'error')
        return redirect(url_for('admin_customers'))

# Salesperson Management (Admin only)
@app.route('/admin/salespersons')
@admin_required
def admin_salespersons():
    """List all salespersons (admin)"""
    try:
        salespersons = Salesperson.query.order_by(Salesperson.hire_date.desc()).all()
        return render_template('admin/salespersons/list.html', salespersons=salespersons)
    except Exception as e:
        flash(f'Error loading salespersons: {str(e)}', 'error')
        return render_template('admin/salespersons/list.html', salespersons=[])

@app.route('/admin/salespersons/add', methods=['GET', 'POST'])
@admin_required
def admin_add_salesperson():
    """Add new salesperson (admin)"""
    if request.method == 'POST':
        try:
            salesperson = Salesperson(
                name=request.form['name'],
                contact=request.form['contact'],
                email=request.form['email'],
                hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form['hire_date'] else datetime.now().date(),
                commission_rate=float(request.form['commission_rate']),
                status=request.form['status']
            )
            db.session.add(salesperson)
            db.session.commit()
            flash('Salesperson added successfully!', 'success')
            return redirect(url_for('admin_salespersons'))
        except Exception as e:
            flash(f'Error adding salesperson: {str(e)}', 'error')
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin/salespersons/add.html', today_date=today_date)

@app.route('/admin/salespersons/edit/<int:employee_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_salesperson(employee_id):
    """Edit salesperson (admin)"""
    salesperson = Salesperson.query.get_or_404(employee_id)
    
    if request.method == 'POST':
        try:
            salesperson.name = request.form['name']
            salesperson.contact = request.form['contact']
            salesperson.email = request.form['email']
            salesperson.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date() if request.form['hire_date'] else salesperson.hire_date
            salesperson.commission_rate = float(request.form['commission_rate'])
            salesperson.status = request.form['status']
            
            db.session.commit()
            flash('Salesperson updated successfully!', 'success')
            return redirect(url_for('admin_salespersons'))
        except Exception as e:
            flash(f'Error updating salesperson: {str(e)}', 'error')
    
    return render_template('admin/salespersons/edit.html', salesperson=salesperson)

@app.route('/admin/salespersons/delete/<int:employee_id>', methods=['POST'])
@admin_required
def admin_delete_salesperson(employee_id):
    """Delete salesperson (admin)"""
    try:
        salesperson = Salesperson.query.get_or_404(employee_id)
        db.session.delete(salesperson)
        db.session.commit()
        flash('Salesperson deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting salesperson: {str(e)}', 'error')
    
    return redirect(url_for('admin_salespersons'))

@app.route('/admin/salespersons/<int:employee_id>')
@admin_required
def admin_salesperson_detail(employee_id):
    """Salesperson detail with sales history (admin)"""
    try:
        salesperson = Salesperson.query.get_or_404(employee_id)
        sales = Sale.query.filter_by(salesperson_id=employee_id).all()
        bookings = Booking.query.filter_by(salesperson_id=employee_id).all()
        inquiries = Inquiry.query.filter_by(assigned_to=employee_id).all()
        
        return render_template('admin/salespersons/detail.html', 
                             salesperson=salesperson, 
                             sales=sales, 
                             bookings=bookings, 
                             inquiries=inquiries)
    except Exception as e:
        flash(f'Error loading salesperson details: {str(e)}', 'error')
        return redirect(url_for('admin_salespersons'))

# Sales Management (Admin only)
@app.route('/admin/sales')
@admin_required
def admin_sales():
    """List all sales (admin)"""
    try:
        sales_data = db.session.query(Sale, Car, Customer, Salesperson).join(
            Car, Sale.car_id == Car.car_id
        ).join(
            Customer, Sale.customer_id == Customer.customer_id
        ).join(
            Salesperson, Sale.salesperson_id == Salesperson.employee_id
        ).order_by(Sale.sale_date.desc()).all()
        
        return render_template('admin/sales/list.html', sales=sales_data)
    except Exception as e:
        flash(f'Error loading sales: {str(e)}', 'error')
        return render_template('admin/sales/list.html', sales=[])

@app.route('/admin/sales/add', methods=['GET', 'POST'])
@admin_required
def admin_add_sale():
    """Add new sale (admin)"""
    if request.method == 'POST':
        try:
            car_id = int(request.form['car_id'])
            car = Car.query.get(car_id)
            
            # Check if car is available and has stock
            if not car or car.available_stock <= 0:
                flash('Selected car is not available for sale', 'error')
                return render_template('admin/sales/add.html', 
                                     cars=Car.query.filter(Car.available_stock > 0).all(),
                                     customers=Customer.query.all(),
                                     salespersons=Salesperson.query.filter_by(status='active').all())
            
            # Calculate commission amount
            commission_rate = float(request.form.get('commission_rate', 5.0))
            sale_price = float(request.form['sale_price'])
            commission_amount = (sale_price * commission_rate) / 100
            
            sale = Sale(
                car_id=car_id,
                customer_id=int(request.form['customer_id']),
                salesperson_id=int(request.form['salesperson_id']),
                sale_price=sale_price,
                payment_method=request.form['payment_method'],
                commission_amount=commission_amount,
                notes=request.form.get('notes', '')
            )
            
            # Reduce car stock
            car.available_stock -= 1
            
            # Update car status if no stock left
            if car.available_stock == 0:
                car.status = 'sold'
            
            db.session.add(sale)
            db.session.commit()
            flash('Sale recorded successfully! Stock updated.', 'success')
            return redirect(url_for('admin_sales'))
        except Exception as e:
            flash(f'Error recording sale: {str(e)}', 'error')
    
    cars = Car.query.filter(Car.available_stock > 0).all()
    customers = Customer.query.all()
    salespersons = Salesperson.query.filter_by(status='active').all()
    
    return render_template('admin/sales/add.html', cars=cars, customers=customers, salespersons=salespersons)

# Booking Management (Admin only)
@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    """List all bookings (admin)"""
    try:
        bookings_data = db.session.query(Booking, Car, Customer, Salesperson).join(
            Car, Booking.car_id == Car.car_id
        ).join(
            Customer, Booking.customer_id == Customer.customer_id
        ).outerjoin(
            Salesperson, Booking.salesperson_id == Salesperson.employee_id
        ).order_by(Booking.booking_date, Booking.booking_time).all()
        
        return render_template('admin/bookings/list.html', bookings=bookings_data)
    except Exception as e:
        flash(f'Error loading bookings: {str(e)}', 'error')
        return render_template('admin/bookings/list.html', bookings=[])

@app.route('/admin/bookings/add', methods=['GET', 'POST'])
@admin_required
def admin_add_booking():
    """Add new booking (admin)"""
    if request.method == 'POST':
        try:
            booking = Booking(
                car_id=int(request.form['car_id']),
                customer_id=int(request.form['customer_id']),
                salesperson_id=int(request.form['salesperson_id']) if request.form['salesperson_id'] else None,
                booking_date=datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date(),
                booking_time=datetime.strptime(request.form['booking_time'], '%H:%M').time(),
                duration_minutes=int(request.form.get('duration_minutes', 30)),
                purpose=request.form['purpose'],
                notes=request.form.get('notes', '')
            )
            db.session.add(booking)
            db.session.commit()
            flash('Booking created successfully!', 'success')
            return redirect(url_for('admin_bookings'))
        except Exception as e:
            flash(f'Error creating booking: {str(e)}', 'error')
    
    cars = Car.query.filter_by(status='available').all()
    customers = Customer.query.all()
    salespersons = Salesperson.query.filter_by(status='active').all()
    
    return render_template('admin/bookings/add.html', cars=cars, customers=customers, salespersons=salespersons)

@app.route('/admin/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if request.method == 'POST':
        try:
            booking.status = request.form['status']
            booking.notes = request.form.get('notes', '')
            db.session.commit()
            flash('Booking updated successfully!', 'success')
            return redirect(url_for('admin_bookings'))
        except Exception as e:
            flash(f'Error updating booking: {str(e)}', 'error')
    return render_template('admin/bookings/edit.html', booking=booking)

# Reports (Admin only)
@app.route('/admin/reports')
@admin_required
def admin_reports():
    """Reports dashboard (admin)"""
    return render_template('admin/reports/index.html')

@app.route('/admin/reports/sales')
@admin_required
def admin_sales_report():
    """Sales report (admin)"""
    try:
        # Monthly sales data
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_sales = db.session.query(
            Car.brand,
            Car.model,
            db.func.count(Sale.sale_id).label('units_sold'),
            db.func.sum(Sale.sale_price).label('total_revenue'),
            db.func.avg(Sale.sale_price).label('avg_price')
        ).join(Sale, Car.car_id == Sale.car_id).filter(
            db.extract('month', Sale.sale_date) == current_month,
            db.extract('year', Sale.sale_date) == current_year
        ).group_by(Car.car_id, Car.brand, Car.model).order_by(
            db.func.count(Sale.sale_id).desc()
        ).all()
        
        # Top selling models
        top_models = db.session.query(
            Car.brand,
            Car.model,
            db.func.count(Sale.sale_id).label('total_sales')
        ).join(Sale, Car.car_id == Sale.car_id).group_by(
            Car.brand, Car.model
        ).order_by(db.func.count(Sale.sale_id).desc()).limit(10).all()
        
        # Salesperson performance
        salesperson_performance = db.session.query(
            Salesperson.name,
            db.func.count(Sale.sale_id).label('total_sales'),
            db.func.sum(Sale.sale_price).label('total_revenue'),
            db.func.sum(Sale.commission_amount).label('total_commission')
        ).join(Sale, Salesperson.employee_id == Sale.salesperson_id).group_by(
            Salesperson.employee_id, Salesperson.name
        ).order_by(db.func.sum(Sale.sale_price).desc()).all()
        
        return render_template('admin/reports/sales.html', 
                             monthly_sales=monthly_sales,
                             top_models=top_models,
                             salesperson_performance=salesperson_performance)
    except Exception as e:
        flash(f'Error generating sales report: {str(e)}', 'error')
        return render_template('admin/reports/sales.html')

@app.route('/admin/reports/sales/reset', methods=['POST'])
@admin_required
def admin_sales_report_reset():
    try:
        num_deleted = Sale.query.delete()
        db.session.commit()
        flash(f'Successfully cleared {num_deleted} sales records.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing sales records: {str(e)}', 'error')
    return redirect(url_for('admin_sales_report'))

@app.route('/admin/reports/inventory')
@admin_required
def admin_inventory_report():
    """Inventory report (admin)"""
    try:
        from sqlalchemy import case
        # Inventory status
        inventory_status = db.session.query(
            Car.brand,
            Car.model,
            Car.year,
            db.func.count(Car.car_id).label('total_cars'),
            db.func.sum(case((Car.status == 'available', 1), else_=0)).label('available_cars'),
            db.func.sum(case((Car.status == 'sold', 1), else_=0)).label('sold_cars'),
            db.func.avg(Car.price).label('avg_price')
        ).group_by(Car.brand, Car.model, Car.year).all()
        
        # Low stock alerts
        low_stock = Car.query.filter(Car.available_stock <= 2).all()
        
        return render_template('admin/reports/inventory.html', 
                             inventory_status=inventory_status,
                             low_stock=low_stock)
    except Exception as e:
        flash(f'Error generating inventory report: {str(e)}', 'error')
        return render_template('admin/reports/inventory.html')

# Customer Routes
@app.route('/customer')
@customer_required
def customer_dashboard():
    """Customer dashboard"""
    try:
        customer_id = session.get('customer_id')
        customer = Customer.query.get(customer_id)
        
        # Get customer's bookings
        bookings = db.session.query(Booking, Car).join(
            Car, Booking.car_id == Car.car_id
        ).filter(Booking.customer_id == customer_id).order_by(
            Booking.booking_date.desc()
        ).all()
        
        # Get customer's inquiries
        inquiries = Inquiry.query.filter_by(customer_id=customer_id).order_by(
            Inquiry.created_at.desc()
        ).all()
        
        return render_template('customer/dashboard.html', 
                             customer=customer, 
                             bookings=bookings, 
                             inquiries=inquiries)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('customer/dashboard.html')

@app.route('/customer/catalog')
def customer_catalog():
    """Customer car catalog (public access)"""
    try:
        cars = Car.query.filter(Car.available_stock > 0).order_by(Car.created_at.desc()).all()
        return render_template('customer/catalog.html', cars=cars)
    except Exception as e:
        flash(f'Error loading catalog: {str(e)}', 'error')
        return render_template('customer/catalog.html', cars=[])

@app.route('/customer/book-car/<int:car_id>', methods=['GET', 'POST'])
@customer_required
def customer_book_car(car_id):
    """Book a car (customer)"""
    car = Car.query.get_or_404(car_id)
    
    if request.method == 'POST':
        try:
            customer_id = session.get('customer_id')
            
            booking = Booking(
                car_id=car_id,
                customer_id=customer_id,
                booking_date=datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date(),
                booking_time=datetime.strptime(request.form['booking_time'], '%H:%M').time(),
                purpose='test_drive',
                notes=request.form.get('notes', '')
            )
            db.session.add(booking)
            db.session.commit()
            
            flash('Booking created successfully!', 'success')
            return redirect(url_for('customer_dashboard'))
        except Exception as e:
            flash(f'Error creating booking: {str(e)}', 'error')
    
    return render_template('customer/book_car.html', car=car)

@app.route('/customer/profile')
@customer_required
def customer_profile():
    """Customer profile page"""
    try:
        customer_id = session.get('customer_id')
        customer = Customer.query.get(customer_id)
        return render_template('customer/profile.html', customer=customer)
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('customer_dashboard'))

@app.route('/customer/profile/edit', methods=['GET', 'POST'])
@customer_required
def customer_edit_profile():
    """Edit customer profile"""
    customer_id = session.get('customer_id')
    customer = Customer.query.get(customer_id)
    
    if request.method == 'POST':
        try:
            customer.name = request.form['name']
            customer.phone = request.form['phone']
            customer.address = request.form['address']
            
            # Update password if provided
            if request.form.get('new_password'):
                customer.password_hash = generate_password_hash(request.form['new_password'])
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('customer_profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
    
    return render_template('customer/edit_profile.html', customer=customer)

# API endpoints for AJAX
@app.route('/api/cars/search')
def api_search_cars():
    """Search cars by brand, model, or price range"""
    try:
        brand = request.args.get('brand', '')
        model = request.args.get('model', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        availability = request.args.get('availability', 'available')
        
        query = Car.query
        
        if brand:
            query = query.filter(Car.brand.ilike(f'%{brand}%'))
        if model:
            query = query.filter(Car.model.ilike(f'%{model}%'))
        if min_price:
            query = query.filter(Car.price >= float(min_price))
        if max_price:
            query = query.filter(Car.price <= float(max_price))
        
        # Filter by availability
        if availability == 'available':
            query = query.filter(Car.available_stock > 0)
        elif availability == 'out_of_stock':
            query = query.filter(Car.available_stock == 0)
        
        cars = query.all()
        
        return jsonify([{
            'car_id': car.car_id,
            'brand': car.brand,
            'model': car.model,
            'year': car.year,
            'color': car.color,
            'price': float(car.price),
            'available_stock': car.available_stock,
            'status': car.status
        } for car in cars])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cars/<int:car_id>')
def api_get_car_details(car_id):
    """Get detailed car information"""
    try:
        car = Car.query.get_or_404(car_id)
        return jsonify({
            'car_id': car.car_id,
            'brand': car.brand,
            'model': car.model,
            'year': car.year,
            'color': car.color,
            'price': float(car.price),
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'engine_capacity': float(car.engine_capacity) if car.engine_capacity else None,
            'mileage': float(car.mileage) if car.mileage else None,
            'available_stock': car.available_stock,
            'status': car.status,
            'description': car.description,
            'image_url': car.image_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/create', methods=['POST'])
@customer_required
def api_create_booking():
    """Create a new booking from customer catalog"""
    try:
        customer_id = session.get('customer_id')
        car_id = request.form.get('car_id')
        booking_date = request.form.get('booking_date')
        booking_time = request.form.get('booking_time')
        
        if not all([car_id, booking_date, booking_time]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Create booking
        booking = Booking(
            car_id=int(car_id) if car_id else 0,
            customer_id=customer_id,
            booking_date=datetime.strptime(booking_date, '%Y-%m-%d').date() if booking_date else datetime.now().date(),
            booking_time=datetime.strptime(booking_time, '%H:%M').time() if booking_time else datetime.now().time(),
            purpose='test_drive',
            notes=request.form.get('notes', '')
        )
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/bookings/check-availability')
def api_check_booking_availability():
    """Check booking availability for a car and time slot"""
    try:
        car_id = int(request.args.get('car_id', 0))
        booking_date_str = request.args.get('booking_date', '')
        booking_time_str = request.args.get('booking_time', '')
        
        if not booking_date_str or not booking_time_str:
            return jsonify({'error': 'Missing booking date or time'}), 400
            
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        booking_time = datetime.strptime(booking_time_str, '%H:%M').time()
        
        # Check for conflicts
        conflict = Booking.query.filter(
            Booking.car_id == car_id,
            Booking.booking_date == booking_date,
            Booking.booking_time == booking_time,
            Booking.status.in_(['pending', 'confirmed'])
        ).first()
        
        return jsonify({'available': conflict is None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 