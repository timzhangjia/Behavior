# language: en
Feature: UI Test Examples
  As a tester
  I want to test web interfaces
  So that I can verify UI functionality

  @ui @smoke
  Scenario: Visit example website
    Given I open the browser
    And I open page "example_page" with URL from config "ui_config.yaml" and value "ui_config.example_url"
    Then the page title should be "Example Domain"
    And element "heading" should be visible
    And element "heading" should contain text "Example"

  @ui @smoke
  Scenario: Visit example website with config
    Given I open the browser
    And I open page "example_page" with URL from config "ui_config.yaml" and value "ui_config.baidu_url"
    Then the page URL should contain "baidu.com"
