# 🚀 Lakebase FastAPI Integration Guide

**A comprehensive guide for building FastAPI applications with Lakebase database integration**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Database Integration](#database-integration)
5. [API Endpoints](#api-endpoints)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Error Handling](#error-handling)
8. [Configuration](#configuration)
9. [Production Deployment](#production-deployment)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This codebase provides a **production-ready FastAPI integration** for Lakebase (Databricks SQL) with:

- ✅ **Async Database Operations** - Full async/await support
- ✅ **Connection Pooling** - Production-grade connection management
- ✅ **OAuth Token Management** - Automatic token refresh
- ✅ **Health Monitoring** - Real-time system health checks
- ✅ **Performance Metrics** - Comprehensive monitoring
- ✅ **Error Handling** - Structured error management
- ✅ **Security** - Environment-based credential management

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Lakebase SDK    │───▶│  Databricks DB  │
│                 │    │  Authentication  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Connection     │    │  Token Refresh   │    │  Health Monitor │
│  Pool Manager   │    │  Background Task │    │  & Metrics      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

1. **`src/database/async_database.py`** - Core database integration
2. **`src/core/auth.py`** - Authentication and token management
3. **`src/core/pool.py`** - Connection pooling
4. **`src/monitoring/`** - Health checks and performance monitoring
5. **`src/core/config.py`** - Configuration management

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Required Databricks credentials
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export LAKEFUSION_DATABRICKS_DAPI="dapi_your_token_here"
export DATABRICKS_DATABASE_INSTANCE="your-database-instance"
export DATABRICKS_DATABASE_HOST="your-instance.database.cloud.databricks.com"

# Optional configuration
export DB_POOL_SIZE="20"
export DB_MAX_OVERFLOW="30"
export DB_TYPE="lakebase"
```

### 3. Basic FastAPI App

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.async_database import get_db, init_engine, lifespan

app = FastAPI(title="Lakebase API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Lakebase FastAPI Integration"}

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    result = await db.execute(text("SELECT * FROM users LIMIT 10"))
    users = result.fetchall()
    return {"users": [dict(user) for user in users]}
```

### 4. Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🗄️ Database Integration

### Async Database Session

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.async_database import get_db

@app.get("/data")
async def get_data(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    # Execute async query
    result = await db.execute(text("SELECT * FROM my_table WHERE id = :id"), {"id": 1})
    row = result.fetchone()
    
    return {"data": dict(row) if row else None}
```

### Transaction Management

```python
@app.post("/create_user")
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    try:
        # Start transaction
        await db.begin()
        
        # Insert user
        result = await db.execute(
            text("INSERT INTO users (name, email) VALUES (:name, :email) RETURNING id"),
            user_data
        )
        user_id = result.scalar()
        
        # Commit transaction
        await db.commit()
        
        return {"user_id": user_id, "status": "created"}
        
    except Exception as e:
        # Rollback on error
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### Connection Pool Management

```python
from src.core.pool import create_enhanced_pool

# Create connection pool
pool = create_enhanced_pool()

# Use in FastAPI dependency
async def get_db_pool():
    return pool

@app.get("/pool-status")
async def get_pool_status(pool = Depends(get_db_pool)):
    return pool.get_pool_status()
```

---

## 🔌 API Endpoints

### Built-in Monitoring Endpoints

The codebase includes a complete monitoring API:

```python
# Health checks
GET /health                    # Basic health status
GET /health/detailed          # Detailed health information

# Performance metrics
GET /metrics/performance      # Performance statistics
GET /metrics/pool            # Connection pool status
GET /metrics/errors          # Error summary

# Testing endpoints
POST /test/connection        # Test database connection
POST /test/query            # Test query performance

# Configuration
GET /config                 # Current configuration

# WebSocket for live updates
WS /ws/live-updates         # Real-time monitoring data
```

### Custom API Endpoints

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.async_database import get_db
from src.core.auth import LakebaseSDKAuthManager

app = FastAPI()

# User management endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    result = await db.execute(
        text("SELECT * FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": dict(user)}

@app.post("/users")
async def create_user(user_data: dict, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    result = await db.execute(
        text("INSERT INTO users (name, email) VALUES (:name, :email) RETURNING id"),
        user_data
    )
    user_id = result.scalar()
    await db.commit()
    
    return {"user_id": user_id, "status": "created"}

# Analytics endpoints
@app.get("/analytics/summary")
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    result = await db.execute(text("""
        SELECT 
            COUNT(*) as total_users,
            AVG(age) as avg_age,
            MAX(created_at) as latest_user
        FROM users
    """))
    
    summary = result.fetchone()
    return {"summary": dict(summary)}
```

---

## 📊 Monitoring & Health Checks

### Health Check Integration

```python
from src.monitoring.health import HealthMonitor, HealthStatus

# Create health monitor
health_monitor = HealthMonitor()

@app.get("/health")
async def health_check():
    health_status = await health_monitor.run_health_checks()
    return {
        "status": health_status.overall_status.value,
        "checks": [check.to_dict() for check in health_status.checks],
        "timestamp": health_status.timestamp.isoformat()
    }
```

### Performance Monitoring

```python
from src.monitoring.performance import PerformanceMonitor, timed_operation

# Create performance monitor
perf_monitor = PerformanceMonitor()

@app.get("/metrics")
async def get_metrics():
    return perf_monitor.get_performance_summary()

# Monitor specific operations
@app.get("/slow-query")
@timed_operation("slow_query")
async def slow_query(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    # This operation will be automatically timed
    result = await db.execute(text("SELECT pg_sleep(1)"))
    return {"status": "completed"}
```

### Real-time Monitoring Dashboard

```python
from fastapi.responses import HTMLResponse

@app.get("/dashboard", response_class=HTMLResponse)
async def monitoring_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lakebase Monitoring Dashboard</title>
    </head>
    <body>
        <h1>Lakebase FastAPI Monitoring</h1>
        <div id="metrics"></div>
        <script>
            // WebSocket connection for live updates
            const ws = new WebSocket('ws://localhost:8000/ws/live-updates');
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                document.getElementById('metrics').innerHTML = 
                    JSON.stringify(data, null, 2);
            };
        </script>
    </body>
    </html>
    """
```

---

## ⚠️ Error Handling

### Structured Error Handling

```python
from src.monitoring.error import (
    ErrorHandler, 
    LakebaseException, 
    DatabaseConnectionError,
    with_error_handling
)

# Global error handler
error_handler = ErrorHandler()

@app.exception_handler(LakebaseException)
async def lakebase_exception_handler(request, exc: LakebaseException):
    return JSONResponse(
        status_code=500,
        content={
            "error": exc.context.message,
            "category": exc.context.category.value,
            "timestamp": exc.context.timestamp.isoformat()
        }
    )

# Error handling decorator
@app.get("/protected-endpoint")
@with_error_handling("user_data_retrieval")
async def get_user_data(user_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import text
    
    result = await db.execute(
        text("SELECT * FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        raise DatabaseConnectionError("User not found")
    
    return {"user": dict(user)}
```

### Custom Error Responses

```python
from fastapi import HTTPException
from src.monitoring.error import handle_error

@app.get("/data/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        
        result = await db.execute(
            text("SELECT * FROM items WHERE id = :item_id"),
            {"item_id": item_id}
        )
        item = result.fetchone()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {"item": dict(item)}
        
    except Exception as e:
        # Handle and log error
        error_context = handle_error(e, "item_retrieval")
        
        if error_context.category.value == "database_connection":
            raise HTTPException(status_code=503, detail="Database unavailable")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
```

---

## ⚙️ Configuration

### Environment-Based Configuration

```python
from src.core.config import load_settings, LakebaseSettings

# Load settings
settings: LakebaseSettings = load_settings()

# Use in FastAPI app
app = FastAPI(
    title=settings.security.application_name,
    description="Lakebase FastAPI Integration"
)

# Access configuration
@app.get("/config")
async def get_config():
    return {
        "database": {
            "host": settings.lakebase.host,
            "port": settings.lakebase.port,
            "database": settings.lakebase.database
        },
        "pool": {
            "size": settings.production_pool.pool_size,
            "max_overflow": settings.production_pool.max_overflow
        },
        "monitoring": {
            "log_level": settings.monitoring.log_level,
            "health_checks": settings.monitoring.enable_health_checks
        }
    }
```

### Configuration Validation

```python
from src.core.config import LakebaseSettings

def validate_config():
    try:
        settings = LakebaseSettings()
        validation = settings.validate_configuration()
        
        if not validation["valid"]:
            print("❌ Configuration validation failed:")
            for error in validation["errors"]:
                print(f"   - {error}")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

# Use in startup
@app.on_event("startup")
async def startup_event():
    if not validate_config():
        raise RuntimeError("Invalid configuration")
```

---

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DB_TYPE=lakebase

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  lakebase-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABRICKS_HOST=${DATABRICKS_HOST}
      - LAKEFUSION_DATABRICKS_DAPI=${LAKEFUSION_DATABRICKS_DAPI}
      - DATABRICKS_DATABASE_INSTANCE=${DATABRICKS_DATABASE_INSTANCE}
      - DATABRICKS_DATABASE_HOST=${DATABRICKS_DATABASE_HOST}
      - DB_POOL_SIZE=20
      - DB_MAX_OVERFLOW=30
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lakebase-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lakebase-api
  template:
    metadata:
      labels:
        app: lakebase-api
    spec:
      containers:
      - name: lakebase-api
        image: lakebase-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABRICKS_HOST
          valueFrom:
            secretKeyRef:
              name: lakebase-secrets
              key: databricks-host
        - name: LAKEFUSION_DATABRICKS_DAPI
          valueFrom:
            secretKeyRef:
              name: lakebase-secrets
              key: databricks-token
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 📝 Examples

### Complete FastAPI Application

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel

from src.database.async_database import get_db, init_engine, lifespan
from src.core.config import load_settings
from src.monitoring.health import HealthMonitor
from src.monitoring.performance import PerformanceMonitor

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int]
    created_at: str

# Initialize FastAPI app
app = FastAPI(
    title="Lakebase User Management API",
    description="FastAPI application with Lakebase database integration",
    version="1.0.0",
    lifespan=lifespan
)

# Load settings
settings = load_settings()

# Initialize monitors
health_monitor = HealthMonitor()
perf_monitor = PerformanceMonitor()

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Lakebase FastAPI Integration",
        "version": "1.0.0",
        "database": "Lakebase (Databricks SQL)"
    }

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset}
    )
    users = result.fetchall()
    return [UserResponse(**dict(user)) for user in users]

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**dict(user))

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            INSERT INTO users (name, email, age, created_at) 
            VALUES (:name, :email, :age, NOW()) 
            RETURNING id, name, email, age, created_at
        """),
        user.dict()
    )
    new_user = result.fetchone()
    await db.commit()
    
    return UserResponse(**dict(new_user))

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("DELETE FROM users WHERE id = :user_id RETURNING id"),
        {"user_id": user_id}
    )
    deleted_user = result.fetchone()
    
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.commit()
    return {"message": "User deleted successfully"}

# Health and monitoring endpoints
@app.get("/health")
async def health_check():
    health_status = await health_monitor.run_health_checks()
    return {
        "status": health_status.overall_status.value,
        "checks": [check.to_dict() for check in health_status.checks],
        "timestamp": health_status.timestamp.isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    return perf_monitor.get_performance_summary()

@app.get("/config")
async def get_config():
    return {
        "database": {
            "host": settings.lakebase.host,
            "port": settings.lakebase.port,
            "database": settings.lakebase.database
        },
        "pool": {
            "size": settings.production_pool.pool_size,
            "max_overflow": settings.production_pool.max_overflow
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Database Schema Setup

```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create audit log table
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    record_id INTEGER,
    changes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors

```bash
# Check environment variables
echo $DATABRICKS_HOST
echo $LAKEFUSION_DATABRICKS_DAPI
echo $DATABRICKS_DATABASE_INSTANCE

# Test connection
curl -X POST http://localhost:8000/test/connection
```

#### 2. Connection Pool Issues

```python
# Check pool status
@app.get("/debug/pool")
async def debug_pool():
    pool = create_enhanced_pool()
    return pool.get_pool_status()
```

#### 3. Performance Issues

```python
# Monitor slow queries
@app.get("/debug/slow-queries")
async def debug_slow_queries():
    from src.monitoring.performance import PerformanceMonitor
    monitor = PerformanceMonitor()
    return monitor.get_operation_stats("slow_query")
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug endpoints
@app.get("/debug/config")
async def debug_config():
    return {
        "environment": dict(os.environ),
        "settings": settings.dict() if settings else None
    }

@app.get("/debug/health")
async def debug_health():
    return await health_monitor.run_health_checks()
```

### Logging Configuration

```python
# Configure structured logging
import logging
from src.core.config import load_settings

settings = load_settings()

logging.basicConfig(
    level=getattr(logging, settings.monitoring.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
```

---

## 📚 Additional Resources

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Monitoring Dashboard

- **Dashboard**: `http://localhost:8000/dashboard`
- **Health Check**: `http://localhost:8000/health`
- **Metrics**: `http://localhost:8000/metrics/performance`

### Development Tools

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with specific log level
uvicorn main:app --log-level debug

# Run with multiple workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## 🎯 Conclusion

This Lakebase FastAPI integration provides:

- ✅ **Production-ready** database integration
- ✅ **Async/await** support throughout
- ✅ **Comprehensive monitoring** and health checks
- ✅ **Structured error handling**
- ✅ **Security best practices**
- ✅ **Easy deployment** with Docker/Kubernetes

The codebase is designed to be **LLM-friendly** with clear patterns, comprehensive documentation, and consistent naming conventions. Developers and AI assistants can easily understand and extend the functionality.

---

*For more information, see the main README.md and individual module documentation.*
