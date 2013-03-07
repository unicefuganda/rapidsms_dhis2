Feature: Dhis2 reporter index page 

  Scenario: DHIS2 Reports Task Log Index Page
    Given I have some submission tasks run
    And I am logged in 
    I must see all submission tasks on the index page
    
  Scenario: DHIS2 Reports Task Details Page
    Given I have some submission tasks run
    And I am logged in 
    And I select a  task
    And I have some submissions for that task
    And I open details page for the task
    Then the corresponding task details page appears 

    