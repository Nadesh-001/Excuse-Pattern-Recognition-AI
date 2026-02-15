"""
PostgreSQL/Supabase Connection Manager
Provides connection pooling and database access for the application.
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
import sys
import platform
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Global connection pool
_connection_pool = None


class DatabaseConnection:
    """
    Database connection manager using PostgreSQL connection pooling.
    Provides context manager support for automatic connection handling.
    """
    
    @staticmethod
    def initialize_pool(min_conn=1, max_conn=5):
        """
        Initialize the connection pool.
        Should be called once at application startup.
        
        Args:
            min_conn: Minimum number of connections to maintain
            max_conn: Maximum number of connections allowed
        """
        global _connection_pool
        
        try:
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=min_conn,
                maxconn=max_conn,
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                sslmode='require',  # Supabase requires SSL
                connect_timeout=10,
                options='-c statement_timeout=30000'  # 30 second query timeout
            )
            print("✅ Database connection pool initialized successfully")
            print(f"   Pool size: {min_conn}-{max_conn} connections")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize database pool: {e}")
            raise
    
    @staticmethod
    def get_pool():
        """Get the connection pool instance"""
        return _connection_pool
    
    @staticmethod
    def close_pool():
        """Close all connections in the pool"""
        global _connection_pool
        if _connection_pool:
            _connection_pool.closeall()
            print("✅ Database connection pool closed")


def get_conn():
    """
    Get a database connection from the pool.
    Validates connection before returning.
    
    Returns:
        psycopg2.connection: Database connection with RealDictCursor
        
    Raises:
        Exception: If pool is not initialized or no connections available
    """
    if _connection_pool is None:
        raise Exception("Database pool not initialized. Call DatabaseConnection.initialize_pool() first.")
    
    try:
        conn = _connection_pool.getconn()
        if conn:
            # Check if connection is closed (local check)
            if conn.closed:
                print("⚠️  Got locally closed connection, discarding...")
                _connection_pool.putconn(conn, close=True)
                return get_conn()

            # Active Liveness Check (server check)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                print(f"⚠️  Connection dead ({e}), discarding and retrying...")
                _connection_pool.putconn(conn, close=True)
                return get_conn()
            except Exception as e:
                print(f"⚠️  Unexpected error during liveness check: {e}")
                # Don't recurse infinitely on unknown errors, but try one more time?
                # Safer to raise or maybe just try to refresh
                _connection_pool.putconn(conn, close=True)
                raise Exception("Refused to return potentially unsafe connection")

            # Set cursor factory for dict-like results
            conn.cursor_factory = RealDictCursor
            return conn
        raise Exception("Failed to get connection from pool")
    except Exception as e:
        # Avoid recursion depth errors
        if "Refused to return" not in str(e):
             print(f"❌ Error getting database connection: {e}")
        raise


def release_conn(conn, close=False):
    """
    Return a connection back to the pool.
    
    Args:
        conn: Database connection to release
        close: If True, close the connection (remove from pool)
    """
    if _connection_pool and conn:
        try:
            _connection_pool.putconn(conn, close=close)
        except Exception as e:
            print(f"⚠️  Error releasing connection: {e}")


@contextmanager
def get_db_connection():
    """
    Context manager for automatic connection handling.
    """
    conn = get_conn()
    close_conn = False
    try:
        yield conn
    except psycopg2.InterfaceError:
        # Connection failed usually due to being closed
        close_conn = True
        raise
    except Exception:
        raise
    finally:
        release_conn(conn, close=close_conn)


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor):
    """
    Context manager for automatic cursor and connection handling.
    Returns dictionary-based results by default.
    """
    conn = get_conn()
    cursor = None
    close_conn = False
    try:
        cursor = conn.cursor(cursor_factory=cursor_factory)
        yield cursor
        conn.commit()
    except Exception as e:
        # Safely rollback
        try:
            if not conn.closed:
                conn.rollback()
        except Exception as rollback_err:
             print(f"⚠️  Rollback failed: {rollback_err}")
        
        # Check if it was a connection error
        if isinstance(e, (psycopg2.InterfaceError, psycopg2.OperationalError)):
            close_conn = True
            
        raise
    finally:
        if cursor:
            try:
                 cursor.close()
            except Exception:
                 pass
        
        # If connection is closed by server, make sure we drop it from pool
        if conn.closed:
            close_conn = True
            
        release_conn(conn, close=close_conn)


def execute_query(query, params=None, fetch=True, cursor_factory=RealDictCursor):
    """
    Execute a query with automatic connection management.
    
    Args:
        query: SQL query string (use %s for parameters)
        params: Query parameters (tuple or dict)
        fetch: If True, returns results. If False, returns affected row count.
        cursor_factory: Cursor type (RealDictCursor for dicts, None for tuples)
    
    Returns:
        List of results if fetch=True, row count if fetch=False
        
    Example:
        # Fetch data
        users = execute_query("SELECT * FROM users WHERE role = %s", ('admin',))
        
        # Insert data
        rows = execute_query(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ('John', 'john@example.com', 'hashed_password', 'employee'),
            fetch=False
        )
    """
    with get_db_cursor(cursor_factory=cursor_factory) as cursor:
        cursor.execute(query, params or ())
        
        if fetch:
            return cursor.fetchall()
        else:
            return cursor.rowcount


def execute_many(query, params_list):
    """
    Execute the same query with multiple parameter sets (bulk insert).
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
        
    Returns:
        Number of rows affected
        
    Example:
        execute_many(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            [
                ('John', 'john@example.com', 'hash1', 'employee'),
                ('Jane', 'jane@example.com', 'hash2', 'manager'),
                ('Bob', 'bob@example.com', 'hash3', 'admin')
            ]
        )
    """
    with get_db_cursor() as cursor:
        cursor.executemany(query, params_list)
        return cursor.rowcount


def test_connection():
    """
    Test database connection and display system info.
    Used for diagnostics and health checks.
    
    Returns:
        dict: Connection test results
    """
    try:
        with get_db_cursor() as cursor:
            # Test query
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            # Get PostgreSQL version
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            
            # Get current database
            cursor.execute("SELECT current_database()")
            db_name = cursor.fetchone()
            
            # Get connection count
            cursor.execute("""
                SELECT count(*) as connections 
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            connections = cursor.fetchone()
            
            # Get table count
            cursor.execute("""
                SELECT count(*) as table_count
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            table_count = cursor.fetchone()
            
            return {
                'database': {
                    'status': True,
                    'message': f"PostgreSQL is connected and healthy. Cluster: {db_name['current_database']}",
                    'version': version['version'],
                    'active_connections': connections['connections'],
                    'tables': table_count['table_count']
                },
                'system': {
                    'Python Version': sys.version,
                    'OS': f"{platform.system()} {platform.release()}"
                }
            }
    except Exception as e:
        return {
            'database': {
                'status': False,
                'message': f"Connection Error: {str(e)}"
            },
            'system': {
                'Python Version': sys.version,
                'OS': f"{platform.system()} {platform.release()}"
            }
        }


# Alias for backward compatibility with simple connection module
DatabaseConnection.test_connection = test_connection
