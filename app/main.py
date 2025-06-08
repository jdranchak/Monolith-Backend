from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.customers import router as customer_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.api.transactions import router as transactions_router
from app.api.tickets import router as tickets_router


app = FastAPI(title="Monolith Backend API", version="1.0.0")
app.include_router(health_router)
app.include_router(customer_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(tickets_router)

@app.get("/") 
def read_root():
    return {"status": "API is up!", "message": "Monolith Backend with full CRUD operations"}


@app.get("/greeting")
def get_greeting():
    return {"message": "hello"}
