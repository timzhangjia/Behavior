from pytest_bdd import given, when, then, parsers
from src.utils.db_manager import DB


@when(parsers.cfparse('I connect to database "{db_path}"'))
def connect_db(request, db_path, config):
    """Connect to database using path format like 'sqlserver.database1'."""
    try:
        db_config_data = config.get(db_path, {})
        
        print(f"\nDatabase Path: {db_path}")
        print(f"Database Configuration: {db_config_data}")
        
        # get 'sqlserver' from db_path
        engine = db_path.split('.')[0].lower()
        
        db = DB(engine=engine, **db_config_data)
        request.config.cache.set("db_instance", db)
        
        request.addfinalizer(lambda: db.close())
        return db
    except Exception as e:
        raise RuntimeError(f"Failed to connect to {db_path}: {str(e)}")


@when('I execute SQL query "<sql_query>"')
def execute_sql_query(sql_query, request):
    """Execute SQL query without parameters."""
    execute_query(request, sql_query, "")
    
    # Also store results in request.cls for backward compatibility
    if hasattr(request, 'cls'):
        result = request.config.cache.get("query_result", [])
        request.cls.query_results = result
        # Extract column names from first row if available
        if result:
            request.cls.result_columns = list(result[0].keys()) if isinstance(result[0], dict) else []


@when(parsers.cfparse('I execute query "{sql}" with params "{params}"'))
def execute_query(request, sql, params):
    """Execute SQL query with parameters."""
    db = request.config.cache.get("db_instance", None)
    assert db, "Database connection not initialized"
    
    # Parse parameters
    params_list = []
    if params and params.strip().lower() != 'none':
        params_list = [p.strip() for p in params.split(",")]
    
    try:
        # Execute query and get cursor
        cursor = db._execute(sql, params_list)
        
        # Get column names from cursor description
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Convert results to list of dictionaries
        result = []
        for row in cursor.fetchall():
            result.append(dict(zip(columns, row)))
        
        # Store results in cache
        request.config.cache.set("query_result", result)
    except Exception as e:
        raise RuntimeError(f"Failed to execute query: {str(e)}")


@when(parsers.cfparse('I execute update "{sql}" with params "{params}"'))
def execute_update(request, sql, params):
    """Execute SQL update statement with parameters."""
    db = request.config.cache.get("db_instance", None)
    assert db, "Database connection not initialized"
    
    # Parse parameters
    params_list = []
    if params and params.strip().lower() != 'none':
        params_list = [p.strip() for p in params.split(",")]
    
    try:
        # Execute update and get affected rows count
        cursor = db._execute(sql, params_list)
        affected_rows = cursor.rowcount
        
        # Store affected rows count in cache
        request.config.cache.set("affected_rows", affected_rows)
    except Exception as e:
        raise RuntimeError(f"Failed to execute update: {str(e)}")


@then('I should get results with "<count>" rows')
def verify_result_count(count, request):
    """Verify that the query returned the expected number of rows."""
    # Try to get from cache first, then fall back to request.cls for backward compatibility
    result = request.config.cache.get("query_result", [])
    if not result and hasattr(request, 'cls') and hasattr(request.cls, 'query_results'):
        result = request.cls.query_results
    
    assert len(result) == int(count), f"Expected {count} rows, got {len(result)}"


@then('the results should contain column "<column_name>"')
def verify_result_column(column_name, request):
    """Verify that the query results contain the specified column."""
    # Try to get columns from cache first, then fall back to request.cls
    columns = []
    result = request.config.cache.get("query_result", [])
    if result:
        columns = list(result[0].keys()) if isinstance(result[0], dict) else []
    elif hasattr(request, 'cls') and hasattr(request.cls, 'result_columns'):
        columns = request.cls.result_columns
    
    assert column_name in columns, f"Column '{column_name}' not found in result set"


@then(parsers.cfparse('the result field "{field}" should be "{expected_value}"'))
def verify_field_value(request, field, expected_value):
    """Verify that a specific field in the query result equals the expected value."""
    result = request.config.cache.get("query_result", [])
    assert result, "No query results found"
    
    # Get the first row of results
    first_row = result[0]
    assert field in first_row, f"Field '{field}' not found in query results"
    
    # Get actual value and convert to string for comparison
    actual_value = str(first_row[field])
    assert actual_value == expected_value, \
        f"Expected field '{field}' to be '{expected_value}', but got '{actual_value}'"