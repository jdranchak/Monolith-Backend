from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, JSON, Date
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
    order_count = Column(Integer, default=0)

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
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="orders")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, index=True)
    price = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    order_count = Column(Integer, default=0)
    orders = relationship("Order", back_populates="product")
    quantity = Column(Integer, nullable=False)
    inventory = relationship("Inventory", back_populates="product")
    inventory_history = relationship("InventoryHistory", back_populates="product")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    location = Column(String, default="Main Warehouse")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationship
    product = relationship("Product", back_populates="inventory")

class InventoryHistory(Base):
    __tablename__ = "inventory_history"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    old_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    quantity_change = Column(Integer, nullable=False)  # new - old (can be negative)
    change_reason = Column(String, nullable=False)  # "sale", "restock", "damage", "adjustment"
    location = Column(String, default="Main Warehouse")
    changed_by = Column(String, nullable=False)  # user ID or system
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable =True)  # Optional additional details
    
    # Relationship
    product = relationship("Product", back_populates="inventory_history")


#user management and authentication
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Many-to-many relationship with roles
    roles = relationship("Role", secondary="user_roles", back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)  # "admin", "manager", "employee"
    permissions = Column(JSON)
    
    # Many-to-many relationship with users
    users = relationship("User", secondary="user_roles", back_populates="roles")

class UserRole(Base):  # Many-to-many
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))



#company structure 
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # "Sales", "Engineering", "HR"
    manager_id = Column(Integer, ForeignKey("employees.id"))
    budget = Column(Float)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    employee_id = Column(String, unique=True)  # "EMP001"
    department_id = Column(Integer, ForeignKey("departments.id"))
    position = Column(String)
    salary = Column(Float)
    hire_date = Column(Date)
    manager_id = Column(Integer, ForeignKey("employees.id"))  # Self-reference

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # "New York Office", "Warehouse A"
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)


 #financial management    
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    account_number = Column(String, unique=True)
    account_name = Column(String)
    account_type = Column(String)  # "asset", "liability", "equity", "revenue", "expense"
    balance = Column(Float, default=0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    transaction_number = Column(String, unique=True)
    date = Column(Date)
    description = Column(Text)
    total_amount = Column(Float)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class TransactionLine(Base):  # Double-entry bookkeeping
    __tablename__ = "transaction_lines"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit_amount = Column(Float, default=0)
    credit_amount = Column(Float, default=0)

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    issue_date = Column(Date)
    due_date = Column(Date)
    subtotal = Column(Float)
    tax_amount = Column(Float)
    total_amount = Column(Float)
    status = Column(String)  # "draft", "sent", "paid", "overdue"


 #supply chain and vendors   

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(Text)
    payment_terms = Column(String)  # "Net 30", "COD"
    is_active = Column(Boolean, default=True)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    po_number = Column(String, unique=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    order_date = Column(Date)
    expected_delivery = Column(Date)
    status = Column(String)  # "pending", "approved", "shipped", "received"
    total_amount = Column(Float)

class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity_ordered = Column(Integer)
    quantity_received = Column(Integer, default=0)
    unit_price = Column(Float)



#analytics and reporting
class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Text)
    query = Column(Text)  # SQL query or report definition
    created_by = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    table_name = Column(String)
    record_id = Column(Integer)
    action = Column(String)  # "CREATE", "UPDATE", "DELETE"
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    first_name = Column(String)
    last_name = Column(String)
    title = Column(String)
    email = Column(String)
    phone = Column(String)
    is_primary = Column(Boolean, default=False)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    company_name = Column(String)
    contact_name = Column(String)
    email = Column(String)
    phone = Column(String)
    source = Column(String)  # "website", "referral", "cold_call"
    status = Column(String)  # "new", "contacted", "qualified", "converted"
    assigned_to = Column(Integer, ForeignKey("employees.id"))

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    name = Column(String)
    value = Column(Float)
    probability = Column(Float)  # 0-100%
    stage = Column(String)  # "prospecting", "proposal", "negotiation", "closed"
    expected_close_date = Column(Date)
    assigned_to = Column(Integer, ForeignKey("employees.id"))

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    ticket_number = Column(String, unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    subject = Column(String)
    description = Column(Text)
    priority = Column(String)  # "low", "medium", "high", "urgent"
    status = Column(String)  # "open", "in_progress", "resolved", "closed"
    assigned_to = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = Column(DateTime)

class TicketComment(Base):
    __tablename__ = "ticket_comments"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    comment = Column(Text)
    is_internal = Column(Boolean, default=False)  # Internal notes vs customer-visible
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    