#!/usr/bin/env python3
"""
Secure Environment Setup Script
Helps users set up environment variables for secure credential management
"""

import os
import sys
from pathlib import Path

def create_env_template():
    """Create a .env.template file with required environment variables"""
    template_content = """# Lakebase Secure Environment Configuration
# Copy this file to .env and fill in your actual values
# DO NOT commit .env to version control

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
"""
    
    template_path = Path(".env.template")
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Created {template_path}")
    print("📝 Next steps:")
    print("   1. Copy .env.template to .env")
    print("   2. Fill in your actual credentials in .env")
    print("   3. Never commit .env to version control")

def validate_env_file():
    """Validate that .env file exists and has required variables"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("📝 Run: cp .env.template .env")
        return False
    
    # Load the .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "DATABRICKS_HOST",
        "LAKEFUSION_DATABRICKS_DAPI",
        "DATABRICKS_DATABASE_INSTANCE",
        "DATABRICKS_DATABASE_HOST"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ .env file is properly configured")
    return True

def main():
    """Main setup function"""
    print("🔐 Lakebase Secure Environment Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "template":
        create_env_template()
    elif len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_env_file()
    else:
        print("Usage:")
        print("  python setup_secure_env.py template  # Create .env.template")
        print("  python setup_secure_env.py validate  # Validate .env file")
        print()
        print("Security Notes:")
        print("  ✅ Use environment variables instead of JSON files")
        print("  ✅ Never commit .env to version control")
        print("  ✅ Use secure credential storage in production")
        print("  ✅ Rotate tokens regularly")

if __name__ == "__main__":
    main()
