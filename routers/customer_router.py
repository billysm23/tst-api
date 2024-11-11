from fastapi import APIRouter, HTTPException
import json
from typing import List, Dict, Optional
from pydantic import BaseModel

# Pydantic models for request and response
class CustomerBase(BaseModel):
    name: str
    age: int
    height: float
    weight: float
    health_goals: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

router = APIRouter()

# Helper functions for data operations
def read_customers() -> Dict:
    try:
        with open("data/customers.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"customers": []}

def write_customers(data: Dict) -> None:
    with open("data/customers.json", "w") as f:
        json.dump(data, f, indent=4)

def get_next_id() -> int:
    data = read_customers()
    if not data["customers"]:
        return 1
    return max(customer["id"] for customer in data["customers"]) + 1

# API Routes
@router.get("/customers", response_model=List[Customer])
async def get_all_customers():
    data = read_customers()
    return data["customers"]

@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    data = read_customers()
    customer = next((c for c in data["customers"] if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    data = read_customers()
    new_customer = customer.dict()
    new_customer["id"] = get_next_id()
    
    data["customers"].append(new_customer)
    write_customers(data)
    return new_customer

@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: int, updated_customer: CustomerCreate):
    data = read_customers()
    customer_idx = next((idx for idx, c in enumerate(data["customers"]) if c["id"] == customer_id), None)
    
    if customer_idx is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Preserve the ID while updating other fields
    updated_data = updated_customer.dict()
    updated_data["id"] = customer_id
    
    data["customers"][customer_idx] = updated_data
    write_customers(data)
    return updated_data

@router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int):
    data = read_customers()
    customer = next((c for c in data["customers"] if c["id"] == customer_id), None)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    data["customers"] = [c for c in data["customers"] if c["id"] != customer_id]
    write_customers(data)
    return {"message": "Customer deleted successfully"}