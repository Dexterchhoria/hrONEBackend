# E-commerce Backend API

A FastAPI-based backend application for an e-commerce platform with MongoDB integration. This application provides RESTful APIs for managing products and orders.

## Features

- **Product Management**: Create and list products with filtering capabilities
- **Order Management**: Create orders and retrieve user order history
- **MongoDB Integration**: Efficient data storage and retrieval
- **Pagination**: Built-in pagination support for all list endpoints
- **Input Validation**: Comprehensive request/response validation using Pydantic
- **Error Handling**: Proper HTTP status codes and error messages

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.11+**: Programming language
- **MongoDB**: NoSQL database for data storage
- **PyMongo**: Python driver for MongoDB
- **Pydantic**: Data validation and serialization

## Project Structure

```
├── main.py              # Main application file with all API endpoints
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Database Schema

### Products Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "price": "float",
  "size": "string",
  "available_quantity": "int"
}
```

### Orders Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": "int",
      "price": "float"
    }
  ],
  "total_amount": "float",
  "created_at": "ISO datetime string"
}
```

## API Endpoints

### 1. Create Product
- **Endpoint**: `POST /products`
- **Description**: Create a new product
- **Request Body**:
```json
{
  "name": "string",
  "price": 0.0,
  "size": "string",
  "available_quantity": 0
}
```
- **Response**: Created product with `_id`
- **Status Code**: 201

### 2. List Products
- **Endpoint**: `GET /products`
- **Description**: List products with optional filtering
- **Query Parameters**:
  - `name` (optional): Filter by product name (supports partial search)
  - `size` (optional): Filter by product size
  - `limit` (optional, default=10): Number of products to return
  - `offset` (optional, default=0): Number of products to skip
- **Response**: Paginated list of products
- **Status Code**: 200

### 3. Create Order
- **Endpoint**: `POST /orders`
- **Description**: Create a new order
- **Request Body**:
```json
{
  "user_id": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": 0
    }
  ]
}
```
- **Response**: Created order with calculated total amount
- **Status Code**: 201

### 4. List User Orders
- **Endpoint**: `GET /orders/{user_id}`
- **Description**: List orders for a specific user
- **Path Parameters**:
  - `user_id`: User ID to fetch orders for
- **Query Parameters**:
  - `limit` (optional, default=10): Number of orders to return
  - `offset` (optional, default=0): Number of orders to skip
- **Response**: Paginated list of user orders
- **Status Code**: 200

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- MongoDB instance (local or MongoDB Atlas)

### Local Development

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ecommerce-backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set environment variables**:
```bash
export MONGODB_URI="mongodb://localhost:27017"  # Or your MongoDB Atlas URI
```

5. **Run the application**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Deployment

#### MongoDB Atlas Setup
1. Create a free M0 cluster on [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a database user
3. Whitelist your IP address (or 0.0.0.0/0 for development)
4. Get your connection string

#### Deploy to Render/Railway
1. **For Render**:
   - Connect your GitHub repository
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `python main.py`
   - Add environment variable: `MONGODB_URI` with your Atlas connection string

2. **For Railway**:
   - Connect your GitHub repository
   - Railway will auto-detect Python and use the requirements.txt
   - Add environment variable: `MONGODB_URI` with your Atlas connection string

## API Documentation

Once the application is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative docs**: `http://localhost:8000/redoc`

## Key Features Implemented

### 1. **Robust Error Handling**
- Proper HTTP status codes
- Detailed error messages
- Input validation errors

### 2. **Efficient Database Queries**
- Indexed queries for better performance
- Proper MongoDB aggregation for complex operations
- Optimized pagination

### 3. **Inventory Management**
- Automatic quantity reduction when orders are placed
- Stock validation before order creation
- Prevents overselling

### 4. **Advanced Filtering**
- Case-insensitive partial name search using regex
- Size-based filtering
- Pagination support with has_next indicator

### 5. **Data Validation**
- Pydantic models for request/response validation
- ObjectId validation for MongoDB
- Type safety throughout the application

## Testing the APIs

### Example Requests

1. **Create a Product**:
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Headphones",
    "price": 99.99,
    "size": "large",
    "available_quantity": 50
  }'
```

2. **List Products**:
```bash
curl "http://localhost:8000/products?name=headphones&size=large&limit=5&offset=0"
```

3. **Create an Order**:
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "items": [
      {
        "product_id": "60f7b2b5c8d6f8b4c8d6f8b4",
        "quantity": 2
      }
    ]
  }'
```

4. **List User Orders**:
```bash
curl "http://localhost:8000/orders/user123?limit=10&offset=0"
```

## Health Check

The application includes a health check endpoint:
```bash
curl "http://localhost:8000/health"
```

## Environment Variables

- `MONGODB_URI`: MongoDB connection string (required)

## Performance Considerations

1. **Database Indexing**: Consider adding indexes on frequently queried fields
2. **Connection Pooling**: PyMongo handles connection pooling automatically
3. **Pagination**: Implemented to handle large datasets efficiently
4. **Error Handling**: Comprehensive error handling prevents crashes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is created for the HROne Backend Intern Hiring Task.