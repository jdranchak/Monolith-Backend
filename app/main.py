from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.customers import router as customer_router
from app.api.products import router as products_router


app = FastAPI()
app.include_router(health_router)
app.include_router(customer_router)
app.include_router(products_router)

@app.get("/") 
def read_root():
    return {"status": "API is up!"}


@app.get("/greeting")
def get_greeting():
    return {"message": "hello"}
