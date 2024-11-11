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
    data = read_customers()
    if not data["customers"]:
        return 1
    return max(customer["id"] for customer in data["customers"]) + 1

# API Routes
@router.get("/customers", response_model=List[Customer], tags=["customers"])
async def get_all_customers():
    try:
        data = read_customers()
        return data["customers"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customers/{customer_id}", response_model=Customer, tags=["customers"])
async def get_customer(customer_id: int):
    try:
        data = read_customers()
        customer = next((c for c in data["customers"] if c["id"] == customer_id), None)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customers", response_model=Customer, tags=["customers"])
async def create_customer(customer: CustomerCreate):
    try:
        data = read_customers()
        new_customer = customer.dict()
        new_customer["id"] = get_next_id()
        
        data["customers"].append(new_customer)
        write_customers(data)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/customers/{customer_id}", response_model=Customer, tags=["customers"])
async def update_customer(customer_id: int, updated_customer: CustomerCreate):
    try:
        data = read_customers()
        customer_idx = next((idx for idx, c in enumerate(data["customers"]) if c["id"] == customer_id), None)
        
        if customer_idx is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        updated_data = updated_customer.dict()
        updated_data["id"] = customer_id
        
        data["customers"][customer_idx] = updated_data
        write_customers(data)
        return updated_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/customers/{customer_id}", tags=["customers"])
async def delete_customer(customer_id: int):
    try:
        data = read_customers()
        customer = next((c for c in data["customers"] if c["id"] == customer_id), None)
        
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        data["customers"] = [c for c in data["customers"] if c["id"] != customer_id]
        write_customers(data)
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))