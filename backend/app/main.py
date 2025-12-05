from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db import connect_to_mongo, close_mongo_connection
from app.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

# Initialize scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    
    # Initialize database indexes
    from app.models import initialize_indexes
    from app.core.db import get_database
    await initialize_indexes(get_database())
    
    # Configure APScheduler with MongoDB jobstore if URL provided
    if settings.SCHEDULER_JOBSTORE_URL:
        from pymongo import MongoClient
        mongo_client = MongoClient(settings.SCHEDULER_JOBSTORE_URL)
        jobstores = {
            'default': MongoDBJobStore(
                database=settings.MONGODB_DB_NAME,
                collection='apscheduler_jobs',
                client=mongo_client
            )
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        scheduler.configure(jobstores=jobstores, executors=executors)
    
    scheduler.start()
    print("✅ APScheduler started")
    
    # Start auto-cancel cron job
    from app.services.scheduler_service import start_auto_cancel_cron
    start_auto_cancel_cron(scheduler)
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    print("❌ APScheduler shutdown")
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Clinic Management System API",
    description="Backend API for Clinic Management System with appointment scheduling",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Clinic Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers
from app.routes import auth, users, appointments, twilio_webhook, time
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(twilio_webhook.router, prefix="/api/v1/twilio", tags=["Twilio"])
app.include_router(time.router, prefix="/api/v1/time", tags=["Time"])


# Export scheduler for use in other modules
def get_scheduler():
    return scheduler
