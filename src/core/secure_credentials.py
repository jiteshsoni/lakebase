#!/usr/bin/env python3
"""
Secure Credential Management for Lakebase
Uses environment variables and secure methods instead of plain JSON files
"""

import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_secure_credentials() -> Dict:
    """
    Get credentials securely from environment variables or secure storage
    Prefers environment variables over any file-based storage
    """
    try:
        # Load from .env file if it exists (for development)
        load_dotenv()
        
        # Get credentials from environment variables (preferred method)
        config = {
            "databricks": {
                "workspace_url": os.getenv("DATABRICKS_HOST"),
                "personal_access_token": os.getenv("LAKEFUSION_DATABRICKS_DAPI"),
                "workspace_id": os.getenv("DATABRICKS_WORKSPACE_ID"),
                "username": "jitesh.soni@databricks.com"  # Use the email from your credentials
            },
            "lakebase": {
                "name": os.getenv("DATABRICKS_DATABASE_INSTANCE"),
                "host": os.getenv("DATABRICKS_DATABASE_HOST"),
                "port": int(os.getenv("DATABRICKS_DATABASE_PORT", "5432")),
                "database": os.getenv("DATABRICKS_DATABASE_NAME", "databricks_postgres")
            },
            "production_pool": {
                "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
                "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
                "pool_recycle_interval": int(os.getenv("DB_POOL_RECYCLE", "3000"))
            },
            "benchmark": {
                "thread_counts": [16],  # Only test 16 threads
                "test_duration_seconds": 60,
                "table_rows": 1000000,  # 1 million rows
                "batch_size": 10000,
                "connection_stagger_delay": 0.1,
                "max_pool_init_time": 30
            }
        }
        
        # Validate required credentials
        required_vars = [
            "DATABRICKS_HOST",
            "LAKEFUSION_DATABRICKS_DAPI", 
            "DATABRICKS_DATABASE_INSTANCE"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        logger.info("Secure credentials loaded from environment variables")
        return config
        
    except Exception as e:
        logger.error(f"Failed to load secure credentials: {e}")
        raise

def setup_secure_environment():
    """Configure environment variables securely"""
    try:
        # Get secure credentials
        config = get_secure_credentials()
        
        # Set only required variables, don't clear everything
        env_vars = {
            'DB_TYPE': 'lakebase',
            'DATABRICKS_HOST': config['databricks']['workspace_url'],
            'LAKEFUSION_DATABRICKS_DAPI': config['databricks']['personal_access_token'],
            'DATABRICKS_DATABASE_INSTANCE': config['lakebase']['name'],
            'DATABRICKS_DATABASE_NAME': config['lakebase']['database'],
            'DATABRICKS_DATABASE_PORT': str(config['lakebase']['port']),
            'DATABRICKS_DATABASE_HOST': config['lakebase']['host'],
            'SERVICE_NAME': 'LakeFusionDBService',
            'DB_POOL_SIZE': str(config['production_pool']['pool_size']),
            'DB_MAX_OVERFLOW': str(config['production_pool']['max_overflow']),
            'DB_POOL_TIMEOUT': str(config['production_pool']['pool_timeout']),
            'DB_POOL_RECYCLE': str(config['production_pool']['pool_recycle_interval'])
        }
        
        os.environ.update(env_vars)
        
        # Log non-sensitive info only
        logger.info("Database environment configured securely")
        logger.info(f"Database: {config['lakebase']['name']}")
        logger.info(f"Host: {config['lakebase']['host']}")
        logger.info(f"Pool size: {config['production_pool']['pool_size']}")
        
    except Exception as e:
        logger.error(f"Failed to configure environment: {e}")
        raise

def validate_secure_credentials() -> bool:
    """Validate that all required credentials are available"""
    try:
        config = get_secure_credentials()
        
        # Check that all required fields are present
        required_fields = [
            ('databricks', 'workspace_url'),
            ('databricks', 'personal_access_token'),
            ('lakebase', 'name'),
            ('lakebase', 'host')
        ]
        
        for section, field in required_fields:
            if not config.get(section, {}).get(field):
                logger.error(f"Missing required credential: {section}.{field}")
                return False
        
        logger.info("All required credentials are available")
        return True
        
    except Exception as e:
        logger.error(f"Credential validation failed: {e}")
        return False

def get_credential_info() -> Dict[str, str]:
    """Get non-sensitive credential information for logging"""
    try:
        config = get_secure_credentials()
        return {
            "database_name": config['lakebase']['name'],
            "database_host": config['lakebase']['host'],
            "database_port": str(config['lakebase']['port']),
            "workspace_url": config['databricks']['workspace_url'],
            "pool_size": str(config['production_pool']['pool_size'])
        }
    except Exception as e:
        logger.error(f"Failed to get credential info: {e}")
        return {}
