from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import re

# Initialize FastAPI app
app = FastAPI(title="E-commerce Backend API", version="1.0.0")

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "ecommerce_db"

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
products_collection = db.products
orders_collection = db.orders

# Pydantic models for request/response
class ProductCreate(BaseModel):
    name: str
    price: float
    size: str
    available_quantity: int

class Product(BaseModel):
    _id: str
    name: str
    price: float
    size: str
    available_quantity: int

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItem]

class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
    _id: str
    user_id: str
    items: List[OrderItemResponse]
    total_amount: float
    created_at: str

class ProductsListResponse(BaseModel):
    data: List[Product]
    page: Dict[str, Any]

class OrdersListResponse(BaseModel):
    data: List[Order]
    page: Dict[str, Any]

# Helper function to convert ObjectId to string
def serialize_document(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

# Helper function to serialize list of documents
def serialize_documents(docs):
    return [serialize_document(doc) for doc in docs]

@app.get("/")
async def root():
    return {"message": "E-commerce Backend API is running"}

@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        # Insert product into MongoDB
        product_dict = product.dict()
        result = products_collection.insert_one(product_dict)
        
        # Retrieve the created product
        created_product = products_collection.find_one({"_id": result.inserted_id})
        created_product = serialize_document(created_product)
        
        return created_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@app.get("/products", status_code=200)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports partial search)"),
    size: Optional[str] = Query(None, description="Filter by product size"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    """List products with optional filtering and pagination"""
    try:
        # Build filter query
        filter_query = {}
        
        if name:
            # Use regex for partial matching (case-insensitive)
            filter_query["name"] = {"$regex": re.escape(name), "$options": "i"}
        
        if size:
            filter_query["size"] = size
        
        # Get total count for pagination info
        total_count = products_collection.count_documents(filter_query)
        
        # Execute query with pagination
        products = products_collection.find(filter_query).sort("_id", 1).skip(offset).limit(limit)
        products_list = serialize_documents(list(products))
        
        # Prepare response
        response = {
            "data": products_list,
            "page": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_next": offset + limit < total_count
            }
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order"""
    try:
        total_amount = 0.0
        order_items = []
        
        # Validate products and calculate total
        for item in order.items:
            # Find product
            try:
                product_id = ObjectId(item.product_id)
            except:
                raise HTTPException(status_code=400, detail=f"Invalid product_id: {item.product_id}")
            
            product = products_collection.find_one({"_id": product_id})
            if not product:
                raise HTTPException(status_code=404, detail=f"Product not found: {item.product_id}")
            
            # Check availability
            if product["available_quantity"] < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient quantity for product {item.product_id}. Available: {product['available_quantity']}, Requested: {item.quantity}"
                )
            
            # Calculate item total
            item_total = product["price"] * item.quantity
            total_amount += item_total
            
            # Add to order items
            order_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": product["price"]
            })
            
            # Update product quantity
            products_collection.update_one(
                {"_id": product_id},
                {"$inc": {"available_quantity": -item.quantity}}
            )
        
        # Create order document
        order_doc = {
            "user_id": order.user_id,
            "items": order_items,
            "total_amount": round(total_amount, 2),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert order
        result = orders_collection.insert_one(order_doc)
        
        # Return created order
        created_order = orders_collection.find_one({"_id": result.inserted_id})
        created_order = serialize_document(created_order)
        
        return created_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@app.get("/orders/{user_id}", status_code=200)
async def list_orders(
    user_id: str = Path(..., description="User ID to fetch orders for"),
    limit: int = Query(10, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    """List orders for a specific user"""
    try:
        # Build filter query
        filter_query = {"user_id": user_id}
        
        # Get total count
        total_count = orders_collection.count_documents(filter_query)
        
        # Execute query with pagination
        orders = orders_collection.find(filter_query).sort("_id", 1).skip(offset).limit(limit)
        orders_list = serialize_documents(list(orders))
        
        # Prepare response
        response = {
            "data": orders_list,
            "page": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_next": offset + limit < total_count
            }
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)