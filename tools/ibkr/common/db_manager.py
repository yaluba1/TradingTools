"""
Database management utility for IBKR Trading Tools using SQLAlchemy.
This module provides a singleton DatabaseManager to handle connections to
the MariaDB/MySQL database used for logging and state management.
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from .config import get_db_config

class DatabaseManager:
    """
    Manages database connections and provides sessions for MariaDB.
    This class initializes the SQLAlchemy engine and session factory based on
    the configuration provided in the secrets directory.
    """
    def __init__(self):
        """
        Initialize the DatabaseManager by loading configuration and creating
         the SQLAlchemy engine.
        """
        config = get_db_config()["database"]
        user = config["user"]
        password = config["password"]
        host = config["host"]
        port = config["port"]
        db_name = config["name"]
        
        # Build the connection URL for MariaDB using the pymysql driver.
        # Example: mysql+pymysql://user:password@localhost:3306/ibkr_db
        self.url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        
        # Create the engine with pool_pre_ping=True to handle stale connections.
        self.engine = create_engine(self.url, pool_pre_ping=True)
        
        # Create a configured "Session" class
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Metadata object for table reflections if needed
        self.metadata = MetaData()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Ensures that the session is properly closed and that changes are 
        committed if no exceptions occur, or rolled back otherwise.

        Yields:
            Session: A SQLAlchemy ORM session object.

        Raises:
            Exception: Re-raises any exception that occurs during the session.
        """
        session = self.SessionLocal()
        try:
            yield session
            # If no exception, commit the transaction
            session.commit()
        except Exception:
            # If an exception occurs, roll back any changes
            session.rollback()
            raise
        finally:
            # Always close the session to return the connection to the pool
            session.close()

# Singleton instance to be used across the tool family
db_manager = DatabaseManager()
