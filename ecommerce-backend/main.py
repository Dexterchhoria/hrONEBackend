from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
import re

# 🌱 Start_the_FastAPI _journey_with_life
app = FastAPI(title="E-commerce Backend API", version="1.0.0")

# 🔌 Connect_to_MongoDB,_our _data _home
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "ecommerce_db"

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
products_collection = db.products
orders_collection = db.orders

# 📦 Define_what_a_product_looks_like
class ProductCreate(BaseModel):
    name: str
    price: float
    size: str
    available_quantity: int

# 📄 Product response model with _id included
class Product(BaseModel):
    _id: str
    name: str
    price: float
    size: str
    available_quantity: int

# 🛒 Structure_of_each_order_item
class OrderItem(BaseModel):
    product_id: str
    quantity: int

# 🧾 Order_create_model_for_users
class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItem]

# 🧾 Detail_each_item_in_the_order
class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    price: float

# 📦 Final_structure_of_order_response
class Order(BaseModel):
    _id: str
    user_id: str
    items: List[OrderItemResponse]
    total_amount: float
    created_at: str

# 📃 Response_for_listing_products
class ProductsListResponse(BaseModel):
    data: List[Product]
    page: Dict[str, Any]

# 📃 Response_for_listing_orders
class OrdersListResponse(BaseModel):
    data: List[Order]
    page: Dict[str, Any]

# 🔄 Convert_ObjectId_to_string_format
def serialize_document(doc):
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

# 🔁 Convert_all_documents_in_a_list
def serialize_documents(docs):
    return [serialize_document(doc) for doc in docs]

# 🎯 Root_path,_just _a _warm_greeting
@app.get("/")
async def root():
    return {"message": "E-commerce Backend API is running"}

# 🛍️ Create_a_new_product_in_DB
@app.post("/products", status_code=201)
async def create_product(product: ProductCreate):
    try:
        product_dict = product.dict()
        result = products_collection.insert_one(product_dict)
        created_product = products_collection.find_one({"_id": result.inserted_id})
        created_product = serialize_document(created_product)
        return created_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

# 📦 List_all_products_with_optional_filters
@app.get("/products", status_code=200)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports partial search)"),
    size: Optional[str] = Query(None, description="Filter by product size"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    try:
        filter_query = {}

        if name:
            filter_query["name"] = {"$regex": re.escape(name), "$options": "i"}

        if size:
            filter_query["size"] = size

        total_count = products_collection.count_documents(filter_query)
        products = products_collection.find(filter_query).sort("_id", 1).skip(offset).limit(limit)
        products_list = serialize_documents(list(products))

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

# 🧾 Create_an_order_for_a_user
@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate):
    try:
        total_amount = 0.0
        order_items = []

        for item in order.items:
            try:
                product_id = ObjectId(item.product_id)
            except:
                raise HTTPException(status_code=400, detail=f"Invalid product_id: {item.product_id}")

            product = products_collection.find_one({"_id": product_id})
            if not product:
                raise HTTPException(status_code=404, detail=f"Product not found: {item.product_id}")

            if product["available_quantity"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient quantity for product {item.product_id}. Available: {product['available_quantity']}, Requested: {item.quantity}"
                )

            item_total = product["price"] * item.quantity
            total_amount += item_total

            order_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": product["price"]
            })

            products_collection.update_one(
                {"_id": product_id},
                {"$inc": {"available_quantity": -item.quantity}}
            )

        order_doc = {
            "user_id": order.user_id,
            "items": order_items,
            "total_amount": round(total_amount, 2),
            "created_at": datetime.utcnow().isoformat()
        }

        result = orders_collection.insert_one(order_doc)
        created_order = orders_collection.find_one({"_id": result.inserted_id})
        created_order = serialize_document(created_order)

        return created_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

# 📜 List_orders_placed_by_a_user
@app.get("/orders/{user_id}", status_code=200)
async def list_orders(
    user_id: str = Path(..., description="User ID to fetch orders for"),
    limit: int = Query(10, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    try:
        filter_query = {"user_id": user_id}
        total_count = orders_collection.count_documents(filter_query)
        orders = orders_collection.find(filter_query).sort("_id", 1).skip(offset).limit(limit)
        orders_list = serialize_documents(list(orders))

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

# ❤️ Health_check_to_monitor_service
@app.get("/health")
async def health_check():
    try:
        client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# ▶️ Run_the_app_locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
