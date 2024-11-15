from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import customer_router
import os

app = FastAPI(
    title="FitKitchen API",
    description="API for FitKitchen Customer Management",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(customer_router.router)

@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to FitKitchen API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)