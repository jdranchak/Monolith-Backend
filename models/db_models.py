from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship: One customer can have many orders
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    sale_price = Column(Float, nullable=False)
    sold_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, nullable=False)
    # Foreign key: Links to customers table
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Relationship: Each order belongs to one customer
    customer = relationship("Customer", back_populates="orders")