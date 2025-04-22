# Field Services Application

A comprehensive field service management application designed for fit-out project management. This application combines messaging, documentation, project management, inventory tracking, and more into a unified platform.

## Features

- **User Management**: Role-based access control, authentication, and authorization
- **Project Management**: Project tracking with status, timeline, and budget
- **Work Order Management**: Detailed work orders linked to projects
- **Customer Management**: Company and contact management
- **Technician Management**: Skills, certifications, and location tracking
- **Inventory Management**: Track inventory levels and manage stock
- **Document Management**: Version control and approval workflows
- **Communication Tools**: Internal messaging and WhatsApp integration
- **Billing System**: Invoice generation and payment tracking
- **Training System**: Course management and certification tracking
- **Reporting**: Customizable dashboards and analytics

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (recommended) or SQLite for development
- Redis (for Celery task queue)

### Step 1: Clone the repository

```bash
git clone https://github.com/yourusername/field_services_app.git
cd field_services_app
```

### Step 2: Create a virtual environment

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -e .
# Or alternatively
pip install -r requirements.txt
```

### Step 4: Set up environment variables

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=django-insecure-w3k8$f7d9a4%h2j6l5!p0r1t2y3u4i7o8p9@#$%^&*()
DATABASE_URL=postgresql://postgre:K9121&6274k@localhost:5432/field_services
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 5: Run database migrations

```bash
python manage.py migrate
```

### Step 6: Create a superuser

```bash
python manage.py createsuperuser
```

### Step 7: Start the development server

```bash
python manage.py runserver
```

## Usage

Access the application at http://localhost:8000/

- Admin interface: http://localhost:8000/admin/
- API documentation: http://localhost:8000/swagger/ or http://localhost:8000/redoc/

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
black .
isort .
```

## Deployment

For production deployment, additional settings need to be configured:

- Set `DEBUG=False`
- Configure a production-ready database
- Set up proper HTTPS with certificates
- Configure static files serving
- Set up a task queue with Celery and Redis

## Project Structure

```
field_services_app/
├── config/                   # Main Django project settings
├── apps/                     # Application modules
│   ├── users/                # User management
│   ├── projects/             # Project management
│   ├── customers/            # Customer management
│   ├── work_orders/          # Work order management
│   ├── technicians/          # Field technician management
│   ├── inventory/            # Inventory management
│   ├── documents/            # Document management
│   ├── communication/        # Internal messaging
│   ├── whatsapp/             # WhatsApp integration
│   ├── billing/              # Billing and invoicing
│   ├── training/             # Training and certification
│   └── reports/              # Reporting and dashboards
├── templates/                # HTML templates
└── static/                   # Static assets
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the development team.
