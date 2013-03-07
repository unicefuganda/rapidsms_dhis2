Feature: Fred API 

  Scenario: Index
    Given I have some submission tasks run
    And I am logged in 
    I must see all submission tasks on the index page
    Delete the test task logs created
    