from fastapi import FastAPI, HTTPException
from routers import customer_router
import uvicorn

app = FastAPI(
    title="FitKitchen API",
    description="API for personalized catering service",
    version="1.0.0"
)

app.include_router(customer_router.router)

@app.get("/")
async def root() -> dict:
    return {"message": "Welcome to FitKitchen API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)