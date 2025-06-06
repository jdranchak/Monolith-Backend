#!/usr/bin/env python3
"""
Simple script to test database connection and add sample customers
"""
import sys
sys.path.append('/home/appuser')

from common.db import SessionLocal, engine
from models.db_models import Base, Customer

# Create tables
Base.metadata.create_all(bind=engine)

# Create sample customers
def add_sample_customers():
    db = SessionLocal()
    try:
        # Check if customers already exist
        existing = db.query(Customer).first()
        if existing:
            print("Customers already exist in database:")
            customers = db.query(Customer).all()
            for customer in customers:
                print(f"  ID: {customer.id}, Name: {customer.name}, Email: {customer.email}")
            return
        
        # Add sample customers
        customers = [
            Customer(name="John Doe", email="john@example.com"),
            Customer(name="Jane Smith", email="jane@example.com"),
            Customer(name="Bob Johnson", email="bob@example.com")
        ]
        
        for customer in customers:
            db.add(customer)
        
        db.commit()
        print("✅ Successfully added sample customers!")
        
        # Show what was added
        all_customers = db.query(Customer).all()
        print("\nCustomers in database:")
        for customer in all_customers:
            print(f"  ID: {customer.id}, Name: {customer.name}, Email: {customer.email}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_customers() 