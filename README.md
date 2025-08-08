# Lakebase - Async Database Benchmarking & Connection Management

A comprehensive toolkit for benchmarking and managing async database connections with Databricks Lakebase, featuring secure credential management and high-performance connection pooling.

## 🚀 Features

- **Async Database Connections** - High-performance async connections with SQLAlchemy
- **Secure Credential Management** - Environment variables instead of plain JSON files
- **Connection Pooling** - Production-grade connection pooling with health monitoring
- **Benchmarking Tools** - Comprehensive performance testing with 100M+ row datasets
- **FastAPI Integration** - Ready-to-use FastAPI database modules
- **OAuth Token Management** - Automatic background token refresh for Lakebase

## 📁 Project Structure

```
lakebase/
├── README.md                           # This file
├── requirements.txt                    # Dependencies
├── .gitignore                         # Git ignore rules
├── .env                               # Secure credentials (gitignored)
├── .env.template                      # Template for credentials
├── lakebase_credentials.conf.example  # Legacy config example
├── lakebase_1m_benchmark.py          # Benchmark compatibility wrapper
├── async_database_wrapper.py          # Async database compatibility wrapper
│
├── src/                               # Main source code
│   ├── core/                          # Core functionality
│   │   ├── auth.py                    # Authentication management
│   │   ├── config.py                  # Configuration management
│   │   ├── pool.py                    # Connection pooling
│   │   ├── utils.py                   # Utility functions
│   │   └── secure_credentials.py      # Secure credential management
│   ├── monitoring/                    # Monitoring and health
│   │   ├── performance.py             # Performance monitoring
│   │   ├── health.py                  # Health monitoring
│   │   ├── error.py                   # Error handling
│   │   └── fastapi_monitoring.py      # FastAPI monitoring
│   └── database/                      # Database connections
│       └── async_database.py          # Async database module
│
├── scripts/                           # Executable scripts
│   ├── benchmark.py                   # Main benchmark script
│   ├── setup.py                       # Setup script
│   ├── config_helper.py               # Configuration helper
│   ├── update_token.py                # Token update script
│   └── setup_secure_env.py            # Secure environment setup
│
├── tests/                             # Test files
├── examples/                          # Example implementations
├── docs/                              # Documentation
├── config/                            # Configuration examples
└── data/                              # Data files
```

## 🔐 Secure Credential Management

This project uses **environment variables** instead of plain JSON files for secure credential management.

### Setup Secure Environment

1. **Create environment template:**
   ```bash
   python scripts/setup_secure_env.py template
   ```

2. **Configure your credentials:**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

3. **Validate configuration:**
   ```bash
   python scripts/setup_secure_env.py validate
   ```

### Required Environment Variables

```bash
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
LAKEFUSION_DATABRICKS_DAPI=dapi_your_personal_access_token_here
DATABRICKS_WORKSPACE_ID=your_workspace_id_here
DATABRICKS_USERNAME=your.email@company.com

# Lakebase Database Configuration
DATABRICKS_DATABASE_INSTANCE=your-benchmark-instance
DATABRICKS_DATABASE_HOST=instance-your-id.database.cloud.databricks.com
DATABRICKS_DATABASE_PORT=5432
DATABRICKS_DATABASE_NAME=databricks_postgres

# Connection Pool Configuration
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3000

# Service Configuration
SERVICE_NAME=LakeFusionDBService
DB_TYPE=lakebase
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Secure Credentials

```bash
python scripts/setup_secure_env.py template
cp .env.template .env
# Edit .env with your credentials
python scripts/setup_secure_env.py validate
```

### 3. Run Benchmark

```bash
python lakebase_1m_benchmark.py
```

### 4. Use in FastAPI

```python
from fastapi import FastAPI, Depends
from async_database_wrapper import get_db, lifespan

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root(db = Depends(get_db)):
    return {"message": "Hello World"}
```

## 📊 Benchmarking

The benchmark script tests Lakebase performance with:

- **100M+ row datasets** for realistic testing
- **Multi-threaded concurrent queries** (20-300 threads)
- **Connection pooling** with OAuth rate limiting mitigation
- **Comprehensive metrics** (throughput, latency, error rates)

### Benchmark Configuration

```python
# Default benchmark settings
thread_counts = [20, 40, 80, 100]  # Concurrent connections
test_duration = 30                  # Seconds per test
table_rows = 100000000             # 100M rows
batch_size = 10000                 # Batch size for operations
```

### Running Benchmarks

```bash
# Run full benchmark suite
python lakebase_1m_benchmark.py

# Run specific test
python tests/test_mysql_vs_lakebase.py

# Run comprehensive tests
python tests/comprehensive_test.py
```

## 🔧 Database Connection Features

### Async Database Module

- **Async SQLAlchemy** connections with `asyncpg`
- **Background token refresh** every 50 minutes
- **Connection pooling** with health monitoring
- **Error handling** and automatic recovery
- **FastAPI integration** with lifespan management

### Connection Pool Configuration

```python
pool_size = 20                    # Base pool size
max_overflow = 30                 # Maximum overflow connections
pool_timeout = 30                 # Pool checkout timeout
pool_recycle = 3000              # Pool recycle interval
```

## 🧪 Testing

### Run All Tests

```bash
python tests/comprehensive_test.py
```

### Test Categories

- ✅ **Dependencies** - All required packages
- ✅ **Configuration** - Secure credential validation
- ✅ **Benchmark** - Performance testing
- ✅ **Async Database** - Connection management
- ✅ **Async Functionality** - Async operations

## 📈 Performance Features

### Connection Pooling

- **Pre-warmed connections** for faster startup
- **Health monitoring** with automatic cleanup
- **OAuth rate limiting** mitigation
- **Background maintenance** tasks

### Monitoring

- **Performance metrics** collection
- **Health checks** for database connections
- **Error tracking** and categorization
- **Real-time monitoring** capabilities

## 🔒 Security

### Credential Management

- ✅ **Environment variables** instead of JSON files
- ✅ **No hardcoded secrets** in code
- ✅ **Secure token storage** and rotation
- ✅ **Non-sensitive logging** only

### Best Practices

- Never commit `.env` files to version control
- Use secure credential storage in production
- Rotate tokens regularly
- Monitor access logs

## 📋 Requirements

```
pydantic==2.11.5
pydantic-settings==2.9.1
python-dotenv==1.1.0
databricks-sdk==0.56.0
psycopg2-binary==2.9.9
fastapi==0.115.12
uvicorn==0.34.3
asyncpg==0.30.0
sqlalchemy==2.0.41
sqlmodel>=0.0.24
aiomysql==0.2.0
PyJWT==2.8.0
```

## 🎯 Usage Examples

### Basic Database Connection

```python
from async_database_wrapper import get_db, init_engine

# Initialize database
init_engine()

# Use in FastAPI
@app.get("/users")
async def get_users(db = Depends(get_db)):
    result = await db.execute("SELECT * FROM users LIMIT 10")
    return result.fetchall()
```

### Custom Benchmark

```python
from scripts.benchmark import Lakebase1MBenchmark

benchmark = Lakebase1MBenchmark()
benchmark.thread_counts = [10, 20, 50]  # Custom thread counts
benchmark.test_duration = 60            # 60 seconds per test
benchmark.run_full_benchmark()
```

### Secure Environment Setup

```python
from src.core.secure_credentials import setup_secure_environment, validate_secure_credentials

# Set up secure environment
setup_secure_environment()

# Validate credentials
if validate_secure_credentials():
    print("✅ Credentials are valid")
```

## 🚨 Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```bash
   python scripts/setup_secure_env.py validate
   ```

2. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Connection Issues**
   - Check your Databricks credentials
   - Verify network connectivity
   - Check token expiration

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python lakebase_1m_benchmark.py
```

## 📄 License

This project is for internal use at Databricks.

## 🤝 Contributing

1. Follow secure credential management practices
2. Add tests for new features
3. Update documentation for changes
4. Use async patterns for database operations

---

**Note**: This project uses secure credential management with environment variables. Never commit `.env` files or hardcoded secrets to version control.
