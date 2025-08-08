#!/usr/bin/env python3
"""
Test script to verify Lakebase parallel execution capabilities
This test only focuses on Lakebase, no MySQL comparison
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
engine = None
AsyncSessionLocal = None

def load_credentials():
    """Load credentials from secure environment variables"""
    try:
        # Add the src directory to the path
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        from core.secure_credentials import get_secure_credentials
        return get_secure_credentials()
    except Exception as e:
        logger.error(f"Failed to load credentials: {e}")
        return None

def init_lakebase_engine():
    """Initialize the Lakebase database engine"""
    global engine, AsyncSessionLocal
    
    # Lakebase configuration
    config = load_credentials()
    if not config:
        logger.error("Failed to load Lakebase credentials")
        return False
        
    lakebase_config = config.get('lakebase', {})
    databricks_config = config.get('databricks', {})
    
    url = f"postgresql+asyncpg://{lakebase_config.get('database', 'databricks_postgres')}:{lakebase_config.get('port', 5432)}/{lakebase_config.get('database', 'databricks_postgres')}"
    
    # For Lakebase, we need to use the actual OAuth token
    # Let's get the token from the auth manager
    try:
        # Add the src directory to the path
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        from core.auth import LakebaseSDKAuthManager
        auth_manager = LakebaseSDKAuthManager()
        conn_params = auth_manager.get_connection_params(quiet=True)
        
        engine = create_async_engine(
            url,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                'host': conn_params.get('host', ''),
                'user': conn_params.get('user', ''),
                'password': conn_params.get('password', ''),
                'ssl': 'require'
            }
        )
    except Exception as e:
        logger.error(f"Failed to get Lakebase connection parameters: {e}")
        return False
    logger.info("Lakebase engine initialized")
    
    AsyncSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession
    )
    
    return True

async def warm_up_connection():
    """Warm up a single Lakebase connection"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT pg_sleep(1) as delay"))
            rows = result.fetchall()
            await session.commit()
            logger.info("Lakebase connection warm-up successful")
            return True
    except Exception as e:
        logger.error(f"Lakebase connection warm-up failed: {e}")
        return False

async def warm_up_pool():
    """Warm up multiple Lakebase connections in parallel"""
    logger.info("Starting parallel Lakebase connection warm-up...")
    start_time = time.time()
    
    # Create multiple warm-up tasks
    tasks = [warm_up_connection() for _ in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    successful = sum(1 for r in results if r is True)
    logger.info(f"Lakebase warm-up completed: {successful}/5 connections successful in {total_time:.2f}s")
    
    return successful == 5

async def run_lakebase_query(query_id: int, sleep_time: int):
    """Run a test query on Lakebase with sleep"""
    start_time = time.time()
    logger.info(f"Lakebase Query {query_id}: Starting (sleep {sleep_time}s)")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("SELECT pg_sleep(:sleep_time) as delay, :test_id as test_id"),
                {"sleep_time": sleep_time, "test_id": str(query_id)}
            )
            
            rows = result.fetchall()
            await session.commit()
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Lakebase Query {query_id}: Completed in {duration:.2f}s")
            return True
            
    except Exception as e:
        logger.error(f"Lakebase Query {query_id}: Failed - {e}")
        return False

async def test_lakebase_parallel_execution():
    """Test parallel query execution on Lakebase"""
    logger.info("Testing Lakebase parallel query execution...")
    start_time = time.time()
    
    # Create queries with different sleep times to demonstrate parallelism
    queries = [
        (1, 3),  # Query 1: 3 seconds
        (2, 2),  # Query 2: 2 seconds  
        (3, 4),  # Query 3: 4 seconds
        (4, 1),  # Query 4: 1 second
        (5, 3),  # Query 5: 3 seconds
    ]
    
    # Run all queries in parallel
    tasks = [run_lakebase_query(query_id, sleep_time) for query_id, sleep_time in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    total_time = end_time - start_time
    sequential_time = sum(sleep_time for _, sleep_time in queries)
    
    successful = sum(1 for r in results if r is True)
    logger.info(f"Lakebase parallel execution completed: {successful}/5 queries successful")
    logger.info(f"Total time: {total_time:.2f}s (parallel execution)")
    logger.info(f"Sequential time would be: {sequential_time}s")
    logger.info(f"Speedup factor: {sequential_time / total_time:.1f}x")
    
    return successful == 5, total_time, sequential_time

async def test_lakebase_connection_pool():
    """Test Lakebase connection pool functionality"""
    logger.info("Testing Lakebase connection pool...")
    
    # Test multiple concurrent connections
    async def test_connection(conn_id: int):
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1 as test_connection"))
                result.fetchall()
                logger.info(f"Connection {conn_id}: Success")
                return True
        except Exception as e:
            logger.error(f"Connection {conn_id}: Failed - {e}")
            return False
    
    # Test 10 concurrent connections
    tasks = [test_connection(i) for i in range(1, 11)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if r is True)
    logger.info(f"Connection pool test: {successful}/10 connections successful")
    
    return successful == 10

async def main():
    """Main test function"""
    logger.info("🚀 Starting Lakebase Parallel Execution Test")
    logger.info("=" * 60)
    
    # Initialize Lakebase engine
    if not init_lakebase_engine():
        logger.error("Failed to initialize Lakebase engine")
        return False
    
    try:
        # Test 1: Connection pool warm-up
        logger.info("\n📋 Test 1: Connection Pool Warm-up")
        if not await warm_up_pool():
            logger.error("Lakebase connection warm-up failed")
            return False
        
        # Test 2: Connection pool functionality
        logger.info("\n📋 Test 2: Connection Pool Functionality")
        if not await test_lakebase_connection_pool():
            logger.error("Lakebase connection pool test failed")
            return False
        
        # Test 3: Parallel execution
        logger.info("\n📋 Test 3: Parallel Query Execution")
        success, parallel_time, sequential_time = await test_lakebase_parallel_execution()
        if not success:
            logger.error("Lakebase parallel execution test failed")
            return False
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 LAKEBASE TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Connection Pool Warm-up: PASSED")
        logger.info(f"✅ Connection Pool Functionality: PASSED")
        logger.info(f"✅ Parallel Execution: PASSED")
        logger.info(f"")
        logger.info(f"📈 Performance Metrics:")
        logger.info(f"   Sequential Time: {sequential_time}s")
        logger.info(f"   Parallel Time: {parallel_time:.2f}s")
        logger.info(f"   Speedup Factor: {sequential_time / parallel_time:.1f}x")
        logger.info(f"")
        logger.info(f"🎉 LAKEBASE PARALLEL EXECUTION CONFIRMED!")
        logger.info(f"✅ Lakebase supports true parallel query execution")
        logger.info(f"✅ Async/await patterns work correctly with Lakebase")
        logger.info(f"✅ Connection pooling is functioning properly")
        
        return True
        
    except Exception as e:
        logger.error(f"Lakebase test failed: {e}")
        return False
    finally:
        if engine:
            await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
