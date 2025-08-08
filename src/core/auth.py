#!/usr/bin/env python3
"""
Enhanced Lakebase Authentication using Databricks SDK

This module implements production-grade authentication using the official Databricks SDK
instead of manual OAuth token management. Based on best practices from the FastAPI app.

Features:
- Automatic token generation using Databricks SDK
- Background token refresh every 50 minutes
- Connection parameter caching
- Comprehensive error handling
- Production-grade logging

Usage:
    from lakebase_sdk_auth import LakebaseSDKAuthManager
    
    auth_manager = LakebaseSDKAuthManager()
    conn_params = auth_manager.get_connection_params()
    
    # Start background refresh for long-running applications
    await auth_manager.start_background_refresh()
"""

import asyncio
import logging
import os
import time
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.database import DatabaseInstance
import json

logger = logging.getLogger(__name__)


class LakebaseSDKAuthManager:
    """Enhanced authentication manager using Databricks SDK for token generation"""
    
    def __init__(self, config_file: str = None):
        """
        Initialize SDK-based authentication manager
        
        Args:
            config_file: Path to configuration file (kept for backward compatibility)
        """
        # Load configuration from secure environment variables
        self.config = self._load_config()
        
        # Authentication state
        self.workspace_client: Optional[WorkspaceClient] = None
        self.database_instance: Optional[DatabaseInstance] = None
        self.postgres_password: Optional[str] = None
        self.last_password_refresh: float = 0
        self.background_refresh_task: Optional[asyncio.Task] = None
        
        # Configuration cache
        self._connection_params_cache: Optional[Dict] = None
        self._cache_expiry: float = 0
        
        # Initialize SDK client
        self._initialize_sdk()
        
    def _load_config(self) -> Dict:
        """Load configuration from secure environment variables"""
        try:
            # Try relative import first, then absolute import
            try:
                from .secure_credentials import get_secure_credentials
            except ImportError:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                from src.core.secure_credentials import get_secure_credentials
            
            config = get_secure_credentials()
            logger.info("✅ Configuration loaded from secure environment variables")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config from environment: {e}")
            raise Exception(f"Configuration loading failed: {e}")
    
    def _initialize_sdk(self):
        """Initialize Databricks SDK WorkspaceClient"""
        try:
            databricks_config = self.config['databricks']
            
            # Initialize WorkspaceClient with explicit credentials
            if os.getenv("DATABRICKS_HOST"):
                # Use environment variables if available
                self.workspace_client = WorkspaceClient()
                logger.info("🔐 Using Databricks SDK with environment authentication")
            else:
                # Use configuration file credentials
                self.workspace_client = WorkspaceClient(
                    host=databricks_config['workspace_url'],
                    token=databricks_config['personal_access_token']
                )
                logger.info(f"🔐 Using Databricks SDK with PAT authentication: {databricks_config['workspace_url']}")
            
            # Get database instance
            lakebase_config = self.config['lakebase']
            logger.info(f"🔍 Getting database instance: {lakebase_config['name']}")
            self.database_instance = self.workspace_client.database.get_database_instance(
                name=lakebase_config['name']
            )
            logger.info(f"✅ Database instance found: {self.database_instance.name}")
            logger.info(f"🗄️ Connected to database instance: {self.database_instance.name}")
            
            # Generate initial credentials
            self._refresh_credentials()
            
        except Exception as e:
            logger.error(f"❌ SDK initialization failed: {e}")
            raise Exception(f"Databricks SDK initialization failed: {e}")
    
    def _refresh_credentials(self) -> str:
        """Generate fresh database credentials using SDK"""
        try:
            logger.info("🔄 Generating fresh database credentials...")
            
            # Generate database credential using SDK
            cred = self.workspace_client.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[self.database_instance.name]
            )
            
            self.postgres_password = cred.token
            self.last_password_refresh = time.time()
            
            # Clear cache to force regeneration
            self._connection_params_cache = None
            self._cache_expiry = 0
            
            logger.info(f"✅ Database credentials refreshed successfully. Token length: {len(self.postgres_password)}")
            logger.info(f"🔐 Token preview: {self.postgres_password[:50]}...")
            return self.postgres_password
            
        except Exception as e:
            logger.error(f"❌ Credential refresh failed: {e}")
            raise Exception(f"Database credential generation failed: {e}")
    
    def get_connection_params(self, quiet: bool = False) -> Dict[str, str]:
        """Get PostgreSQL connection parameters with caching"""
        current_time = time.time()
        
        # Check cache validity (5 minutes cache)
        if self._connection_params_cache and current_time < self._cache_expiry:
            if not quiet:
                logger.debug("📋 Using cached connection parameters")
            return self._connection_params_cache
        
        try:
            lakebase_config = self.config['lakebase']
            databricks_config = self.config['databricks']
            
            # Check if credentials need refresh (45 minutes)
            if current_time - self.last_password_refresh > 2700:  # 45 minutes
                if not quiet:
                    logger.info("⏰ Credentials approaching expiry, refreshing...")
                self._refresh_credentials()
            
            # Extract username from JWT token (more reliable than email parsing)
            import jwt
            try:
                decoded_token = jwt.decode(self.postgres_password, options={"verify_signature": False})
                logger.info(f"🔐 JWT token decoded: {decoded_token}")
                # Try using the full email address first
                username = decoded_token.get('sub', '')  # Use full email address
                logger.info(f"🔐 Using full email from JWT token: {username}")
            except Exception as e:
                # Fallback to email parsing
                username = databricks_config['username'].split('@')[0]
                logger.warning(f"⚠️  JWT decode failed, using email fallback: {e}")
            
            connection_params = {
                'host': lakebase_config['host'],
                'port': lakebase_config['port'],
                'database': lakebase_config['database'],
                'user': username,
                'password': self.postgres_password,
                'sslmode': 'require'
            }
            
            logger.info(f"🔐 Connection parameters: host={connection_params['host']}, port={connection_params['port']}, database={connection_params['database']}, user={connection_params['user']}")
            
            # Cache parameters for 5 minutes
            self._connection_params_cache = connection_params
            self._cache_expiry = current_time + 300  # 5 minutes
            
            if not quiet:
                expiry_time = datetime.fromtimestamp(self.last_password_refresh + 3600)
                time_until_expiry = expiry_time - datetime.now()
                logger.info(f"✅ Connection parameters ready (expires in {time_until_expiry})")
            
            return connection_params
            
        except Exception as e:
            logger.error(f"❌ Failed to get connection parameters: {e}")
            raise Exception(f"Connection parameter generation failed: {e}")
    
    def get_connection(self):
        """Get a new database connection using psycopg2"""
        import psycopg2
        return psycopg2.connect(**self.get_connection_params(quiet=True))
    
    async def refresh_token_background(self):
        """Background task to refresh tokens every 50 minutes"""
        logger.info("🔄 Starting background token refresh task (50-minute interval)")
        
        while True:
            try:
                # Wait 50 minutes (3000 seconds)
                await asyncio.sleep(50 * 60)
                
                logger.info("🔄 Background token refresh: Generating fresh database credentials")
                self._refresh_credentials()
                logger.info("✅ Background token refresh: Credentials updated successfully")
                
            except asyncio.CancelledError:
                logger.info("🛑 Background token refresh task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Background token refresh failed: {e}")
                # Continue running even if one refresh fails
    
    async def start_background_refresh(self):
        """Start the background token refresh task"""
        if self.background_refresh_task is None or self.background_refresh_task.done():
            self.background_refresh_task = asyncio.create_task(self.refresh_token_background())
            logger.info("🚀 Background token refresh task started")
    
    async def stop_background_refresh(self):
        """Stop the background token refresh task"""
        if self.background_refresh_task and not self.background_refresh_task.done():
            self.background_refresh_task.cancel()
            try:
                await self.background_refresh_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Background token refresh task stopped")
    
    def test_connection(self) -> bool:
        """Test database connection with current credentials"""
        try:
            import psycopg2
            
            logger.info("🔍 Testing database connection...")
            conn_params = self.get_connection_params(quiet=False)
            
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Connection test successful: {version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get authentication manager statistics"""
        return {
            'last_refresh': datetime.fromtimestamp(self.last_password_refresh) if self.last_password_refresh else None,
            'next_refresh': datetime.fromtimestamp(self.last_password_refresh + 3000) if self.last_password_refresh else None,
            'cache_valid': time.time() < self._cache_expiry if self._cache_expiry else False,
            'background_task_running': self.background_refresh_task and not self.background_refresh_task.done(),
            'database_instance': self.database_instance.name if self.database_instance else None
        }


if __name__ == "__main__":
    # Test the SDK authentication
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    auth = LakebaseSDKAuthManager()
    
    # Test connection
    success = auth.test_connection()
    
    # Show stats
    stats = auth.get_stats()
    print("\n📊 Authentication Manager Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    if success:
        print("\n✅ SDK-based authentication working correctly!")
    else:
        print("\n❌ SDK authentication test failed!")