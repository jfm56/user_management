from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
import importlib
import logging.config
import os

from app.database import Database
from app.dependencies import get_settings
from app.routers import user_routes, email_routes
from app.utils.api_description import getDescription

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Load logging configuration
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="User Management",
    description=getDescription(),
    version="0.0.1",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
# CORS middleware configuration
# This middleware will enable CORS and allow requests from any origin
# It can be configured to allow specific methods, headers, and origins
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of origins that are allowed to access the server, ["*"] allows all
    allow_credentials=True,  # Support credentials (cookies, authorization headers, etc.)
    allow_methods=["*"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allowed HTTP headers
)

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    Database.initialize(settings.database_url, settings.debug)

# Add explicit exception handlers to make sure errors are properly returned
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services when the application starts."""
    logger.info("Initializing application services...")
    
    # Initialize Kafka consumer
    try:
        # Import here to avoid circular imports
        from app.tasks.kafka_consumers import start_kafka_consumers
        start_kafka_consumers()
        logger.info("Kafka consumer service initialized successfully")
    except ImportError:
        logger.warning("Kafka consumer module not available")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka consumer service: {e}")
    
    logger.info("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down."""
    logger.info("Shutting down application...")
    
    # Stop Kafka consumer
    try:
        from app.tasks.kafka_consumers import stop_kafka_consumers
        stop_kafka_consumers()
        logger.info("Kafka consumer service stopped successfully")
    except ImportError:
        logger.warning("Kafka consumer module not available")
    except Exception as e:
        logger.error(f"Error stopping Kafka consumer service: {e}")
    
    logger.info("Application shutdown complete")

# Include routers
app.include_router(user_routes.router)
app.include_router(email_routes.router)