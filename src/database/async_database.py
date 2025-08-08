import asyncio
import os
import time
import uuid
import jwt
import json
import logging
import ssl
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials

from databricks.sdk import WorkspaceClient
from sqlalchemy import URL, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Set up logging with timestamps and thread info
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d - %(threadName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('utility_database')

# Import secure credential management
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.secure_credentials import get_secure_credentials, setup_secure_environment

# Set up secure environment
setup_secure_environment()

# Load configuration securely
config = get_secure_credentials()

# Environment configuration (now using secure environment variables)
SERVICE_NAME = os.getenv("SERVICE_NAME", "LakeFusionDBService")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_DAPI = os.getenv("LAKEFUSION_DATABRICKS_DAPI")
DATABRICKS_DATABASE_INSTANCE = os.getenv("DATABRICKS_DATABASE_INSTANCE")
DATABRICKS_DATABASE_NAME = os.getenv("DATABRICKS_DATABASE_NAME", "databricks_postgres")
DATABRICKS_DATABASE_PORT = int(os.getenv("DATABRICKS_DATABASE_PORT", "5432"))
DATABRICKS_DATABASE_HOST = os.getenv("DATABRICKS_DATABASE_HOST")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3000"))

# Global variables
engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None
workspace_client: WorkspaceClient | None = None
database_instance = None
app_name: str = SERVICE_NAME

# Token management for background refresh
postgres_password: str | None = None
last_password_refresh: float = 0
token_refresh_task: asyncio.Task | None = None

async def refresh_token_background():
    global postgres_password, last_password_refresh, workspace_client, database_instance

    while True:
        try:
            await asyncio.sleep(50 * 60)  # Refresh every 50 minutes
            logger.info("Background token refresh: Generating fresh PostgreSQL OAuth token")

            cred = workspace_client.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[database_instance.name],
            )
            postgres_password = cred.token
            last_password_refresh = time.time()
            logger.info("Background token refresh: Token updated successfully")

        except Exception as e:
            logger.error(f"Background token refresh failed: {e}")

def init_engine():
    global engine, AsyncSessionLocal, workspace_client, database_instance, postgres_password, last_password_refresh

    try:
        # Get DB_TYPE from environment each time
        db_type = os.environ.get("DB_TYPE", "mysql").lower()
        logger.debug(f"Initializing engine with DB_TYPE: {db_type}")
        
        if db_type == 'lakebase':
            logger.info("Initializing Lakebase connection...")
            
            # Check if we have valid Databricks credentials
            if DATABRICKS_HOST == "https://your-workspace.cloud.databricks.com" or DATABRICKS_DAPI == "dapi_your_token_here":
                logger.error("Invalid Databricks credentials. Please set up your lakebase_credentials.conf file or environment variables.")
                raise RuntimeError("Invalid Databricks credentials")
            
            logger.debug(f"Using Databricks host: {DATABRICKS_HOST}")
            workspace_client = WorkspaceClient(
                host=DATABRICKS_HOST,
                token=DATABRICKS_DAPI
            )

            logger.debug(f"Getting database instance: {DATABRICKS_DATABASE_INSTANCE}")
            database_instance = workspace_client.database.get_database_instance(
                name=DATABRICKS_DATABASE_INSTANCE
            )

            logger.debug("Generating database credential...")
            cred = workspace_client.database.generate_database_credential(
                request_id=str(uuid.uuid4()), instance_names=[database_instance.name]
            )
            postgres_password = cred.token
            last_password_refresh = time.time()
            logger.info("Database: Initial credentials generated")

            decoded_token = jwt.decode(
                cred.token, options={"verify_signature": False}
            )
            username = decoded_token.get('sub', '')

            url = URL.create(
                drivername="postgresql+asyncpg",  # Use asyncpg for async support
                username=username,
                password=postgres_password,  # Set initial password
                host=DATABRICKS_DATABASE_HOST,  # Use secure environment variable
                port=DATABRICKS_DATABASE_PORT,
                database=DATABRICKS_DATABASE_NAME,
            )

            logger.debug(f"Creating engine with URL: {url}")
            
            # Create SSL context that accepts self-signed certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            engine = create_async_engine(  # Use async engine
                url,
                pool_pre_ping=True,
                echo=True,  # Enable SQL logging
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                pool_recycle=DB_POOL_RECYCLE,
                connect_args={
                    'ssl': 'require',
                    'sslmode': 'require',
                    'ssl_context': ssl_context,
                    'server_settings': {
                        'application_name': SERVICE_NAME,
                        'statement_timeout': '30000',
                        'idle_in_transaction_session_timeout': '60000'
                    }
                }
            )

            logger.info(
                f"Database engine initialized for {DATABRICKS_DATABASE_NAME} with background token refresh"
            )
        else:
            # MySQL configuration with async support
            url = URL.create(
                drivername="mysql+aiomysql",
                username=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASS", ""),
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "3306")),
                database=os.getenv("DB_NAME", "test"),
            )

            engine = create_async_engine(
                url,
                pool_pre_ping=True,
                echo=True,  # Enable SQL logging
                pool_size=DB_POOL_SIZE,
                max_overflow=DB_MAX_OVERFLOW,
                pool_timeout=DB_POOL_TIMEOUT,
                pool_recycle=DB_POOL_RECYCLE,
            )
            logger.info("Database engine initialized")

        # Create async session factory
        AsyncSessionLocal = sessionmaker(
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            bind=engine
        )

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise RuntimeError(f"Failed to initialize database: {e}") from e

async def start_token_refresh():
    global token_refresh_task
    if token_refresh_task is None or token_refresh_task.done():
        token_refresh_task = asyncio.create_task(refresh_token_background())
        logger.info("Background token refresh task started")

async def stop_token_refresh():
    global token_refresh_task
    if token_refresh_task and not token_refresh_task.done():
        token_refresh_task.cancel()
        try:
            await token_refresh_task
        except asyncio.CancelledError:
            pass
        logger.info("Background token refresh task stopped")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - async version"""
    if AsyncSessionLocal is None:
        raise RuntimeError("Engine not initialized; call init_engine() first")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def token_required_wrapper(
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    # Simplified token check for testing
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")

    logger.info(f"Initializing database engine for db_type: {os.environ.get('DB_TYPE', 'mysql')}")
    init_engine()
    logger.info("Database engine initialized")

    if os.environ.get("DB_TYPE", "mysql").lower() == "lakebase":
        logger.info("Starting Lakebase token refresh")
        await start_token_refresh()

    logger.info("Application startup complete")
    yield

    logger.info("Application shutdown initiated")
    if os.environ.get("DB_TYPE", "mysql").lower() == "lakebase":
        logger.info("Stopping Lakebase token refresh")
        await stop_token_refresh()

    logger.info("Application shutdown complete")