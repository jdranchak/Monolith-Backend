from fastapi import FastAPI
from app.api.health import router as health_router

app = FastAPI(title="Monolith Backend")
app.include_router(health_router)

@app.get("/") 
def read_root():
    return {"status": "API is up!"}


@app.get("/greeting")
def get_greeting():
    return {"message": "hello"}
