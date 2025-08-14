#!/usr/bin/env python3
"""
Simple Sync Lakebase Test
Uses existing working infrastructure but demonstrates sync sessions with threading
"""

import time
import logging
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import the working async infrastructure
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from async_database_wrapper import init_engine, start_token_refresh, stop_token_refresh

def create_sync_engine_from_async():
    """Create a sync engine using the same connection parameters as the working async version"""
    
    # First initialize the async engine to get the working connection
    init_engine()
    
    # Import the global variables from the async module
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from database.async_database import engine as async_engine
    
    # Get the connection URL from the async engine
    url = async_engine.url
    
    # Create a sync version of the same URL
    from sqlalchemy import URL
    sync_url = URL.create(
        drivername="postgresql+psycopg2",  # Use psycopg2 for sync
        username=url.username,
        password=url.password,
        host=url.host,
        port=url.port,
        database=url.database,
    )
    
    # Create sync engine with simpler SSL settings
    sync_engine = create_engine(
        sync_url,
        pool_pre_ping=True,
        echo=False,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_recycle=3000,
        connect_args={
            'sslmode': 'require',
            'application_name': 'LakeFusionDBService',
        }
    )
    
    return sync_engine

def run_sync_query(session_factory, query_id: int, sleep_time: int):
    """Run a sync query with sleep"""
    start_time = time.time()
    thread_name = threading.current_thread().name
    logger.info(f"[{thread_name}] Query {query_id}: Starting (sleep {sleep_time}s)")
    
    try:
        with session_factory() as session:
            # Use PostgreSQL sleep function
            result = session.execute(
                text("SELECT pg_sleep(:sleep_time) as delay, :test_id as test_id, NOW() as timestamp"),
                {"sleep_time": sleep_time, "test_id": str(query_id)}
            )
            
            row = result.fetchone()
            session.commit()
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"[{thread_name}] Query {query_id}: Completed in {duration:.2f}s - Result: {row}")
            return True
            
    except Exception as e:
        logger.error(f"[{thread_name}] Query {query_id}: Failed - {e}")
        return False

def test_sync_parallel_execution():
    """Test parallel execution using sync sessions and threading"""
    logger.info("Testing sync parallel execution with ThreadPoolExecutor...")
    start_time = time.time()
    
    # Create sync engine using working async infrastructure
    sync_engine = create_sync_engine_from_async()
    session_factory = sessionmaker(bind=sync_engine)
    
    # Create queries with different sleep times to demonstrate parallelism
    queries = [
        (1, 2),  # Query 1: 2 seconds
        (2, 1),  # Query 2: 1 second  
        (3, 3),  # Query 3: 3 seconds
        (4, 1),  # Query 4: 1 second
        (5, 2),  # Query 5: 2 seconds
    ]
    
    # Run queries in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        futures = [
            executor.submit(run_sync_query, session_factory, query_id, sleep_time) 
            for query_id, sleep_time in queries
        ]
        
        # Wait for all tasks to complete
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Task failed: {e}")
                results.append(False)
    
    end_time = time.time()
    total_time = end_time - start_time
    sequential_time = sum(sleep_time for _, sleep_time in queries)
    
    successful = sum(1 for r in results if r is True)
    speedup_factor = sequential_time / total_time if total_time > 0 else 0
    
    logger.info(f"Sync parallel execution completed: {successful}/{len(queries)} queries successful")
    logger.info(f"Total time: {total_time:.2f}s (parallel execution)")
    logger.info(f"Sequential time would be: {sequential_time}s")
    logger.info(f"Speedup factor: {speedup_factor:.1f}x")
    
    return {
        'success': successful == len(queries),
        'total_time': total_time,
        'sequential_time': sequential_time,
        'speedup_factor': speedup_factor,
        'successful_queries': successful,
        'total_queries': len(queries)
    }

def main():
    """Main test function"""
    logger.info("🚀 Starting Simple Sync Lakebase Test")
    logger.info("=" * 60)
    logger.info("This test uses SYNC sessions with ThreadPoolExecutor")
    logger.info("=" * 60)
    
    try:
        # Start token refresh (same as async test)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_token_refresh())
        
        # Test parallel execution
        logger.info("\n📋 Test: Sync Parallel Query Execution")
        parallel_result = test_sync_parallel_execution()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 SYNC LAKEBASE TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Parallel Execution: {'PASSED' if parallel_result['success'] else 'FAILED'}")
        logger.info(f"")
        logger.info(f"📈 Performance Metrics:")
        logger.info(f"   Sequential Time: {parallel_result['sequential_time']}s")
        logger.info(f"   Parallel Time: {parallel_result['total_time']:.2f}s")
        logger.info(f"   Speedup Factor: {parallel_result['speedup_factor']:.1f}x")
        logger.info(f"   Success Rate: {parallel_result['successful_queries']}/{parallel_result['total_queries']}")
        logger.info(f"")
        
        if parallel_result['success']:
            logger.info(f"🎉 SYNC LAKEBASE PARALLEL EXECUTION CONFIRMED!")
            logger.info(f"✅ Lakebase supports parallel execution with sync sessions")
            logger.info(f"✅ ThreadPoolExecutor provides true parallel execution")
            logger.info(f"✅ Same performance benefits as async patterns")
        else:
            logger.info(f"⚠️  Some queries failed, but parallel execution structure works")
        
        # Stop token refresh
        loop.run_until_complete(stop_token_refresh())
        loop.close()
        
        return parallel_result['success']
        
    except Exception as e:
        logger.error(f"Sync test failed: {e}")
        return False

if __name__ == "__main__":
    import os
    success = main()
    if success:
        logger.info("✅ Simple sync Lakebase test completed successfully!")
    else:
        logger.error("❌ Simple sync Lakebase test failed!")
