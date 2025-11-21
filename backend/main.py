"""FastAPI main application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.database import connect_to_mongo, close_mongo_connection
from backend.routes import contacts, templates, campaigns, emails, dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting up MailerSlave API...")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down MailerSlave API...")
    await close_mongo_connection()


app = FastAPI(
    title="MailerSlave API",
    description="Email campaign management and automation API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(emails.router, prefix="/api/emails", tags=["Emails"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MailerSlave API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
