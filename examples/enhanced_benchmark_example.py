#!/usr/bin/env python3
"""
Enhanced Lakebase Benchmark Example
Demonstrates all the FastAPI best practices integrated together.

This example shows how to:
- Use environment-based configuration
- Leverage enhanced error handling
- Monitor performance in real-time
- Check system health
- Use the enhanced production connection pool

Run this script to see all the enhanced features in action!
"""

import asyncio
import logging
import time
from typing import List, Dict, Any

# Import our enhanced modules
from config import load_settings
from enhanced_production_pool import create_enhanced_pool
from error_handling import handle_error, LakebaseException
from performance_monitoring import PerformanceTimer, timed_operation
from health_monitoring import HealthStatus

logger = logging.getLogger(__name__)


@timed_operation("benchmark_operation")
def run_benchmark_query(pool, query: str, iterations: int = 100) -> Dict[str, Any]:
    """Run a benchmark query with performance monitoring"""
    results = []
    errors = 0
    
    for i in range(iterations):
        try:
            with PerformanceTimer(f"query_iteration_{i}", pool.performance_monitor):
                conn = pool.get_connection()
                
                with conn.cursor() as cursor:
                    start_time = time.time()
                    cursor.execute(query)
                    result = cursor.fetchone()
                    duration_ms = (time.time() - start_time) * 1000
                    
                    results.append({
                        "iteration": i,
                        "duration_ms": duration_ms,
                        "result": result[0] if result else None
                    })
                
                pool.return_connection(conn)
                
        except Exception as e:
            error_context = handle_error(e, f"benchmark_query_iteration_{i}")
            logger.error(f"Query iteration {i} failed: {error_context.message}")
            errors += 1
    
    # Calculate statistics
    durations = [r["duration_ms"] for r in results]
    if durations:
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        success_rate = ((iterations - errors) / iterations) * 100
    else:
        avg_duration = min_duration = max_duration = 0
        success_rate = 0
    
    return {
        "query": query,
        "iterations": iterations,
        "successful": len(results),
        "errors": errors,
        "success_rate": success_rate,
        "avg_duration_ms": avg_duration,
        "min_duration_ms": min_duration,
        "max_duration_ms": max_duration,
        "results": results[:5]  # First 5 results for inspection
    }


def demonstrate_configuration():
    """Demonstrate the enhanced configuration system"""
    print("\n🔧 CONFIGURATION DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Load configuration with validation
        settings = load_settings()
        
        print("✅ Configuration loaded successfully!")
        print(f"   Database: {settings.lakebase.host}:{settings.lakebase.port}")
        print(f"   Pool Size: {settings.production_pool.pool_size}")
        print(f"   Max Overflow: {settings.production_pool.max_overflow}")
        print(f"   Performance Monitoring: {settings.monitoring.enable_performance_monitoring}")
        print(f"   Health Checks: {settings.monitoring.enable_health_checks}")
        
        # Validate configuration
        validation = settings.validate_configuration()
        print(f"   Configuration Valid: {validation['valid']}")
        
        if validation['warnings']:
            print("   ⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"      - {warning}")
        
        if validation['recommendations']:
            print("   💡 Recommendations:")
            for rec in validation['recommendations']:
                print(f"      - {rec}")
        
        return settings
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return None


def demonstrate_connection_pool(settings):
    """Demonstrate the enhanced connection pool"""
    print("\n🏊 CONNECTION POOL DEMONSTRATION")
    print("=" * 50)
    
    try:
        with create_enhanced_pool() as pool:
            print("✅ Enhanced connection pool created!")
            
            # Show initial pool status
            status = pool.get_pool_status()
            print(f"   Pool Size: {status['pool_size']}")
            print(f"   Available Connections: {status['available_connections']}")
            print(f"   Utilization: {status['utilization_rate']}%")
            
            # Test connection checkout/checkin
            print("\n   Testing connection checkout/checkin...")
            connections = []
            
            # Check out multiple connections
            for i in range(3):
                conn = pool.get_connection()
                connections.append(conn)
                print(f"   ✅ Connection {i+1} checked out")
            
            # Return connections
            for i, conn in enumerate(connections):
                pool.return_connection(conn)
                print(f"   ✅ Connection {i+1} returned")
            
            # Show updated status
            status = pool.get_pool_status()
            print(f"   Updated Available Connections: {status['available_connections']}")
            
            return pool
            
    except Exception as e:
        error_context = handle_error(e, "connection_pool_demo")
        print(f"❌ Connection pool demo failed: {error_context.message}")
        return None


def demonstrate_performance_monitoring(pool):
    """Demonstrate performance monitoring capabilities"""
    print("\n📊 PERFORMANCE MONITORING DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Run some benchmark queries
        queries = [
            "SELECT 1",
            "SELECT COUNT(*) FROM pg_tables",
            "SELECT NOW()",
            "SELECT version()"
        ]
        
        print("   Running benchmark queries...")
        benchmark_results = []
        
        for query in queries:
            print(f"   Running: {query}")
            result = run_benchmark_query(pool, query, iterations=10)
            benchmark_results.append(result)
            print(f"   ✅ Completed - Avg: {result['avg_duration_ms']:.1f}ms, "
                  f"Success Rate: {result['success_rate']:.1f}%")
        
        # Get performance metrics
        metrics = pool.get_performance_metrics()
        print(f"\n   📈 Overall Performance Metrics:")
        print(f"   Total Requests: {metrics['total_requests']}")
        print(f"   Success Rate: {metrics['overall_success_rate']:.1f}%")
        print(f"   Total Errors: {metrics['total_errors']}")
        
        # Recent performance
        recent = metrics['recent_5min']
        print(f"\n   📈 Recent 5min Performance:")
        print(f"   Requests: {recent['requests']}")
        print(f"   Success Rate: {recent['success_rate']:.1f}%")
        print(f"   Avg Duration: {recent['average_duration_ms']:.1f}ms")
        
        # Show top operations
        print(f"\n   🔝 Top Operations:")
        operations = metrics['operation_stats']
        for op_name, stats in sorted(operations.items(), 
                                   key=lambda x: x[1]['total_requests'], 
                                   reverse=True)[:3]:
            print(f"   - {op_name}: {stats['total_requests']} requests, "
                  f"{stats['average_duration_ms']:.1f}ms avg")
        
        return benchmark_results
        
    except Exception as e:
        error_context = handle_error(e, "performance_monitoring_demo")
        print(f"❌ Performance monitoring demo failed: {error_context.message}")
        return []


async def demonstrate_health_monitoring(pool):
    """Demonstrate health monitoring capabilities"""
    print("\n🏥 HEALTH MONITORING DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Run health checks
        print("   Running comprehensive health checks...")
        health_result = await pool.health_monitor.run_health_checks()
        
        # Show overall health
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.WARNING: "⚠️",
            HealthStatus.UNHEALTHY: "❌",
            HealthStatus.CRITICAL: "🚨"
        }
        
        emoji = status_emoji.get(health_result.overall_status, "❓")
        print(f"   {emoji} Overall System Health: {health_result.overall_status.value.upper()}")
        print(f"   Uptime: {health_result.uptime_seconds} seconds")
        print(f"   Total Checks: {len(health_result.checks)}")
        
        # Show individual checks
        print(f"\n   🔍 Individual Health Checks:")
        for check in health_result.checks:
            check_emoji = status_emoji.get(check.status, "❓")
            print(f"   {check_emoji} {check.component}: {check.message} "
                  f"({check.response_time_ms:.1f}ms)")
            
            if check.details:
                for key, value in check.details.items():
                    if key not in ['error', 'traceback']:  # Skip verbose error details
                        print(f"      - {key}: {value}")
        
        # Show health trends if available
        trends = pool.health_monitor.get_health_trends(hours=1)
        if trends.get('total_checks', 0) > 0:
            print(f"\n   📈 Health Trends (last 1 hour):")
            print(f"   Availability: {trends['availability_percent']:.1f}%")
            print(f"   Total Checks: {trends['total_checks']}")
            print(f"   Status Distribution: {trends['status_distribution']}")
        
        return health_result
        
    except Exception as e:
        error_context = handle_error(e, "health_monitoring_demo")
        print(f"❌ Health monitoring demo failed: {error_context.message}")
        return None


def demonstrate_error_handling():
    """Demonstrate structured error handling"""
    print("\n🛡️ ERROR HANDLING DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Simulate various error types
        print("   Testing error handling capabilities...")
        
        # Test configuration error
        try:
            from config import LakebaseSettings
            invalid_config = {"invalid": "config"}
            LakebaseSettings(**invalid_config)
        except Exception as e:
            error_context = handle_error(e, "config_validation")
            print(f"   ✅ Configuration Error Handled: {error_context.category.value}")
        
        # Test database connection error (simulate)
        try:
            import psycopg2
            psycopg2.connect("invalid://connection")
        except Exception as e:
            error_context = handle_error(e, "database_connection")
            print(f"   ✅ Database Error Handled: {error_context.category.value}")
            print(f"      Recoverable: {error_context.recoverable}")
            print(f"      Severity: {error_context.severity.value}")
        
        # Test custom Lakebase exception
        try:
            from error_handling import DatabaseTimeoutError
            raise DatabaseTimeoutError(
                "Simulated timeout error",
                details={"timeout_seconds": 30, "operation": "test"}
            )
        except LakebaseException as e:
            print(f"   ✅ Custom Error Handled: {e.context.category.value}")
            print(f"      Message: {e.context.message}")
            print(f"      Details: {e.context.details}")
        
        print("   ✅ Error handling system working correctly!")
        
    except Exception as e:
        print(f"❌ Error handling demo failed: {e}")


def show_summary(benchmark_results: List[Dict[str, Any]], health_result):
    """Show comprehensive summary"""
    print("\n🎯 SUMMARY")
    print("=" * 50)
    
    # Benchmark summary
    if benchmark_results:
        total_queries = sum(r['iterations'] for r in benchmark_results)
        total_errors = sum(r['errors'] for r in benchmark_results)
        avg_success_rate = sum(r['success_rate'] for r in benchmark_results) / len(benchmark_results)
        avg_duration = sum(r['avg_duration_ms'] for r in benchmark_results) / len(benchmark_results)
        
        print(f"📊 Benchmark Results:")
        print(f"   Total Queries: {total_queries}")
        print(f"   Total Errors: {total_errors}")
        print(f"   Average Success Rate: {avg_success_rate:.1f}%")
        print(f"   Average Duration: {avg_duration:.1f}ms")
    
    # Health summary
    if health_result:
        print(f"\n🏥 Health Status:")
        print(f"   Overall Status: {health_result.overall_status.value.upper()}")
        print(f"   System Uptime: {health_result.uptime_seconds} seconds")
        print(f"   Health Checks: {len(health_result.checks)} completed")
    
    print(f"\n✨ Enhanced Features Demonstrated:")
    print(f"   ✅ Environment-based configuration")
    print(f"   ✅ Structured error handling")
    print(f"   ✅ Performance monitoring")
    print(f"   ✅ Health monitoring")
    print(f"   ✅ Enhanced connection pool")
    print(f"   ✅ Real-time metrics collection")
    
    print(f"\n🚀 Next Steps:")
    print(f"   - Start FastAPI monitoring: python fastapi_monitoring.py")
    print(f"   - Access dashboard: http://localhost:8000/dashboard")
    print(f"   - Run full benchmark: python lakebase_1m_benchmark.py")
    print(f"   - Check enhanced README: README_ENHANCED.md")


async def main():
    """Main demonstration function"""
    print("🌊 ENHANCED LAKEBASE BENCHMARK DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases all FastAPI best practices integrated!")
    print()
    
    # Step 1: Configuration
    settings = demonstrate_configuration()
    if not settings:
        return
    
    # Step 2: Connection Pool
    pool = demonstrate_connection_pool(settings)
    if not pool:
        return
    
    try:
        # Step 3: Performance Monitoring
        benchmark_results = demonstrate_performance_monitoring(pool)
        
        # Step 4: Health Monitoring
        health_result = await demonstrate_health_monitoring(pool)
        
        # Step 5: Error Handling
        demonstrate_error_handling()
        
        # Step 6: Summary
        show_summary(benchmark_results, health_result)
        
    except Exception as e:
        error_context = handle_error(e, "main_demo")
        print(f"❌ Demo failed: {error_context.message}")
        logger.error(f"Demo error: {error_context.details}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the demonstration
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo failed")