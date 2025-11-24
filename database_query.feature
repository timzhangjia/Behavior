Feature: Database Query from Configuration

  Scenario: Execute SQL query using database configuration from settings
    When I connect to database "sqlserver.database1"
    When I execute SQL query "SELECT * FROM users LIMIT 10"
    Then the result field "id" should be "1"