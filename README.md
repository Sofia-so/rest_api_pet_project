# Online Store REST API

A RESTful API for an online store built with Flask.
The project provides a RESTful API for user authentication, product and category management, and order processing with role-based access control.

**Project Status:** In Progress

## Technologies
- Python
- Flask
- SQLAlchemy
- PostgreSQL
- Alembic
- Marshmallow
- Flask-Smorest
- Flask-JWT-Extended 
- Git

## Current Features

- User registration and JWT authentication
- Role-based access control (Admin, Employee, and User)
- User profile management
- Category CRUD operations
- Product CRUD operations
- Product categorization, search, and inventory management
- Order management (create, view, update status, and cancel orders)
- Automatic total price calculation and inventory updates after order creation or cancellation
- Request and response validation with Marshmallow
- Interactive Swagger/OpenAPI documentation
- Database migrations with Alembic

## Requirements

- Python 3.12+
- PostgreSQL

## Installation and Running

### 1. Clone the repository

```bash
git clone https://github.com/Sofia-so/rest_api_pet_project.git
cd rest_api_pet_project
```

### 2. Create and activate a virtual environment

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URI=postgresql+psycopg://your_username:your_password@localhost:5432/your_database
ADMIN_PASSWORD=your_admin_password
```

### 5. Run database migrations

```bash
flask db upgrade
```

### 6. Start the application

```bash
flask --app app:create_app --debug run
```

The API will be available at:

- API: http://127.0.0.1:5000
- Swagger UI: http://127.0.0.1:5000/swagger-ui

---

## Author

**Sofia Sudarkova**

GitHub: https://github.com/Sofia-so  
Email: sudarkovasofia0@gmail.com
