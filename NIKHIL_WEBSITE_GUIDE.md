# 🚀 Lakebase Benchmarking Website Guide for Nikhil

**A comprehensive guide to build a web interface for running Lakebase performance benchmarks**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Frontend Implementation](#frontend-implementation)
5. [Backend API Integration](#backend-api-integration)
6. [Real-time Monitoring](#real-time-monitoring)
7. [Database Integration](#database-integration)
8. [Deployment](#deployment)
9. [Security Considerations](#security-considerations)
10. [Examples](#examples)

---

## 🎯 Overview

This guide will help you build a **modern web application** that allows users to:

- ✅ **Configure and run benchmarks** through a web interface
- ✅ **Monitor real-time progress** with live updates
- ✅ **View historical results** and performance trends
- ✅ **Compare different configurations** side-by-side
- ✅ **Export reports** in various formats
- ✅ **Manage multiple benchmark runs** with user authentication

### 🎨 Recommended Tech Stack

**Frontend:**
- **React.js** or **Vue.js** for the UI
- **Tailwind CSS** for styling
- **Chart.js** or **D3.js** for visualizations
- **WebSocket** for real-time updates

**Backend:**
- **FastAPI** (already integrated with Lakebase)
- **PostgreSQL** for storing benchmark results
- **Redis** for caching and session management
- **Celery** for background task processing

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│◄──►│  FastAPI Backend │◄──►│  Lakebase DB    │
│                 │    │                  │    │                 │
│  - Benchmark UI │    │  - API Endpoints │    │  - Test Tables  │
│  - Real-time    │    │  - Auth Manager  │    │  - Results      │
│  - Charts       │    │  - Task Queue    │    │  - Metrics      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  WebSocket      │    │  Celery Workers  │    │  Benchmark      │
│  Real-time      │    │  Background      │    │  Scripts        │
│  Updates        │    │  Processing      │    │  Execution      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## ⚡ Quick Start

### 1. Project Structure

```
lakebase-website/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   └── requirements.txt
├── lakebase/               # Existing Lakebase codebase
└── docker-compose.yml      # Development setup
```

### 2. Backend Setup

```bash
# Create backend directory
mkdir -p backend/app
cd backend

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis celery

# Copy existing Lakebase code
cp -r ../lakebase/src ./app/lakebase
cp ../lakebase/requirements.txt .
```

### 3. Frontend Setup

```bash
# Create React app
npx create-react-app frontend
cd frontend

# Install dependencies
npm install axios chart.js react-chartjs-2 tailwindcss @headlessui/react
npm install socket.io-client react-router-dom
```

---

## 🎨 Frontend Implementation

### 1. Main Dashboard Component

```jsx
// frontend/src/components/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import BenchmarkForm from './BenchmarkForm';
import ResultsTable from './ResultsTable';
import RealTimeMetrics from './RealTimeMetrics';

const Dashboard = () => {
  const [benchmarks, setBenchmarks] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentBenchmark, setCurrentBenchmark] = useState(null);

  const startBenchmark = async (config) => {
    setIsRunning(true);
    try {
      const response = await fetch('/api/benchmarks/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await response.json();
      setCurrentBenchmark(data);
    } catch (error) {
      console.error('Failed to start benchmark:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            Lakebase Performance Benchmarking
          </h1>
          <p className="mt-2 text-gray-600">
            Configure and run performance tests on your Lakebase database
          </p>
        </div>

        {/* Benchmark Form */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <BenchmarkForm onStart={startBenchmark} disabled={isRunning} />
        </div>

        {/* Real-time Metrics */}
        {isRunning && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <RealTimeMetrics benchmarkId={currentBenchmark?.id} />
          </div>
        )}

        {/* Results Table */}
        <div className="bg-white shadow rounded-lg p-6">
          <ResultsTable benchmarks={benchmarks} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

### 2. Benchmark Configuration Form

```jsx
// frontend/src/components/BenchmarkForm.jsx
import React, { useState } from 'react';

const BenchmarkForm = ({ onStart, disabled }) => {
  const [config, setConfig] = useState({
    threadCounts: [20],
    tableRows: 1000000,
    testDuration: 60,
    batchSize: 10000
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onStart(config);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Benchmark Configuration
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Thread Counts */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Thread Counts
          </label>
          <input
            type="text"
            value={config.threadCounts.join(', ')}
            onChange={(e) => setConfig({
              ...config,
              threadCounts: e.target.value.split(',').map(x => parseInt(x.trim()))
            })}
            placeholder="20, 40, 80"
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Comma-separated list of thread counts to test
          </p>
        </div>

        {/* Table Rows */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Table Rows
          </label>
          <input
            type="number"
            value={config.tableRows}
            onChange={(e) => setConfig({
              ...config,
              tableRows: parseInt(e.target.value)
            })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Number of rows in test table (default: 1,000,000)
          </p>
        </div>

        {/* Test Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Test Duration (seconds)
          </label>
          <input
            type="number"
            value={config.testDuration}
            onChange={(e) => setConfig({
              ...config,
              testDuration: parseInt(e.target.value)
            })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Duration for each thread count test
          </p>
        </div>

        {/* Batch Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Batch Size
          </label>
          <input
            type="number"
            value={config.batchSize}
            onChange={(e) => setConfig({
              ...config,
              batchSize: parseInt(e.target.value)
            })}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Batch size for data insertion
          </p>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={disabled}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {disabled ? 'Running...' : 'Start Benchmark'}
        </button>
      </div>
    </form>
  );
};

export default BenchmarkForm;
```

### 3. Real-time Metrics Component

```jsx
// frontend/src/components/RealTimeMetrics.jsx
import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import io from 'socket.io-client';

const RealTimeMetrics = ({ benchmarkId }) => {
  const [metrics, setMetrics] = useState({
    throughput: [],
    latency: [],
    errors: []
  });
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    if (!benchmarkId) return;

    // Connect to WebSocket
    const newSocket = io('http://localhost:8000');
    setSocket(newSocket);

    // Listen for real-time updates
    newSocket.on('benchmark_update', (data) => {
      if (data.benchmark_id === benchmarkId) {
        setMetrics(prev => ({
          throughput: [...prev.throughput, { x: Date.now(), y: data.throughput }],
          latency: [...prev.latency, { x: Date.now(), y: data.avg_latency }],
          errors: [...prev.errors, { x: Date.now(), y: data.error_count }]
        }));
      }
    });

    return () => newSocket.close();
  }, [benchmarkId]);

  const chartData = {
    labels: metrics.throughput.map(m => new Date(m.x).toLocaleTimeString()),
    datasets: [
      {
        label: 'Throughput (ops/sec)',
        data: metrics.throughput.map(m => m.y),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1
      },
      {
        label: 'Avg Latency (ms)',
        data: metrics.latency.map(m => m.y),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.1
      }
    ]
  };

  return (
    <div>
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Real-time Performance Metrics
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {metrics.throughput.length > 0 
              ? Math.round(metrics.throughput[metrics.throughput.length - 1].y)
              : 0}
          </div>
          <div className="text-sm text-blue-600">Throughput (ops/sec)</div>
        </div>
        
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {metrics.latency.length > 0 
              ? Math.round(metrics.latency[metrics.latency.length - 1].y)
              : 0}
          </div>
          <div className="text-sm text-red-600">Avg Latency (ms)</div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">
            {metrics.errors.length > 0 
              ? metrics.errors[metrics.errors.length - 1].y
              : 0}
          </div>
          <div className="text-sm text-yellow-600">Errors</div>
        </div>
      </div>

      <div className="h-64">
        <Line 
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }}
        />
      </div>
    </div>
  );
};

export default RealTimeMetrics;
```

---

## 🔌 Backend API Integration

### 1. FastAPI Application Structure

```python
# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import List

from .api import benchmarks, auth, results
from .services.benchmark_service import BenchmarkService
from .models.database import init_db

app = FastAPI(title="Lakebase Benchmarking API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(benchmarks.router, prefix="/api/benchmarks", tags=["benchmarks"])
app.include_router(results.router, prefix="/api/results", tags=["results"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Benchmark API Endpoints

```python
# backend/app/api/benchmarks.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio

from ..models.database import get_db
from ..models.benchmark import Benchmark, BenchmarkCreate, BenchmarkResponse
from ..services.benchmark_service import BenchmarkService
from ..lakebase.scripts.benchmark import Lakebase1MBenchmark

router = APIRouter()

@router.post("/start", response_model=BenchmarkResponse)
async def start_benchmark(
    config: BenchmarkCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new benchmark run with website-provided configuration"""
    try:
        # Create benchmark record
        benchmark = Benchmark(
            thread_counts=config.thread_counts,
            table_rows=config.table_rows,
            test_duration=config.test_duration,
            batch_size=config.batch_size,
            status="running"
        )
        db.add(benchmark)
        db.commit()
        db.refresh(benchmark)

        # Start benchmark in background with website configuration
        background_tasks.add_task(
            run_benchmark_task,
            benchmark.id,
            config.dict()
        )

        return BenchmarkResponse(
            id=benchmark.id,
            status=benchmark.status,
            created_at=benchmark.created_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configure", response_model=dict)
async def configure_benchmark(config: BenchmarkCreate):
    """Validate and return benchmark configuration"""
    try:
        # Validate configuration
        if not config.thread_counts or len(config.thread_counts) == 0:
            raise HTTPException(status_code=400, detail="At least one thread count is required")
        
        if config.table_rows < 1000:
            raise HTTPException(status_code=400, detail="Minimum 1,000 rows required")
        
        if config.test_duration < 10:
            raise HTTPException(status_code=400, detail="Minimum 10 seconds test duration required")
        
        # Calculate estimated time
        total_threads = sum(config.thread_counts)
        estimated_time = len(config.thread_counts) * config.test_duration + 30  # 30s for setup
        
        return {
            "valid": True,
            "estimated_time_seconds": estimated_time,
            "total_threads": total_threads,
            "configuration": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{benchmark_id}", response_model=BenchmarkResponse)
async def get_benchmark(benchmark_id: int, db: Session = Depends(get_db)):
    """Get benchmark details"""
    benchmark = db.query(Benchmark).filter(Benchmark.id == benchmark_id).first()
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return benchmark

@router.get("/", response_model=List[BenchmarkResponse])
async def list_benchmarks(db: Session = Depends(get_db)):
    """List all benchmarks"""
    benchmarks = db.query(Benchmark).order_by(Benchmark.created_at.desc()).all()
    return benchmarks

async def run_benchmark_task(benchmark_id: int, config: dict):
    """Background task to run the benchmark with website configuration"""
    try:
        # Initialize benchmark service
        benchmark_service = BenchmarkService()
        
        # Create and configure benchmark with website parameters
        lakebase_benchmark = Lakebase1MBenchmark()
        
        # Override default configuration with website-provided values
        lakebase_benchmark.thread_counts = config["thread_counts"]  # From website
        lakebase_benchmark.table_rows = config["table_rows"]        # From website
        lakebase_benchmark.test_duration = config["test_duration"]  # From website
        lakebase_benchmark.batch_size = config["batch_size"]        # From website
        
        print(f"🎯 Starting benchmark with website configuration:")
        print(f"   Thread counts: {lakebase_benchmark.thread_counts}")
        print(f"   Table rows: {lakebase_benchmark.table_rows:,}")
        print(f"   Test duration: {lakebase_benchmark.test_duration}s")
        print(f"   Batch size: {lakebase_benchmark.batch_size}")

        # Run benchmark with progress updates
        results = await benchmark_service.run_with_progress(
            lakebase_benchmark,
            benchmark_id
        )

        # Save results
        await benchmark_service.save_results(benchmark_id, results)

    except Exception as e:
        # Update benchmark status to failed
        print(f"Benchmark {benchmark_id} failed: {e}")
```

### 3. Database Models

```python
# backend/app/models/benchmark.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

Base = declarative_base()

class Benchmark(Base):
    __tablename__ = "benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    thread_counts = Column(JSON)  # List of thread counts
    table_rows = Column(Integer)
    test_duration = Column(Integer)
    batch_size = Column(Integer)
    status = Column(String)  # running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    results = Column(JSON, nullable=True)  # Benchmark results

class BenchmarkCreate(BaseModel):
    thread_counts: List[int]
    table_rows: int
    test_duration: int
    batch_size: int

class BenchmarkResponse(BaseModel):
    id: int
    thread_counts: List[int]
    table_rows: int
    test_duration: int
    batch_size: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[dict] = None

    class Config:
        from_attributes = True
```

---

## 📊 Real-time Monitoring

### 1. WebSocket Integration

```python
# backend/app/services/benchmark_service.py
import asyncio
import json
from typing import Dict, Any
from ..models.database import get_db
from ..models.benchmark import Benchmark

class BenchmarkService:
    def __init__(self):
        self.active_benchmarks = {}

    async def run_with_progress(self, benchmark: Lakebase1MBenchmark, benchmark_id: int):
        """Run benchmark with real-time progress updates"""
        self.active_benchmarks[benchmark_id] = {
            "status": "running",
            "progress": 0,
            "current_thread": None,
            "results": []
        }

        try:
            # Override the benchmark's progress callback
            original_callback = benchmark.progress_callback
            benchmark.progress_callback = lambda data: self.update_progress(benchmark_id, data)

            # Run the benchmark
            results = benchmark.run_full_benchmark()
            
            # Update final status
            self.active_benchmarks[benchmark_id]["status"] = "completed"
            await self.broadcast_update(benchmark_id, {
                "status": "completed",
                "results": results
            })

            return results

        except Exception as e:
            self.active_benchmarks[benchmark_id]["status"] = "failed"
            await self.broadcast_update(benchmark_id, {
                "status": "failed",
                "error": str(e)
            })
            raise

    def update_progress(self, benchmark_id: int, data: Dict[str, Any]):
        """Update progress for a benchmark"""
        if benchmark_id in self.active_benchmarks:
            self.active_benchmarks[benchmark_id].update(data)
            asyncio.create_task(self.broadcast_update(benchmark_id, data))

    async def broadcast_update(self, benchmark_id: int, data: Dict[str, Any]):
        """Broadcast update to connected clients"""
        from ..main import manager
        
        message = {
            "type": "benchmark_update",
            "benchmark_id": benchmark_id,
            "data": data
        }
        
        await manager.broadcast(message)
```

### 2. Frontend WebSocket Integration

```jsx
// frontend/src/hooks/useWebSocket.js
import { useEffect, useRef } from 'react';
import io from 'socket.io-client';

export const useWebSocket = (url = 'http://localhost:8000') => {
  const socket = useRef(null);

  useEffect(() => {
    socket.current = io(url);

    socket.current.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    socket.current.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
    });

    return () => {
      if (socket.current) {
        socket.current.disconnect();
      }
    };
  }, [url]);

  const subscribeToBenchmark = (benchmarkId, callback) => {
    if (socket.current) {
      socket.current.on('benchmark_update', (data) => {
        if (data.benchmark_id === benchmarkId) {
          callback(data.data);
        }
      });
    }
  };

  return { socket: socket.current, subscribeToBenchmark };
};
```

---

## 🗄️ Database Integration

### 1. Database Schema

```sql
-- backend/app/models/schema.sql

-- Benchmarks table
CREATE TABLE benchmarks (
    id SERIAL PRIMARY KEY,
    thread_counts JSON NOT NULL,
    table_rows INTEGER NOT NULL,
    test_duration INTEGER NOT NULL,
    batch_size INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    results JSON NULL
);

-- Benchmark results table
CREATE TABLE benchmark_results (
    id SERIAL PRIMARY KEY,
    benchmark_id INTEGER REFERENCES benchmarks(id),
    thread_count INTEGER NOT NULL,
    duration_sec FLOAT NOT NULL,
    total_operations INTEGER NOT NULL,
    throughput_ops_sec FLOAT NOT NULL,
    avg_latency_ms FLOAT NOT NULL,
    p95_latency_ms FLOAT NOT NULL,
    p99_latency_ms FLOAT NOT NULL,
    error_count INTEGER NOT NULL,
    error_rate_pct FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table (for authentication)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User benchmarks (for user-specific benchmarks)
CREATE TABLE user_benchmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    benchmark_id INTEGER REFERENCES benchmarks(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Database Connection

```python
# backend/app/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/lakebase_benchmarks")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    Base.metadata.create_all(bind=engine)
```

---

## 🚀 Deployment

### 1. Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Build application
RUN npm run build

# Install serve
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Serve application
CMD ["serve", "-s", "build", "-l", "3000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@postgres/lakebase_benchmarks
      - REDIS_URL=redis://redis:6379
      - DATABRICKS_HOST=${DATABRICKS_HOST}
      - LAKEFUSION_DATABRICKS_DAPI=${LAKEFUSION_DATABRICKS_DAPI}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=lakebase_benchmarks
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:password@postgres/lakebase_benchmarks
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

### 3. Environment Variables

```bash
# .env
# Database
DATABASE_URL=postgresql://user:password@localhost/lakebase_benchmarks
REDIS_URL=redis://localhost:6379

# Lakebase Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
LAKEFUSION_DATABRICKS_DAPI=dapi_your_token_here
DATABRICKS_DATABASE_INSTANCE=your-database-instance
DATABRICKS_DATABASE_HOST=your-instance.database.cloud.databricks.com

# Application
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🔒 Security Considerations

### 1. Authentication

```python
# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from ..models.database import get_db
from ..models.user import User, UserCreate

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### 2. Rate Limiting

```python
# backend/app/middleware/rate_limit.py
from fastapi import HTTPException, Request
import time
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)

    async def check_rate_limit(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < 60
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )
        
        # Add current request
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response
```

---

## 📝 Examples

### 1. Complete React App Structure

```jsx
// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import BenchmarkDetail from './pages/BenchmarkDetail';
import Navbar from './components/Navbar';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/benchmark/:id" element={<BenchmarkDetail />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

### 2. API Service Layer

```javascript
// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const benchmarkAPI = {
  start: (config) => api.post('/api/benchmarks/start', config),
  get: (id) => api.get(`/api/benchmarks/${id}`),
  list: () => api.get('/api/benchmarks/'),
  getResults: (id) => api.get(`/api/benchmarks/${id}/results`),
};

export const authAPI = {
  login: (credentials) => api.post('/api/auth/token', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  me: () => api.get('/api/auth/me'),
};

export default api;
```

### 3. Tailwind CSS Configuration

```javascript
// frontend/tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        }
      }
    },
  },
  plugins: [],
}
```

---

## 🎯 Next Steps for Nikhil

1. **Set up the development environment** with the provided Docker configuration
2. **Implement the frontend components** using React and Tailwind CSS
3. **Create the backend API** with FastAPI and integrate with the existing Lakebase code
4. **Add real-time monitoring** with WebSocket connections
5. **Implement user authentication** and rate limiting
6. **Deploy the application** using Docker Compose
7. **Add comprehensive testing** for all components
8. **Implement error handling** and logging
9. **Add performance monitoring** and analytics
10. **Create user documentation** and help guides

The existing Lakebase codebase is already well-structured and ready for integration. The FastAPI integration guide I created earlier provides all the necessary components for building a production-ready web application.

**Good luck with the project, Nikhil! 🚀**

---

*This guide provides a complete foundation for building a Lakebase benchmarking website. The existing codebase is production-ready and includes all necessary components for high-performance database testing.*
