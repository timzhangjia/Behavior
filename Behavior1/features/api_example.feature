# language: en
Feature: API Test Examples
  As a tester
  I want to test API interfaces
  So that I can verify API functionality

  @api @smoke
  Scenario: Get single post information
    Given I initialize API client with config file "api_config.yaml" and value "api_config.base_url"
    When I send "GET" request to "posts/1"
    Then the response status code should be "200"
    And the response JSON value for "id" should be "1"
    And the response JSON value for "userId" should be "1"

  @api @smoke
  Scenario: Create new post with JSON file
    Given I initialize API client with config file "api_config.yaml" and value "api_config.base_url"
    When I send "POST" request to "posts" with JSON file "create_post.json"
    Then the response status code should be successful
    And the response JSON value for "title" should be "Test Post"

  @api
  Scenario: Update post information with JSON file
    Given I initialize API client with config file "api_config.yaml" and value "api_config.base_url"
    When I send "PUT" request to "posts/1" with JSON file "update_post.json"
    Then the response status code should be "200"
    And the response JSON value for "title" should be "Updated Post"

  @api
  Scenario: Delete post
    Given I initialize API client with config file "api_config.yaml" and value "api_config.base_url"
    When I send "DELETE" request to "posts/1"
    Then the response status code should be "200"

  @api @database
  Scenario: Create post and verify in database
    Given I initialize API client with config file "api_config.yaml" and value "api_config.base_url"
    And I connect to configured database
    When I send "POST" request to "posts" with JSON file "create_post.json"
    Then the response status code should be successful
    And I save the response JSON value for "id" as "post_id"
    When I execute SQL query "SELECT * FROM posts WHERE id = {post_id}"
    Then the query result should contain "1" rows
    And the query result row "0" column "title" should be "Test Post"
