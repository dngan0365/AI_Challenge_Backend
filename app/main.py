import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import database
from app.router import health, history, query, session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Query API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Startup / Shutdown Events
# -------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Initializing DB pool...")
    await database.init_async_pool()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Closing DB pool...")
    await database.close_async_pool()

# Routers
app.include_router(session.router, prefix="/api", tags=["Sessions"])
app.include_router(query.router, prefix="/api", tags=["Queries"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(health.router, tags=["Health"])
