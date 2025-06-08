# Monolith Backend API

Basic backend system for business management. Built with FastAPI + PostgreSQL.

**Local dev:** http://localhost:8000  
**API docs:** http://localhost:8000/docs

## What's implemented

### Core stuff
- Health check endpoints
- Customer management 
- Product catalog with inventory
- Order processing
- User accounts with roles
- Financial transactions
- Support tickets

### Customer API (`/customers`)
```
POST   /customers/           # create customer
GET    /customers/           # list all
GET    /customers/{id}       # get one
GET    /customers/{id}/with-orders  # includes order history
```

Email validation works, tracks order counts automatically.

### Products (`/products`) 
```
POST   /products/            # create product
GET    /products/            # list all  
GET    /products/{id}        # get one
GET    /products/{id}/orders # who bought this product
GET    /products/{id}/inventory    # current stock
PUT    /products/{id}/inventory    # update stock
```

SKU validation, auto inventory tracking. When you create a product it sets up inventory records automatically.

### Orders (`/orders`)
```
POST   /orders/              # create order
GET    /orders/              # list all
GET    /orders/{id}          # get one
GET    /orders/by-status/{status}     # filter by status  
GET    /orders/by-customer/{id}       # customer's orders
PUT    /orders/{id}/status   # update status
```

Creating orders automatically reduces inventory and updates customer order count. Validates customer/product exist first.

Status options: pending, completed, cancelled

### Users (`/users`)
```
POST   /users/               # create user
GET    /users/               # list all
GET    /users/{id}           # get one
GET    /users/{id}/with-roles        # includes roles
POST   /users/{user_id}/roles/{role_id}    # assign role
DELETE /users/{user_id}/roles/{role_id}    # remove role  
PUT    /users/{id}/activate  # activate account
PUT    /users/{id}/deactivate        # deactivate
```

Basic password hashing (SHA256 - should upgrade to bcrypt). Users can have multiple roles.

### Roles (`/roles`)
```
POST   /roles/               # create role
GET    /roles/               # list all
GET    /roles/{id}           # get one
GET    /roles/{id}/with-users        # who has this role
PUT    /roles/{id}           # update permissions
DELETE /roles/{id}           # delete (if no users have it)
```

Stores permissions as JSON. Can't delete roles that are still assigned.

### Transactions (`/transactions`)  
```
POST   /transactions/        # create transaction
GET    /transactions/        # list all
GET    /transactions/{id}    # get one
GET    /transactions/by-user/{id}    # by user
GET    /transactions/by-date-range/  # date filtering
PUT    /transactions/{id}    # update
DELETE /transactions/{id}    # delete
```

Tracks who created each transaction. Date range filtering for reports.

### Support Tickets (`/tickets`)
```
POST   /tickets/             # create ticket
GET    /tickets/             # list all
GET    /tickets/{id}         # get one
GET    /tickets/by-customer/{id}     # customer's tickets
GET    /tickets/by-status/{status}   # filter by status
GET    /tickets/by-priority/{priority}  # filter by priority
PUT    /tickets/{id}/status  # update status
PUT    /tickets/{id}/assign/{employee_id}   # assign to employee
PUT    /tickets/{id}/unassign        # remove assignment
DELETE /tickets/{id}         # delete
```

Status: open, in_progress, resolved, closed  
Priority: low, medium, high, urgent

Auto-sets resolved timestamp when status changes to resolved.

## Database tables

Main tables:
- customers - customer info
- products - product catalog  
- orders - sales transactions
- inventory - current stock levels
- inventory_history - audit trail for stock changes
- users - user accounts
- roles - permission roles
- user_roles - many-to-many junction
- transactions - financial records
- tickets - support tickets

Also have models for employees, departments, vendors, purchase_orders, invoices, accounts, audit_logs but no APIs yet.

## Tech stack

- FastAPI for the API layer
- PostgreSQL for database
- SQLAlchemy ORM 
- Pydantic for validation
- Docker for containerization
- Redis running but not used yet

## Business logic notes

When you create an order:
1. Validates customer and product exist
2. Checks inventory is available  
3. Uses product price if no sale price given
4. Reduces inventory by 1
5. Logs inventory change in history table
6. Increments customer order count
7. Sets order status to "pending"

Inventory history tracks everything - initial stock, sales, manual adjustments, etc.

User-role relationships are many-to-many so users can have multiple roles.

## Quick test commands

Start everything:
```bash
docker-compose up -d
```

Create a customer:
```bash
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

Create a product:  
```bash
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "sku": "LAP001", "price": 999.99, "quantity": 10}'
```

Create an order:
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "product_id": 1}'
```

## TODO / Future stuff

Need to build APIs for:
- Employee management
- Vendor/supplier management  
- Purchase orders
- Invoice generation
- Audit log viewing

Would be nice to have:
- Proper authentication (JWT tokens)
- File uploads for product images
- Email notifications
- Better reporting
- API rate limiting
- Redis caching

## Development notes

All models use singular names (Product not Products). 

Foreign keys reference table names (still plural): `ForeignKey("products.id")`  
Relationships reference class names (singular): `relationship("Product")`

Updated_at fields auto-update on changes where implemented.

Most endpoints validate related records exist before operations.

Error handling returns proper HTTP status codes with descriptive messages. 