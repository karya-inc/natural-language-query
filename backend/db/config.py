# config.py
import os

DATABASE_URI = os.environ['DATABASE_URI']

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries in console

    # Connection pool settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,  # Maximum number of database connections in the pool
        'pool_timeout': 30,  # Seconds to wait before timing out
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'max_overflow': 20,  # Allow up to 20 connections beyond pool_size
        'echo': False,  # Enable SQL query logging
        'pool_pre_ping': True,  # Enable connection health checks
    }

    # Query timeout settings
    SQLALCHEMY_QUERY_TIMEOUT = 60  # Global query timeout in seconds