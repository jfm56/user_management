# User Management System

## Overview

The User Management System is a robust, scalable application for managing user accounts and handling user-related operations. It provides comprehensive user authentication, authorization, and profile management capabilities with a modern event-driven architecture for notifications.

## Latest Updates

### May 2025

- **Database Migration Improvements**: Added conditional checks to prevent duplicate table errors during migrations
- **API Form Interface Enhancements**: Implemented Pydantic models with schema examples for improved Swagger UI forms
- **Nginx Configuration Upgrade**: Updated to use Docker's internal DNS resolver for better container networking
- **Enum Dropdowns**: Added dropdown selection menus for role fields in API forms

![User Management System Architecture](https://via.placeholder.com/800x400?text=User+Management+System+Architecture)

## Key Features

- **User Authentication & Authorization**
  - Secure JWT-based authentication
  - Role-based access control (ADMIN, MANAGER, AUTHENTICATED, ANONYMOUS)
  - Account verification via email
  - Protection against brute force attacks with account locking

- **User Profile Management**
  - Complete user profile creation and editing
  - Professional status tracking
  - Social media integration (GitHub, LinkedIn)

- **Event-Driven Email Notifications**
  - Asynchronous email processing using Celery and Kafka
  - Reliable, scalable notification system
  - Templates for various notification types (verification, account status, role changes)

- **API-First Design**
  - RESTful API endpoints for all functionality
  - Comprehensive Swagger/OpenAPI documentation
  - Pagination for list endpoints

- **Testing & Quality Assurance**
  - 80+ automated tests
  - CI/CD pipeline with GitHub Actions
  - Docker-based deployment

## System Architecture

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Message Broker**: Kafka
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx
- **Testing**: pytest

### Event-Driven Email Architecture

The system implements an event-driven architecture for email notifications using Kafka and Celery:

1. **Topic Initialization**: Required Kafka topics are automatically created during container startup
2. **Event Publishing**: User-related events (verification, account status changes, role changes) are published to Kafka topics
3. **Event Consumption**: Kafka consumers process events and trigger Celery tasks
4. **Asynchronous Processing**: Celery workers handle email generation and delivery
5. **Fault Tolerance**: Failed events can be retried, with graceful degradation to direct email sending when needed

#### Kafka Topics

The system uses the following Kafka topics:

- `user-email-notifications`: For all email-related events
- `user-account-events`: For user account creation, deletion, and status changes
- `user-role-changes`: For role assignment and permission changes
- `user-verification-events`: For email verification and password reset events

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/user-management.git
cd user-management

# Start the services with automatic Kafka topic initialization
./start-app.sh

# Access the API at http://localhost:8000/docs
```

Alternatively, if you want to start services manually:

```bash
# Start Kafka and Zookeeper first
docker compose up -d zookeeper kafka

# Initialize Kafka topics
./kafka-init.sh

# Start remaining services
docker compose up -d
```

### Environment Configuration

Create a `.env` file with the following configurations (modify as needed):

```
DATABASE_URL=postgresql+asyncpg://user:password@postgres/myappdb
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SERVER_BASE_URL=http://localhost
JWT_SECRET_KEY=your_jwt_secret_key
```
   ```

4. Run database migrations:
   ```bash
   docker compose exec fastapi alembic upgrade head
   ```

5. Access the application:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Web Interface: http://localhost:80
   - PGAdmin: http://localhost:5050 (admin@example.com / adminpassword)

### Development Setup

1. For development, you can run the individual components locally:
   ```bash
   # Start the FastAPI development server
   ./start.sh
   
   # Start the Celery worker
   ./start_celery.sh
   ```

2. Running tests:
   ```bash
   docker compose exec fastapi pytest
   ```

3. Managing database migrations:
   ```bash
   # Apply all pending migrations
   docker compose exec fastapi alembic upgrade head
   
   # Create a new migration
   docker compose exec fastapi alembic revision -m "your migration description"
   ```
   
   Note: The migration system now includes guards against duplicate table errors with conditional checks in the scripts.

## Developer Guidelines

### Architecture & Code Organization

The project implements a hybrid architecture combining Clean Architecture principles with Event-Driven Design:

#### Architecture Patterns

1. **Clean Architecture Layer Separation**
   - Domain-driven design with clear separation of concerns
   - Business logic isolated in service layer
   - Data access and API endpoints in separate layers

2. **Event-Driven Notification System**
   - Kafka topics for message distribution
   - Celery workers for asynchronous processing
   - Producers and consumers decoupled for scalability

3. **JWT-Based Authentication & Authorization**
   - Token-based security with role-based permissions
   - Custom exception handling for proper error code propagation
   - Nginx configured for secure header passing

4. **Resilient Data Access Layer**
   - Conditional database migrations with idempotency checks
   - Asynchronous database operations with SQLAlchemy
   - Transaction management for data integrity

#### Directory Structure

```
user_management/
├── app/                  # Main application code
│   ├── dependencies/    # FastAPI dependencies for DI
│   ├── models/          # SQLAlchemy database models
│   ├── routers/         # API endpoints with input validation
│   ├── schemas/         # Pydantic validation schemas
│   ├── services/        # Business logic & transaction handling
│   ├── tasks/           # Celery async task definitions
│   └── utils/           # Helper functions & common utilities
├── settings/            # Environment-specific configurations
├── nginx/               # Web server & proxy configurations
├── alembic/             # Database migration scripts
├── email_templates/     # HTML & text email templates
├── tests/               # Test suite organized by component
└── scripts/             # Utility scripts for deployment & setup
```

### Coding Standards

- Follow PEP 8 standards for Python code
- Use type hints for all function parameters and return values
- Write docstrings for all modules, classes, and functions
- Maintain test coverage for new features

## Troubleshooting

### Authentication Issues

If you encounter 401 Unauthorized errors returning as 500 Internal Server Errors:

1. **Nginx Configuration**: Ensure that Nginx is correctly passing the error codes from the FastAPI app without modification. Check the `nginx/nginx.conf` file. The recent update adds Docker's internal DNS resolver to avoid stale IP references:
   ```nginx
   # Use Docker DNS resolver for dynamic upstream resolution
   resolver 127.0.0.11 valid=30s;
   set $backend fastapi:8000;
   
   location / {
       proxy_pass http://$backend;
       # Other proxy settings...
   }
   ```

2. **FastAPI Exception Handlers**: The application defines custom exception handlers for authentication errors. Make sure they're correctly registered in `app/main.py`.

3. **JWT Token Issues**: Verify that your JWT tokens have the correct format and are not expired. Use the included token generation tools for testing.

### Event Processing Issues

If email notifications are not being sent:

1. **Kafka Topics**: The system automatically creates all required Kafka topics during startup. To manually verify existing topics:
   ```bash
   docker compose exec kafka kafka-topics --list --bootstrap-server kafka:29092
   ```
   
   The following topics should be available:
   - user-email-notifications
   - user-account-events
   - user-role-changes
   - user-verification-events

2. **Celery Worker**: Check if the Celery worker is running and processing tasks:
   ```bash
   docker compose logs celery-worker
   ```

3. **API Form Fields**: If Swagger UI forms don't show expected input fields, check that your route handlers use Pydantic models for request bodies rather than manually parsing from the request object.

4. **Database Migration Issues**: If you encounter database migration conflicts or errors:
   ```bash
   # Check current migration status
   docker compose exec fastapi alembic current
   
   # View migration history
   docker compose exec fastapi alembic history
   ```

3. **SMTP Configuration**: Verify your SMTP settings in the `.env` file or Docker environment variables.

## API Documentation

The API documentation is available at `/docs` (Swagger UI) or `/redoc` (ReDoc) when the application is running. These provide interactive documentation for all API endpoints.

## Contributing

We welcome contributions to the User Management System! Here's how you can help:

1. **Report Issues**: Open an issue for any bugs or feature requests you may have.

2. **Submit Pull Requests**: Feel free to fork the repository and submit pull requests for bug fixes or new features.

3. **Coding Guidelines**:
   - Write tests for new features or bug fixes
   - Ensure all tests pass before submitting a pull request
   - Follow the project's coding standards
   - Update documentation as needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

