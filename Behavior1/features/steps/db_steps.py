"""
Database Test Steps - Defines BDD steps for database verification
"""

import os
from behave import given, when, then, step
from behavior_framework.utils.database import Database
from behavior_framework.utils.logger import Logger
from behavior_framework.config.settings import Settings

logger = Logger()


@given('I connect to database "{db_type}"')
def step_connect_database(context, db_type):
    """Connect to database"""
    settings = context.settings
    
    # Get database connection parameters from environment variables
    if db_type.lower() == "mysql":
        db = Database(
            db_type="mysql",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "testdb")
        )
    elif db_type.lower() == "postgresql":
        db = Database(
            db_type="postgresql",
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "testdb")
        )
    elif db_type.lower() == "sqlite":
        db = Database(
            db_type="sqlite",
            database=os.getenv("DB_NAME", ":memory:")
        )
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    context.database = db
    logger.info(f"Connected to database: {db_type}")


@given('I connect to configured database')
def step_connect_configured_database(context):
    """Connect to database using configuration"""
    db_type = os.getenv("DB_TYPE", "mysql").lower()
    step_connect_database(context, db_type)


@when('I execute SQL query "{sql_query}"')
def step_execute_sql(context, sql_query):
    """Execute SQL query"""
    if not hasattr(context, 'database'):
        raise RuntimeError("Database not connected. Please connect to database first.")
    
    # Replace variables in SQL query
    original_query = sql_query
    if hasattr(context, 'variables'):
        for var_name, var_value in context.variables.items():
            sql_query = sql_query.replace(f"{{{var_name}}}", str(var_value))
    
    try:
        result = context.database.execute_query(sql_query)
        context.query_result = result
        
        # Save evidence
        if hasattr(context, 'evidence_manager'):
            context.evidence_manager.add_database_query(
                query=sql_query,
                result=result,
                error=None
            )
        
        logger.info(f"Executed SQL query: {sql_query}")
    except Exception as e:
        error_msg = str(e)
        # Save evidence with error
        if hasattr(context, 'evidence_manager'):
            context.evidence_manager.add_database_query(
                query=sql_query,
                result=None,
                error=error_msg
            )
        raise


@when('I execute SQL update "{sql_query}"')
def step_execute_sql_update(context, sql_query):
    """Execute SQL update statement"""
    if not hasattr(context, 'database'):
        raise RuntimeError("Database not connected. Please connect to database first.")
    
    try:
        affected_rows = context.database.execute_update(sql_query)
        context.affected_rows = affected_rows
        
        # Save evidence
        if hasattr(context, 'evidence_manager'):
            context.evidence_manager.add_database_query(
                query=sql_query,
                result=[{"affected_rows": affected_rows}],
                error=None
            )
        
        logger.info(f"Executed SQL update: {sql_query}, affected rows: {affected_rows}")
    except Exception as e:
        error_msg = str(e)
        # Save evidence with error
        if hasattr(context, 'evidence_manager'):
            context.evidence_manager.add_database_query(
                query=sql_query,
                result=None,
                error=error_msg
            )
        raise


@then('the query result should contain "{expected_count}" rows')
def step_assert_query_result_count(context, expected_count):
    """Assert query result row count"""
    if not hasattr(context, 'query_result'):
        raise AssertionError("No query result available")
    
    actual_count = len(context.query_result)
    expected_count = int(expected_count)
    assert actual_count == expected_count, f"Expected {expected_count} rows, but got {actual_count} rows"
    logger.info(f"Query result count assertion passed: {actual_count} rows")


@then('the query result row "{row_index}" column "{column_name}" should be "{expected_value}"')
def step_assert_query_result_value(context, row_index, column_name, expected_value):
    """Assert query result value"""
    if not hasattr(context, 'query_result'):
        raise AssertionError("No query result available")
    
    row_index = int(row_index)
    if row_index >= len(context.query_result):
        raise AssertionError(f"Row index {row_index} out of range. Query result has {len(context.query_result)} rows")
    
    row = context.query_result[row_index]
    actual_value = row.get(column_name) if isinstance(row, dict) else row[column_name] if hasattr(row, '__getitem__') else None
    
    # Try to convert expected value to appropriate type
    try:
        if expected_value.isdigit():
            expected_value = int(expected_value)
        elif expected_value.lower() in ('true', 'false'):
            expected_value = expected_value.lower() == 'true'
        elif '.' in expected_value and expected_value.replace('.', '').isdigit():
            expected_value = float(expected_value)
    except:
        pass
    
    assert actual_value == expected_value, f"Expected {column_name} to be '{expected_value}', but got '{actual_value}'"
    logger.info(f"Query result value assertion passed: row {row_index}, column {column_name} = {expected_value}")


@then('the affected rows should be "{expected_count}"')
def step_assert_affected_rows(context, expected_count):
    """Assert affected rows count"""
    if not hasattr(context, 'affected_rows'):
        raise AssertionError("No update result available")
    
    actual_count = context.affected_rows
    expected_count = int(expected_count)
    assert actual_count == expected_count, f"Expected {expected_count} affected rows, but got {actual_count}"
    logger.info(f"Affected rows assertion passed: {actual_count} rows")

