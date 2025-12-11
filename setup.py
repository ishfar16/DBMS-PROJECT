#!/usr/bin/env python3
"""
Setup script for Smart Car Showroom Management System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages"""
    print("Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def check_mysql():
    """Check if MySQL is available"""
    print("Checking MySQL connection...")
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        connection.close()
        print("✅ MySQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("Please make sure MySQL is running and accessible")
        return False

def setup_database():
    """Set up the database schema"""
    print("Setting up database...")
    try:
        # Read the SQL file
        with open('database_schema.sql', 'r') as f:
            sql_content = f.read()
        
        # Connect to MySQL and execute the schema
        import mysql.connector
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = connection.cursor()
        
        # Split and execute SQL statements
        statements = sql_content.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("✅ Database setup completed!")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚗 CARZEO Management System Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check MySQL
    if not check_mysql():
        return
    
    # Setup database
    if not setup_database():
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Make sure MySQL is running")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("\nHappy presenting! 🚀")

if __name__ == "__main__":
    main() 