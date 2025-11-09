"""
Database Utility Module - Provides database reading and execution functionality
"""

import pymysql
import psycopg2
import sqlite3
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from ..utils.logger import Logger


class Database:
    """Database operation utility class"""
    
    def __init__(self, db_type: str = "mysql", **kwargs):
        """
        Initialize database connection
        
        Args:
            db_type: Database type (mysql, postgresql, sqlite)
            **kwargs: Database connection parameters
        """
        self.db_type = db_type.lower()
        self.logger = Logger()
        self.connection_params = kwargs
    
    @contextmanager
    def _get_connection(self):
        """Get database connection context manager"""
        conn = None
        try:
            if self.db_type == "mysql":
                conn = pymysql.connect(**self.connection_params)
            elif self.db_type == "postgresql":
                conn = psycopg2.connect(**self.connection_params)
            elif self.db_type == "sqlite":
                db_path = self.connection_params.get("database", ":memory:")
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row  # Enable access by column name
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database operation failed: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> List[Dict[str, Any]]:
        """
        Execute query SQL statement
        
        Args:
            sql: SQL query statement
            params: SQL parameters (for parameterized queries, prevents SQL injection)
            
        Returns:
            Query result list, each element is a dictionary of row data
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                
                # Get column names
                if self.db_type == "sqlite":
                    columns = [description[0] for description in cursor.description]
                else:
                    columns = [desc[0] for desc in cursor.description]
                
                # Get all results
                rows = cursor.fetchall()
                
                # Convert to dictionary list
                result = []
                for row in rows:
                    if self.db_type == "sqlite":
                        result.append(dict(row))
                    else:
                        result.append(dict(zip(columns, row)))
                
                cursor.close()
                self.logger.debug(f"Query executed successfully, returned {len(result)} records")
                return result
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def execute_update(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> int:
        """
        Execute update SQL statement (INSERT, UPDATE, DELETE)
        
        Args:
            sql: SQL update statement
            params: SQL parameters
            
        Returns:
            Number of affected rows
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                affected_rows = cursor.rowcount
                cursor.close()
                self.logger.debug(f"Update executed successfully, affected {affected_rows} rows")
                return affected_rows
        except Exception as e:
            self.logger.error(f"Update execution failed: {str(e)}")
            raise
    
    def execute_many(self, sql: str, params_list: List[Union[tuple, dict]]) -> int:
        """
        Batch execute SQL statements
        
        Args:
            sql: SQL statement
            params_list: Parameter list
            
        Returns:
            Number of affected rows
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, params_list)
                affected_rows = cursor.rowcount
                cursor.close()
                self.logger.debug(f"Batch execution successful, affected {affected_rows} rows")
                return affected_rows
        except Exception as e:
            self.logger.error(f"Batch execution failed: {str(e)}")
            raise
    
    def get_one(self, sql: str, params: Optional[Union[tuple, dict]] = None) -> Optional[Dict[str, Any]]:
        """
        Get single record
        
        Args:
            sql: SQL query statement
            params: SQL parameters
            
        Returns:
            Single record dictionary, returns None if no record
        """
        results = self.execute_query(sql, params)
        return results[0] if results else None
