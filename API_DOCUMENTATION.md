# E-commerce API Documentation



This is a complete Django REST API for an e-commerce system with the following features:
- **JWT-based authentication**
- **Product catalog with categories**
- **Shopping cart and order management**
- **Real-time notifications via WebSockets**
- **Redis caching for performance**
- **Advanced filtering and pagination**
- **Admin interface for management**

##  Table of Contents

1. [Setup & Installation](#setup--installation)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [WebSocket Connections](#websocket-connections)
5. [Admin Interface](#admin-interface)
6. [Testing](#testing)

## 🛠 Setup & Installation

### Prerequisites
- Python 3.8+
- Django 4.2.7
- PostgreSQL (for production) or SQLite (for development)
- Redis (for production caching and WebSockets)

### Installation Steps

1. **Clone and setup virtual environment:**
```bash
git clone <repository>
cd ecommerce_api
python -m venv new_venv
source new_venv/bin/activate  
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup database:**
```bash
python manage.py migrate
python manage.py create_initial_data
```

4. **Run development server:**
```bash
python manage.py runserver
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login
- **Endpoint:** `POST /api/users/login/`
- **Body:**
```json
{
    "email": "admin@example.com",
    "password": "password123"
}
```
- **Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "user": {
        "id": 1,
        "email": "admin@example.com",
        "username": "admin",
        "first_name": "",
        "last_name": ""
    }
}
```

### Using Authentication
Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## 📡 API Endpoints

### User Management

#### User Registration
- **POST** `/api/users/register/`
- **Body:**
```json
{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### User Profile
- **GET** `/api/users/profile/` - Get user profile
- **PUT** `/api/users/update/` - Update user profile

#### User Order History
- **GET** `/api/users/orders/` - Get user's order history

#### Token Refresh
- **POST** `/api/users/token/refresh/`
- **Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

### Product Management

#### Products
- **GET** `/api/products/` - List all products (with pagination and filtering)
- **POST** `/api/products/` - Create new product (admin only)
- **GET** `/api/products/{id}/` - Get product details
- **PUT** `/api/products/{id}/` - Update product (admin only)
- **DELETE** `/api/products/{id}/` - Delete product (admin only)

#### Product Filtering & Search
Query parameters for `/api/products/`:
- `?search=laptop` - Search in name/description
- `?category=1` - Filter by category ID
- `?category_name=Electronics` - Filter by category name
- `?min_price=100&max_price=1000` - Price range
- `?in_stock=true` - Only in-stock products
- `?ordering=-created_at` - Sort by creation date (desc)
- `?page=2&page_size=10` - Pagination

#### Categories
- **GET** `/api/products/categories/` - List all categories
- **POST** `/api/products/categories/` - Create category (admin only)
- **GET** `/api/products/categories/{id}/` - Get category details
- **PUT** `/api/products/categories/{id}/` - Update category (admin only)
- **DELETE** `/api/products/categories/{id}/` - Delete category (admin only)

### Shopping Cart

#### Cart Operations
- **GET** `/api/orders/cart/` - Get user's cart
- **POST** `/api/orders/cart/add/` - Add item to cart
- **PUT** `/api/orders/cart/items/{id}/` - Update cart item quantity
- **DELETE** `/api/orders/cart/items/{id}/` - Remove item from cart

#### Add to Cart
- **POST** `/api/orders/cart/add/`
- **Body:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

### Order Management

#### Orders
- **GET** `/api/orders/` - List user's orders
- **GET** `/api/orders/{id}/` - Get order details
- **POST** `/api/orders/create/` - Create order from cart

#### Create Order
- **POST** `/api/orders/create/`
- **Body:**
```json
{
    "shipping_address": "123 Main St, City, Country"
}
```

#### Update Order Status (Admin only)
- **PUT** `/api/orders/{id}/update-status/`
- **Body:**
```json
{
    "status": "shipped"
}
```

Status options: `pending`, `shipped`, `delivered`, `cancelled`

### Notifications

#### Notifications
- **GET** `/api/notifications/` - List user's notifications
- **GET** `/api/notifications/{id}/` - Get notification details
- **PUT** `/api/notifications/{id}/` - Mark notification as read

## 🔄 WebSocket Connections

### Real-time Notifications

Connect to WebSocket for real-time order status updates:

**WebSocket URL:** `ws://localhost:8000/ws/notifications/?token=<jwt_access_token>`

#### Connection Messages:
```json
// Connection established
{
    "type": "connection_established",
    "message": "Connected to notifications for user user@example.com"
}

// Order status update
{
    "type": "order_status_update",
    "order_id": 1,
    "status": "shipped",
    "status_display": "Shipped",
    "message": "Your order #1 status has been updated to Shipped"
}
```

#### Client Messages:
```json
// Mark notification as read
{
    "type": "mark_notification_read",
    "notification_id": 1
}

// Ping to keep connection alive
{
    "type": "ping"
}
```

## 🛡 Admin Interface

Access the Django admin at: `http://localhost:8000/admin/`

**Admin credentials:**
- Email: `admin@example.com`
- Password: `password123`

### Admin Features:
- **User Management:** View and manage users and profiles
- **Product Management:** Add, edit, delete products and categories
- **Order Management:** View orders, update status, manage cart items
- **Notifications:** View and manage user notifications

## 📊 Database Models

### User Model
- Custom user model with email authentication
- Profile model with avatar and bio
- Fields: email, username, first_name, last_name, phone, address, date_of_birth

### Product Models
- **Category:** name, description, image
- **Product:** name, description, price, stock, category, image, sku
- Optimized with database indexes and caching

### Order Models
- **Cart:** User-specific shopping cart
- **CartItem:** Items in cart with quantities
- **Order:** Order with status tracking
- **OrderItem:** Items in order with prices at purchase time

### Notification Model
- Real-time and database notifications
- Types: order_status_update, order_created, product_back_in_stock, general

## 🔍 Performance Features

### Caching Strategy
- **Product caching:** 1-hour cache for product listings
- **Category caching:** 1-hour cache for categories
- **Cache invalidation:** Automatic when products/categories are modified

### Database Optimization
- **Indexes:** On product name, category, price, stock fields
- **Query optimization:** select_related and prefetch_related for complex queries
- **Pagination:** 10 items per page to handle large datasets

## 🧪 Testing

### Test the API with curl:

#### 1. Register a user:
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "password_confirm": "testpassword123"
  }'
```

#### 2. Login and get token:
```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

#### 3. List products:
```bash
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

#### 4. Add to cart:
```bash
curl -X POST http://localhost:8000/api/orders/cart/add/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

#### 5. Create order:
```bash
curl -X POST http://localhost:8000/api/orders/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Test Street, Test City, Test Country"
  }'
```

## 🚀 Production Deployment

### Environment Variables

Create a `.env` file:
```env
# Database Configuration (PostgreSQL)
DB_NAME=ecommerce_db
DB_USER=ecommerce_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# Django Settings
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Production Settings Changes:
1. Uncomment PostgreSQL database settings
2. Uncomment Redis cache and channel layer settings
3. Set `DEBUG=False`
4. Configure `ALLOWED_HOSTS`
5. Set up proper static files serving
6. Configure HTTPS for WebSocket connections (wss://)

## 📈 API Response Examples

### Product List Response:
```json
{
    "count": 20,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": "999.99",
            "stock": 50,
            "category": 2,
            "category_name": "Electronics",
            "image": null,
            "sku": "LAPTOP001",
            "is_in_stock": true,
            "created_at": "2025-01-20T10:30:00Z"
        }
    ]
}
```

### Order Response:
```json
{
    "id": 1,
    "user_email": "test@example.com",
    "total_price": "1999.98",
    "status": "pending",
    "shipping_address": "123 Test Street",
    "order_items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Laptop",
                "price": "999.99"
            },
            "quantity": 2,
            "price": "999.99",
            "total_price": "1999.98"
        }
    ],
    "total_quantity": 2,
    "created_at": "2025-01-20T11:00:00Z"
}
```

## 🔧 Development Tools

- **Django Admin:** Full admin interface at `/admin/`
- **API Browsing:** Django REST Framework browsable API
- **WebSocket Testing:** Use tools like WebSocket King or browser console
- **Database:** SQLite for development, PostgreSQL for production
- **Caching:** Dummy cache for development, Redis for production

---

**🎉 Your complete e-commerce API is ready!** 

The API provides all the required features including JWT authentication, product management, shopping cart, order processing, real-time notifications, caching, and advanced filtering with pagination.
