from fastapi import APIRouter, HTTPException
import json
import os
from typing import List, Dict, Optional
from pydantic import BaseModel

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
def get_data_file_path() -> str:
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(current_dir)
    # Construct path to data file
    return os.path.join(project_root, "data", "customers.json")

def initialize_data_file():
    data_file = get_data_file_path()
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            json.dump({"customers": []}, f)

# Helper functions for data operations
def read_customers() -> Dict:
    try:
        initialize_data_file()
        with open(get_data_file_path(), "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading customers: {e}")
        return {"customers": []}

def write_customers(data: Dict) -> None:
    try:
        initialize_data_file()
        with open(get_data_file_path(), "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error writing customers: {e}")
        raise HTTPException(status_code=500, detail="Error saving data")

def get_next_id() -> int:
    return max([customer["id"] for customer in CUSTOMERS["customers"]], default=0) + 1

# Root endpoint
@router.get("/")
async def root():
    return {"message": "FitKitchen API is running"}

# Get all customers
@router.get("/api/customers", response_model=List[Customer])
async def get_customers():
    return CUSTOMERS["customers"]

# Get single customer
@router.get("/api/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    customer = next((c for c in CUSTOMERS["customers"] if c["id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Create customer
@router.post("/api/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    new_customer = customer.dict()
    new_customer["id"] = get_next_id()
    CUSTOMERS["customers"].routerend(new_customer)
    return new_customer

# Update customer
@router.put("/api/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: int, customer: CustomerCreate):
    customer_idx = next((idx for idx, c in enumerate(CUSTOMERS["customers"]) if c["id"] == customer_id), None)
    if customer_idx is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    updated_customer = customer.dict()
    updated_customer["id"] = customer_id
    CUSTOMERS["customers"][customer_idx] = updated_customer
    return updated_customer

# Delete customer
@router.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: int):
    customer_idx = next((idx for idx, c in enumerate(CUSTOMERS["customers"]) if c["id"] == customer_id), None)
    if customer_idx is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    CUSTOMERS["customers"].pop(customer_idx)
    return {"message": "Customer deleted successfully"}