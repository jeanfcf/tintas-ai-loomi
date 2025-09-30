"""Initialize database and admin user for RBAC system."""
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.infrastructure.database import SessionLocal, check_database_connection
from app.core.container import container
from app.domain.entities import UserCreate, UserRole
from app.core.logging import get_logger

logger = get_logger(__name__)


def check_migration_status():
    """Check current migration status and available migrations."""
    try:
        current_result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        current_migration = current_result.stdout.strip()
        heads_result = subprocess.run(
            ["alembic", "heads"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if heads_result.returncode == 0:
            latest_migration = heads_result.stdout.strip()
            
            if current_migration and current_migration != latest_migration:
                logger.warning("Pending migrations detected")
                return True, current_migration, latest_migration
            elif not current_migration:
                logger.warning("No migrations applied")
                return True, None, latest_migration
            else:
                return False, current_migration, latest_migration
        else:
            logger.error("Could not check migration heads")
            return True, current_migration, None
            
    except Exception as e:
        error_msg = f"Error checking migration status: {e}"
        logger.error(error_msg)
        return True, None, None


def run_migrations():
    """Run database migrations with intelligent status checking."""
    try:
        has_pending, current, latest = check_migration_status()
        
        if not has_pending:
            return True
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode != 0:
            error_msg = f"Migration failed with return code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"
            if result.stdout:
                error_msg += f"\nOutput: {result.stdout}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info("Migrations applied successfully")
        return True
        
    except FileNotFoundError:
        error_msg = "Alembic not found. Please ensure it's installed: pip install alembic"
        logger.error(error_msg)
        return False
    except subprocess.SubprocessError as e:
        error_msg = f"Subprocess error during migration: {e}"
        logger.error(error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error running migrations: {e}"
        logger.error(error_msg)
        return False


def create_admin_user():
    """Create default admin user if it doesn't exist."""
    db = None
    try:
        db = SessionLocal()
        user_service = container.get_user_service()
        
        existing_admin = user_service.get_user_by_username(db, "admin")
        if existing_admin:
            return True
        admin_data = UserCreate(
            email="admin@tintas-ai-loomi.com",
            username="admin",
            password="Admin@2024!",
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        user_service.create_user(db, admin_data)
        logger.info("Admin user created")
        return True
        
    except ValueError as e:
        error_msg = f"Validation error creating admin user: {e}"
        logger.error(error_msg)
        return False
    except Exception as e:
        error_msg = f"Unexpected error creating admin user: {e}"
        logger.error(error_msg)
        return False
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.warning(f"Error closing database session: {e}")


def initialize_system():
    """Initialize the entire system (migrations + admin user)."""
    try:
        from app.core.settings import settings
        
        logger.info("=== DATABASE CONFIGURATION ===")
        logger.info(f"DATABASE_URL: {settings.database.url}")
        logger.info(f"DATABASE_HOST: {settings.database.db_host}")
        logger.info(f"DATABASE_PORT: {settings.database.db_port}")
        logger.info(f"DATABASE_NAME: {settings.database.db_name}")
        logger.info(f"DATABASE_USER: {settings.database.db_user}")
        logger.info(f"Environment: {settings.app.environment}")
        logger.info("===============================")
        if not check_database_connection():
            error_msg = "Database connection failed. Please start the database first:\nRun: docker compose up -d postgres"
            logger.error(error_msg)
            return False
        
        if not run_migrations():
            error_msg = "Failed to run migrations. Check logs for details."
            logger.error(error_msg)
            return False
        if not create_admin_user():
            error_msg = "Failed to create admin user. Check logs for details."
            logger.error(error_msg)
            return False
        
        logger.info("System initialized")
        return True
        
    except Exception as e:
        error_msg = f"Critical error during system initialization: {e}"
        logger.error(error_msg)
        return False


if __name__ == "__main__":
    if initialize_system():
        logger.info("System ready")
        sys.exit(0)
    else:
        logger.error("System initialization failed")
        sys.exit(1)
