Feature: Dhis2 reporter index page 

	Scenario: DHIS2 Reports Task Log Index Page Has Log Table and Pagination
		Given I have some submission tasks run
		And I am logged in 
		I see the navigation bar
		I must see all submission tasks on the index page

	Scenario: Index Page Log Table Content
		When I have a SUCCESS, RUNNING or FAILED tasks
		And I am logged in 
		I see the navigation bar
		Corresponding submission tasks details appears
     
  # Scenario: DHIS2 Reports Task Details Page
  #   Given I have some submission tasks run
  #   And I am logged in 
  #   And I select a  task
  #   And I have some submissions for that task
  #   And I open details page for the task
  #   Then the corresponding task details page appears 
  # 
  #   