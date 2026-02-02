import sys
import os
import models

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.database import engine, Base
from loguru import logger


def reset_database():
    """Полностью очищает и пересоздает БД"""
    try:
        logger.info("Dropping all tables...")
        models.Base.metadata.drop_all(bind=engine)

        logger.info("Creating all tables...")
        models.Base.metadata.create_all(bind=engine)

        logger.success("Database reset successfully!")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise


if __name__ == "__main__":
    reset_database()